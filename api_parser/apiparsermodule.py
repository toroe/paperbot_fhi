from __future__ import print_function
import urllib.request as libreq
import xmltodict, time, logging, woslite_client, scholarly, requests
from woslite_client.rest import ApiException
from pprint import pprint
class ApiParserModule:
    def __init__(self):
        self.arxiv_base_url = "http://export.arxiv.org/api/query?search_query="
        self.chemrxiv_base_url = "https://chemrxiv.org/engage/chemrxiv/public-api/v1/items"
        # Configure API key authorization for web of science: key
        configuration = woslite_client.Configuration()
        configuration.api_key['X-ApiKey'] = '0eda632cc7f9313a038b4f955db9f731dc64a738'
   #     self.wos_search_api_instance = woslite_client.SearchApi(woslite_client.ApiClient(configuration))

    
    def parse(self, api: str, query_param:str):
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
            #WEB OF SCIENCE API scrapes for titles TODO: implementation of further scraping alternatives
        if api == "wos":
            database_id = "WOS"
            usr_query = f'TI=({query_param})'  # str | User query for requesting data, ex: TS=(cadmium). The query parser will return errors for invalid queries.
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
        
            except ApiException as e:
                print("Exception when calling IntegrationApi->id_unique_id_get: %s\\n" % e)
     
"""
Takes an ARXIV API result dicts, iterates through results and returns a list with article dicts in it
"""
def parse_arxiv_result_dict(article_dict):
    article_list =  []
    if article_dict["feed"]["opensearch:totalResults"]["#text"] != "0":
        for result in article_dict["feed"]["entry"]:
            article = {}
            art_title = result["title"]
            article["title"] = art_title
            abstract = result["summary"]
            article["abstract"] = abstract
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
                    article["keyword"] = keywords
                if isinstance(e, KeyError):
                    article["keyword"] = [{"keyword":""}] 
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
            article["keyword"] = [keyword["name"] for keyword in article_["item"]["categories"]]
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
        article["journal"] = api_response.data[0].source.source_title[0] + " " + api_response.data[0].source.volume[0]
        article["keyword"] = api_response.data[0].keyword.keywords
        return article
if __name__ == "__main__":
    parser = ApiParserModule()
    article_list = parser.parse("chemrxiv", "Karsten Reuter")
    test = 0