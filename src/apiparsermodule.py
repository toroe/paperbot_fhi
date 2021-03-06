from __future__ import print_function
import argparse
import os
import urllib.request as libreq
import xmltodict, time, logging, woslite_client, scholarly, requests
from woslite_client.rest import ApiException
from pprint import pprint
from src.graphdriver import GraphDBDriver
class ApiParserModule:
    def __init__(self):
        self.arxiv_base_url = "http://export.arxiv.org/api/query?search_query="
        self.chemrxiv_base_url = "https://chemrxiv.org/engage/chemrxiv/public-api/v1/items"
        # Configure API key authorization for web of science: key
        configuration = woslite_client.Configuration()
        configuration.api_key['X-ApiKey'] = os.environ["WOSLITE_KEY"]
        self.wos_search_api_instance = woslite_client.SearchApi(woslite_client.ApiClient(configuration))
        logging.basicConfig(
    filename="logs/api.log",
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
    
    def parse(self, api: str, search_field:str , query_param:str):
        #ARXIV parses all available fields
        if api == "arxiv":
            query_param = query_param.replace(" ", "+")
            query_param = "%22" + query_param + "%22"
            search_query = f"all:{query_param}&start=0&max_results=20&sortBy=submittedDate"
            query_url = self.arxiv_base_url + search_query
            with libreq.urlopen(query_url) as url:
                r = url.read()
            article_dict = xmltodict.parse(r)
            article_list = parse_arxiv_result_dict(article_dict)
            return article_list
        if api == "chemrxiv":
            params = {"term": query_param, "limit": 20}
            r = requests.get(self.chemrxiv_base_url, params=params)
            article_list = parse_chemrxiv_results(r.json())
            return article_list
        #WEB OF SCIENCE API ALL FIELDS
        if api == "wos":
            database_id = "WOS"
            usr_query = f'{search_field}=({query_param})'  # str | User query for requesting data, ex: TS=(cadmium). The query parser will return errors for invalid queries.
            count = 1  # int | Number of records returned in the request
            first_record = 1  # int | Specific record, if any within the result set to return. Cannot be less than 1 and greater than 100000.
            try:
                # Find record(s) by specific id
                api_response = self.wos_search_api_instance.root_get(database_id=database_id, usr_query=usr_query, count=count, first_record=first_record)
                article_list = parse_wos_results(api_response)
                if article_list != None:
                    return article_list
                else:    
                    logging.info(f"{query_param} not found")
                    return None  
            except ApiException as e:
                print("Exception when calling SearchApi->root_get: %s\\n" % e)
                return None
     
"""
Takes an ARXIV API result dicts, iterates through results and returns a list with article dicts in it
"""
def parse_arxiv_result_dict(article_dict):
    article_list =  []
    if article_dict["feed"]["opensearch:totalResults"]["#text"] != "0":
        for result in article_dict["feed"]["entry"]:
            article = {}
            article["title"] = result["title"]         
            article["abstract"]= result["summary"]     
            try:
                authors = [{"name":author["name"]} for author in result["author"]]
                article["authors"] = authors
            except TypeError as e:
                article["authors"] = [{"name":result["author"]["name"]}]
            article["authors"] = authors
            try:
                doi = result["arxiv:doi"]["#text"]
                article["doi"] = doi
            except KeyError as e:
                print(e)
            try:
                journal = result["arxiv:journal_ref"]["#text"]
                article["journal"] = journal
            except KeyError as e:
                article["journal"] = "" 
            try:
                keywords = [{"keyword":result["category"]["@term"]}]
                article["keyword"] = keywords  
            except (KeyError, TypeError) as e:
                if isinstance(e, TypeError):
                    keywords = [{"keyword":keyword["@term"]} for keyword in result["category"]]
                    article["keywords"] = keywords
                if isinstance(e, KeyError):
                    article["keywords"] = [{"keyword":""}] 
            article_list.append(article)
        return article_list
    else:
        print("No results found!")
        return None

def parse_chemrxiv_results(results_):
    article_list = []
    if results_["totalCount"] > 0:
        for article_ in results_["itemHits"]:
            article={}
            article["title"] = article_["item"]["title"]
            article["abstract"] = article_["item"]["abstract"]
            article["authors"] = [author["firstName"] + " " + author["lastName"] for author in article_["item"]["authors"]]
            article["doi"] = article_["item"]["doi"]
            article["journal"] = ""
            article["keywords"] = [keyword["name"] for keyword in article_["item"]["categories"]]
            article_list.append(article)
    return article_list
def parse_wos_results(api_response):
    article = {}
    if api_response.data != []:
        article["title"] = api_response.data[0].title.title[0]
        article["abstract"] = ""
        article["authors"] = [author.split(",")[1].strip()+ " " + author.split(",")[0] for author in api_response.data[0].author.authors]
        try:
            article["doi"] = api_response.data[0].other.identifier_doi[0]
        except TypeError as e:
            article["doi"]  = ""
        try:
            article["journal"] = api_response.data[0].source.source_title[0] + " " + api_response.data[0].source.volume[0]
        except TypeError as e:
            article["journal"] = ""
        article["keywords"] = api_response.data[0].keyword.keywords
        article["publication_year"] = int(api_response.data[0].source.published_biblio_year[0])
        return article
        
if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--api",help="API that should be parsed")
    argparser.add_argument("--search_term", default="", help="Specify which search term should be used")
    argparser.add_argument("--query_term")
    argparser.add_argument("--db_connection", default="bolt://localhost:7687")
    args = argparser.parse_args()
    parser = ApiParserModule()
    db_driver = GraphDBDriver(args.db_connection, os.environ["NEO4J_USER"],os.environ["NEO4J_PASSWORD"])
    logmessage = f"PARSERLOG: Scraping for {args.api} started"
    logging.info(logmessage)
    article_list = parser.parse(args.api, args.search_term,args.query_term)
    for article in article_list:
        doi = article["doi"]
        if db_driver.get_article_by_doi(doi) is None:
            for reference in article["references"]:
                article_ = db_driver.get_article_by_doi(reference["doi"])
                if article_ is not None:
                    if article_["generation"] == (1 or 2):
                        logmessage = f"PARSERLOG: Relevant Article {doi} found!"
                        logging.info(logmessage)
                        db_driver.add_article(article)
                        db_driver.link_citing_articles(doi, article_["doi"], True)
    logmessage = f"PARSERLOG: Scraping for {args.api} finished"
    logging.info(logmessage)
                        
 