import urllib.request as libreq
import xmltodict

class ApiParserModule:
    def __init__(self):
        self.arxiv_base_url = "http://export.arxiv.org/api/query?search_query="
        self.chemrxiv_base_url = "https://chemrxiv.org/engage/chemrxiv/public-api/v1/items"

    def parse(self, api: str, query_param:str):
        if api == "arxiv":
            query_param = query_param.replace(" ", "+")
            query_param = "%22" + query_param + "%22"
            search_query = f"all:{query_param}&start=0&max_results=10"
            query_url = self.arxiv_base_url + search_query
            with libreq.urlopen(query_url) as url:
                r = url.read()
            article_dict = xmltodict.parse(r)
            article_list = parse_arxiv_result_dict(article_dict)
            return article_list
        if api == "chemrxiv":
            params = {"term": query_param}
            
            pass
        if api == "wos":
            pass
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
if __name__ == "__main__":
    parser = ApiParserModule()
    article_list = parser.parse("arxiv", "cond-mat.mtrl-sci")
    test = 0