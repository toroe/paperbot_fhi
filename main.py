from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from graphdriver import *

app = FastAPI()
templates = Jinja2Templates(directory="frontend/templates")
db_driver = GraphDBDriver("bolt://localhost:7687", "neo4j", "$cheisse4ldder")
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
    authors: List[Author]
    doi: str
    journal: str
    keyword: List[Keyword]
class Articles(BaseModel):
    articles: List[Article]
    
@app.post("/addarticles/")
async def add_article_to_graph(articles: Articles):
    print("success")
    db_driver.populateNetwork(articles)
@app.post("/addarticle/")
async def add_article_to_graph(article: Article):
    article_ = {}
    article_["doi"] = article.doi
    article_["title"] = article.title
    article_["abstract"] = article.abstract
    article_["authors"] = [author.name for author in article.authors]
    article_["keywords"] = [keyword.keyword for keyword in article.keyword]
    article_["journal"] = article.journal
    db_driver.populateNetwork(article_)



if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5001, log_level="info")