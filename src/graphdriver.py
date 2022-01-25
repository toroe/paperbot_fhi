from operator import ge
from os import name, environ
from typing import Dict, List
from neo4j import GraphDatabase
from datetime import date
import json
import logging
class GraphDBDriver:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        logging.basicConfig(
    filename="logs/api.log",
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
    def close(self):
        self.driver.close()

    def add_article(self, article):
        with self.driver.session() as session:           
                session.write_transaction(self._add_article_to_graph, article)
        self.driver.close()

    def add_user_article(self, article, user_id):
        with self.driver.session() as session:
            session.write_transaction(self._add_user_article_to_graph, article, user_id)
        self.driver.close()
    def get_article_by_doi(self, doi):
        with self.driver.session() as session:
            article_ = session.read_transaction(self._get_article_by_doi, doi)
        self.driver.close()
        if article_ == []:
            return None
        else:
            article = {}
            article["doi"] = article_["a"]["doi"]
            article["title"] = article_["a"]["title"]
            article["publication_year"] = article_["a"]["publication_year"]
            return article
        
    def get_articles_doi(self, generation: str, limit: str):
        with self.driver.session() as session:
            result = session.read_transaction(self._get_articles_doi,generation, limit)
        self.driver.close()
        return result
    def get_relevant_articles(self):
        with self.driver.session() as session:
            articles = session.read_transaction(self.__get_relevant_articles)
        articles_ = []
        for article_ in articles:
            article = {}
            article["doi"] = article_["a"]["doi"]
            article["title"] = article_["a"]["title"]
            article["publication_year"] = article_["a"]["publication_year"]
            articles_.append(article)
        self.driver.close()
        return articles_
    def update_post_ranking(self, post):
        with self.driver.session() as session:      
            session.write_transaction(self._update_post, post)
        self.driver.close()
    def get_article_authors(self, doi):
        with self.driver.session() as session:
            authors = session.read_transaction(self._get_article_authors, doi)
        authors_ = []
        for author in authors:
            if author["b"]["name"] not in authors_:
                authors_.append(author["b"]["name"])
        self.driver.close()
        return authors_

    def get_article_journal(self, doi):
        with self.driver.session() as session:
            journal = session.read_transaction(self._get_article_journal, doi)

        journal_ = journal[0]["b"]["name"]
        return journal_

    def add_citing_articles(self, article, source_doi):
        with self.driver.session() as session:
            session.write_transaction(self._add_article_to_graph, article)
            session.write_transaction(self._add_citing_articles, article, source_doi)
        self.driver.close()

    def update_article_post(self, article_doi, post_id):
        with self.driver.session() as session:
            session.write_transaction(self._update_article_post, article_doi, post_id)
        self.driver.close() 

    @staticmethod 
    def _add_citing_articles(tx, article, source_doi):
        result = tx.run('MATCH (a:Article  {doi:$source_doi}), (b:Article {doi:$doi}) MERGE (b)-[r:cites]->(a) RETURN a, b', doi=article["doi"], source_doi=source_doi)
        for record in result:
            logmessage = "GRAPHLOG: Created relationship between {doi1} and {doi2}".format(doi1=record["a"]["doi"], doi2 = record["b"]["doi"])
            logging.info(logmessage)
             

    @staticmethod
    def _add_article_to_graph(tx, article):
        doi = article["doi"]
        title = article["title"]
        abstract = article["abstract"]
        authors = article["authors"]
        keywords = article["keywords"]
        journal = article["journal"]
        publication_year = article["publication_year"]
        generation = article["generation"]
        creation_date=date.today()
        tx.run('MERGE (a:Article {doi: $doi, title: $title, abstract: $abstract, publication_year: $publication_year})', doi=doi, title=title, abstract=abstract, publication_year=publication_year)
        tx.run("MATCH (a:Article {doi:$doi}) WHERE a.creation_date IS NULL SET a.creation_date = $creation_date", doi=doi, creation_date=creation_date)
        tx.run("MATCH (a:Article {doi:$doi}) WHERE a.generation IS NULL SET a.generation = $generation", doi=doi, generation=generation)
        for author in authors:
            tx.run('MERGE (a:Author {name: $name})', name=author)
            tx.run("MATCH (a:Author {name: $name}) WHERE a.creation_date IS NULL SET a.creation_date = $creation_date", name=author, creation_date=creation_date)
            tx.run('MATCH (a:Article {doi:$doi}), (b:Author {name:$author}) MERGE (b)-[r:isAuthor]->(a)', doi=doi, author=author)
        if keywords is not None:
            for keyword in keywords:
                tx.run('MERGE (a:Keyword {keyword: $keyword})', keyword=keyword)
                tx.run("MATCH (a:Keyword {keyword:$keyword}) WHERE a.creation_date is NULL SET a.creation_date = $creation_date", keyword=keyword, creation_date=creation_date)
                tx.run('MATCH (a:Article {doi:$doi}), (b:Keyword {keyword:$keyword}) MERGE (a)-[r:isAbout]->(b)', doi=doi, keyword=keyword)
        tx.run('MERGE (a:Journal {name:$journal})', journal=journal)
        tx.run('MATCH (a:Journal {name:$journal}) WHERE a.creation_date is NULL SET a.creation_date = $creation_date', journal=journal, creation_date=creation_date)
        tx.run('MATCH (a:Article  {doi:$doi}), (b:Journal {name:$journal}) MERGE (a)-[r:publishedIn]->(b)', doi=doi, journal=journal)
        result = tx.run("MATCH (a:Article  {doi:$doi}) RETURN a", doi=doi)
        if result is not None:
            logmessage = f"GRAPHLOG: {doi} added!"
            logging.info(logmessage)
        else:
            logmessage = f"GRAPHLOG: ERROR ADDING {doi}"
            logging.warning(logmessage)
                
        return result
    @staticmethod
    def _add_user_article_to_graph(tx, article, user_id):
        doi = article["doi"]
        title = article["title"]
        abstract = article["abstract"]
        authors = article["authors"]
        keywords = article["keywords"]
        journal = article["journal"]
        publication_year = article["publication_year"]
        user_id = user_id
        creation_date=date.today()
        tx.run('MERGE (a:Article {doi: $doi, title: $title, abstract: $abstract, publication_year: $publication_year})', doi=doi, title=title, abstract=abstract, publication_year=publication_year)
        tx.run("MATCH (a:Article {doi:$doi}) WHERE a.creation_date IS NULL SET a.creation_date = $creation_date", doi=doi, creation_date=creation_date)
        tx.run("MATCH (a:Article{doi:$doi}) MERGE (u:User{id:$user_id})  MERGE (u)<-[:user_added]-(a)", user_id=user_id, doi=doi)
        for author in authors:
            tx.run('MERGE (a:Author {name: $name})', name=author)
            tx.run("MATCH (a:Author {name: $name}) WHERE a.creation_date IS NULL SET a.creation_date = $creation_date", name=author, creation_date=creation_date)
            tx.run('MATCH (a:Article {doi:$doi}), (b:Author {name:$author}) MERGE (b)-[r:isAuthor]->(a)', doi=doi, author=author)
        if keywords is not None:
            for keyword in keywords:
                tx.run('MERGE (a:Keyword {keyword: $keyword})', keyword=keyword)
                tx.run("MATCH (a:Keyword {keyword:$keyword}) WHERE a.creation_date is NULL SET a.creation_date = $creation_date", keyword=keyword, creation_date=creation_date)
                tx.run('MATCH (a:Article {doi:$doi}), (b:Keyword {keyword:$keyword}) MERGE (a)-[r:isAbout]->(b)', doi=doi, keyword=keyword)
        tx.run('MERGE (a:Journal {name:$journal})', journal=journal)
        tx.run('MATCH (a:Journal {name:$journal}) WHERE a.creation_date is NULL SET a.creation_date = $creation_date', journal=journal, creation_date=creation_date)
        tx.run('MATCH (a:Article  {doi:$doi}), (b:Journal {name:$journal}) MERGE (a)-[r:publishedIn]->(b)', doi=doi, journal=journal)
        result = tx.run("MATCH (a:Article  {doi:$doi}) RETURN a", doi=doi)
        if result is not None:
            logmessage = f"GRAPHLOG: {doi} added per request by user: {user_id}!"
            logging.info(logmessage)
        else:
            logmessage = f"GRAPHLOG: ERROR ADDING {doi}"
            logging.warning(logmessage)
    @staticmethod
    def _get_article_by_doi(tx, doi):
        results = tx.run("MATCH (a:Article {doi:$doi}) RETURN a", doi=doi)
        article = [record for record in results]
        return article
    @staticmethod
    def _get_article_authors(tx, doi):
        results = tx.run('MATCH (a:Article{doi:$doi}) <-[:isAuthor]-(b) RETURN b', doi=doi)
        authors = [record for record in results]
        return authors

    @staticmethod
    def _get_article_journal(tx, doi):
        results = tx.run('MATCH (a:Article{doi:$doi}) -[:publishedIn]->(b) RETURN b', doi=doi)
        journal = [record for record in results]
        return journal
        
    @staticmethod
    def __get_relevant_articles(tx):
        results = tx.run("MATCH (a:Article) WHERE 2022 - a.publication_year <=3 AND (a.generation=0 OR ((a)<-[:user_added]-())) RETURN a LIMIT 25")
        articles = [record for record in results]
        return articles
    @staticmethod 
    def _get_post_by_id(tx, post_id):
        posts = []
        result = tx.run("MATCH (p:Post) WHERE p.id ={post_id:$post_id} RETURN p",  post_id=post_id)
        for record in result:
            posts.append(record)
        return posts
    @staticmethod
    def _update_post(tx, post):
        post_id=post["post_id"]
        user_id=post["user_id"]

        tx.run("MERGE (p:Post {id:$post_id})", post_id=post_id)
        tx.run("MERGE (u:User {id:$user_id})", user_id=user_id)  
        tx.run("MATCH (p:Post {id:$post_id}), (u:User {id:$user_id}) MERGE (u) -[r:voted]->(p) SET r.vote = $vote", post_id=post["post_id"],user_id=post["user_id"], vote=post["action"])
        logmessage = f"GRAPHLOG: REGISTERED VOTE FOR POST: {post_id} FROM USER: {user_id}"
        logging.info(logmessage)
    @staticmethod
    def _update_article_post(tx, article_doi, post_id):
        post_date=date.today()
        result = tx.run("MATCH (a:Article{doi:$doi}) MERGE (p:Post{id:$id}) MERGE (a)-[r:posted]->(p) SET p.post_date = $post_date RETURN r", doi=article_doi, id=post_id, post_date=post_date) 
        posts = [record for record in result]
        if posts is not None:
            logmessage = f"GRAPHLOG: CREATE POST: {post_id} WITH RELATIONSHIP TO {article_doi}"
            logging.info(logmessage)
        else:
            logging.info("GRAPHLOG: ERROR SETTING POST")
        return posts
if __name__ == "__main__":
    driver = GraphDBDriver("bolt://localhost:7687", "neo4j", "password")
    dois = driver.get_article_authors("10.1063/5.0071249")
    test = 0
