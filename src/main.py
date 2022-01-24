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
from chatbotactions import ChatBot
from graphdriver import *
from api_parser.apiparsermodule import ApiParserModule
import os
from datetime import date
import random
app = FastAPI()
templates = Jinja2Templates(directory="frontend/templates")
logging.basicConfig(
    filename="logs/api.log",
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
db_driver = GraphDBDriver("bolt://localhost:7687", os.environ["NEO4J_USER"],"$cheisse4ldder")
api_parser = ApiParserModule()
chatbot = ChatBot(token= "cw4ona15y3f57mobs3p6rdba5r", primary_channel_id="u7km46zfofrpzf3q7m344mj5kw")

app.add_middleware(
    CORSMiddleware,
    allow_credentials = True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Keyword(BaseModel):
    keyword:str
class Author(BaseModel):
    name:str
class Article(BaseModel):
    title: str
    abstract: str
    authors: List[str]
    doi: str
    journal: str
    keyword: List[str]
    publication_year: int
    generation: int
class CitationMapping(BaseModel):
    articles: List[Article]
    referencer_doi: str  

class TitleList(BaseModel):
    titles: List[str]
class MattermostContext(BaseModel):
    action: str
class MatterMostRequest(BaseModel):
    user_id: str
    post_id: str
    channel_id: str
    team_id: str
    context: Dict[str, str]
class Intermediate(BaseModel):
    content: Dict[str, int]
class DoiCommand(BaseModel):
    payload: Dict[str,str]





@app.post("/add_article/")
async def add_article_to_graph(article: Article):
    article_ = {}
    article_["doi"] = article.doi
    article_["title"] = article.title
    article_["abstract"] = article.abstract
    article_["authors"] = [author for author in article.authors]
    article_["keywords"] = [keyword for keyword in article.keyword]     
    article_["journal"] = article.journal
    article_["publication_year"] = article.publication_year
    article_["generation"] = article.generation
    logmessage = f"APILOG: {article.doi} add requested!"
    logging.info(logmessage)
    db_driver.add_article(article_)
    

@app.post("/addbylist/")
async def add_keywords(keywords: Intermediate):

    with open("data/keywordsss.csv", "w") as csv_f:
        writer = csv.writer(csv_f)
        for key, value in keywords.content.items():
            writer.writerow([key, value])

@app.post("/chatbot/update_article_ranking/")
async def update_article_ranking(mattermost_request: MatterMostRequest):
    post = {}
    post["post_id"] = mattermost_request.post_id
    post["user_id"] = mattermost_request.user_id
    post["action"] = mattermost_request.context["action"]
    db_driver.update_post_ranking(post)


@app.post("/add_doi/")
async def add_article_by_doi(token: str = Form(...),text:str = Form(...), user_id:str = Form(...), channel_id:str = Form(...)):
    if token == "ok3t9dmjtp8n8qq3s8ww4mxdhy":
        print(text)
        print(user_id)

@app.get("/chatbot/post_relevant_article/")
async def post_relevant_article():
    articles = db_driver.get_relevant_articles()
    relevant_article = random.choice(articles)
    chatbot.post_relevant_article(relevant_article)

@app.get("/kiosk/update/")
async def update_kiosk(k=6):
    relevant_articles = db_driver.get_relevant_articles()
    for article in relevant_articles:
        article["authors"] = db_driver.get_article_authors(article["doi"])
        article["journal"] = db_driver.get_article_journal(article["doi"])
    return [random.choice(relevant_articles) for idx in range(k)]

@app.post("/link_citations/")
async def link_citations(citation_mapping: CitationMapping):
    for article in citation_mapping.articles:
        article_ = {}
        article_["doi"] = article.doi
        article_["title"] = article.title
        article_["abstract"] = article.abstract
        article_["authors"] = article.authors
        article_["keywords"] = article.keyword
        article_["journal"] = article.journal
        article_["generation"] = article.generation
        article_["publication_year"] = article.publication_year
        db_driver.add_citing_articles(article_, citation_mapping.referencer_doi)
        logging.info("APILOG: Citation linking requested!")
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
	logging.error(f"{request}: {exc_str}")
	content = {'status_code': 10422, 'message': exc_str, 'data': None}
	return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

@app.get("/debug/")
async def debug_conn():
    print("success")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5001)