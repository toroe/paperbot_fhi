from io import StringIO
import logging
from fastapi import FastAPI, Request, status, Form
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel
import random
import json, csv, pandas
from chatbotmodule import ChatBot
from graphdriver import *
from apiparsermodule import ApiParserModule
import os
from datetime import date
import random

app = FastAPI()
logging.basicConfig(
    filename="logs/api.log",
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
db_driver = GraphDBDriver("bolt://localhost:7687", os.environ["NEO4J_USER"],os.environ["NEO4J_PASSWORD"])
api_parser = ApiParserModule()
#chatbot = ChatBot(token= os.environ["CHATBOT_TOKEN"], primary_channel_id="138hexmf4tfrdmsz6o9pzieftc")

app.add_middleware(
    CORSMiddleware,
    allow_credentials = True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)



class Article(BaseModel):
    title: str
    abstract: str
    authors: List[str]
    doi: str
    journal: str
    keywords: List[str]
    publication_year: int
    generation: int
class CitationMapping(BaseModel):
    articles: List[Article]
    referencer_doi: str
    citation_direction: bool  
class MatterMostRequest(BaseModel):
    user_id: str
    post_id: str
    channel_id: str
    team_id: str
    context: Dict[str, str]






@app.post("/system/add_article/")
async def add_article_to_graph(article: Article):
    article_ = {}
    article_["doi"] = article.doi
    article_["title"] = article.title
    article_["abstract"] = article.abstract
    article_["authors"] = [author for author in article.authors]
    article_["keywords"] = [keyword for keyword in article.keywords]     
    article_["journal"] = article.journal
    article_["publication_year"] = article.publication_year
    article_["generation"] = article.generation
    logmessage = f"APILOG: {article.doi} add requested!"
    logging.info(logmessage)
    db_driver.add_article(article_)
    

@app.post("/chatbot/update_article_ranking/")
async def update_article_ranking(mattermost_request: MatterMostRequest):
    post = {}
    post["post_id"] = mattermost_request.post_id
    post["user_id"] = mattermost_request.user_id
    post["action"] = mattermost_request.context["action"]
    db_driver.update_post_ranking(post)


@app.post("/chatbot/add_doi/")
async def add_article_by_doi(token: str = Form(...),text:str = Form(...), user_id:str = Form(...), channel_id:str = Form(...)):
    if token == "ok3t9dmjtp8n8qq3s8ww4mxdhy":
        article = api_parser.parse("wos", "DO", text)
        if article is not None:
            doi = article["doi"]
            logmessage= f"APILOG: Found article DOI: {doi}\nCheck database if non existent"
            logging.info(logmessage)
            article_ = db_driver.get_article_by_doi(doi)
            if article_ is not None:
                logging.info("DOI in system")
                chatbot.post_message(f"Article {doi} already in system", channel_id)
            else:
                logmessage = f"Article {doi} not in system. Add request send"
                logging.info(logmessage)
                db_driver.add_user_article(article, user_id)
                chatbot.post_message(f"Article {doi} was added to the system, thank you!", channel_id)
        else:
            logmessage = f"APILOG: No articles found for {text}."
            logging.info(logmessage)
            chatbot.post_message(logmessage + "\nPlease check DOI", channel_id)
            
    


@app.get("/kiosk/update/")
async def update_kiosk(k=6):
    relevant_articles = db_driver.get_relevant_articles()
    for article in relevant_articles:
        article["authors"] = db_driver.get_article_authors(article["doi"])
        article["authors"] = ", ".join(article["authors"])
        article["journal"] = db_driver.get_article_journal(article["doi"])
    returnage = []
    while len(returnage) != k:
        article = random.choice(relevant_articles)
        if  article not in returnage:
            returnage.append(article)
    return returnage

@app.post("/system/link_citations/")
async def link_citations(citation_mapping: CitationMapping):
    for article in citation_mapping.articles:
        article_ = {}
        article_["doi"] = article.doi
        article_["title"] = article.title
        article_["abstract"] = article.abstract
        article_["authors"] = article.authors
        article_["keywords"] = article.keywords
        article_["journal"] = article.journal
        article_["generation"] = article.generation
        article_["publication_year"] = article.publication_year
        db_driver.add_article(article_)
        db_driver.link_citing_articles(article_["doi"], citation_mapping.referencer_doi, citation_mapping.citation_direction)
        logging.info("APILOG: Citation linking requested!")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
	logging.error(f"{request}: {exc_str}")
	content = {'status_code': 10422, 'message': exc_str, 'data': None}
	return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

@app.get("/system/debug/")
async def debug_conn():
    print("success")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5001)