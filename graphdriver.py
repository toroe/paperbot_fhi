from os import name, environ
from typing import Dict, List
from neo4j import GraphDatabase
import json
class GraphDBDriver:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def populateNetwork(self, article):
        with self.driver.session() as session:
            session.write_transaction(self._create_network_from_article, article)
        self.driver.close()
    def get_node_by_name(self):
        with self.driver.session() as session:
            result = session.read_transaction(self._get_node_by_name)
        self.driver.close()
        return result
    def update_post_ranking(self, post):
        with self.driver.session() as session:      
            session.write_transaction(self._update_post, post)
        self.driver.close()
    def check_article_relevance(self, article):
        pass
    def add_citing_articles(self, article, source_doi):
        with self.driver.session() as session:
            session.write_transaction(self._create_network_from_article, article)
            session.write_transaction(self._add_citing_articles, article, source_doi)
        self.driver.close()
        
    @staticmethod 
    def _add_citing_articles(tx, article, source_doi):
        result = tx.run('MATCH (a:Article  {doi:$source_doi}), (b:Article {title:$title}) MERGE (b)-[r:cites]->(a) RETURN a, b', title=article["title"], source_doi=source_doi)
        for record in result:
            print("Create relationship between {doi1} and {doi2}".format(doi1=record["a"]["doi"], doi2 = record["b"]["doi"]))
             

    @staticmethod
    def _create_network_from_article(tx, article):
        doi = article["doi"]
        title = article["title"]
        abstract = article["abstract"]
        authors = article["authors"]
        keywords = article["keywords"]
        journal = article["journal"]
        tx.run('MERGE (a:Article {doi: $doi, title: $title, abstract: $abstract})', doi=doi, title=title, abstract=abstract)
        for author in authors:
            tx.run('MERGE (a:Author {name: $name})', name=author)
            tx.run('MATCH (a:Article {title:$title}), (b:Author {name:$author}) MERGE (b)-[r:isAuthor]->(a)', title=title, author=author)
        if keywords is not None:
            for keyword in keywords:
                tx.run('MERGE (a:Keyword {keyword: $keyword})', keyword=keyword)
                tx.run('MATCH (a:Article {title:$title}), (b:Keyword {keyword:$keyword}) MERGE (a)-[r:isAbout]->(b)', title=title, keyword=keyword)
        tx.run('MERGE (a:Journal {name:$journal})', journal=journal)
        tx.run('MATCH (a:Article  {title:$title}), (b:Journal {name:$journal}) MERGE (a)-[r:publishedIn]->(b)', title=title, journal=journal)
    @staticmethod
    def _get_node_by_name(tx):
        nodes = []
        results = tx.run('MATCH (n:Article) RETURN n LIMIT 1')
        for record in results:
            nodes.append(record)
        return nodes
    @staticmethod
    def _check_article_relevance(tx, article):
        doi = article["doi"]
        title = article["title"]
        abstract = article["abstract"]
        authors = article["authors"]
        keywords = article["keywords"]
        journal = article["journal"]
    @staticmethod 
    def _get_post_by_id(tx, post_id):
        posts = []
        result = tx.run("MATCH (p:Post) WHERE p.id ={post_id:$post_id} RETURN p",  post_id=post_id)
        for record in result:
            posts.append(record)
        return posts
    @staticmethod
    def _update_post(tx, post):
        tx.run("MERGE (p:Post {id:$post_id})", post_id=post["post_id"])
        tx.run("MERGE (u:User {id:$user_id})", user_id=post["user_id"])  
        tx.run("MATCH (p:Post {id:$post_id}), (u:User {id:$user_id}) MERGE (u) -[r:voted]->(p) SET r.vote = $vote", post_id=post["post_id"],user_id=post["user_id"], vote=post["action"])

if __name__ == "__main__":
    driver = GraphDBDriver("bolt://localhost:7687", "neo4j", "password")
    with open("data/parsed_articles.json", "r") as fp:
        articles = json.load(fp)
    for article in articles:
        driver.populateNetwork(article)
    test = 0
