from api_parser.apiparsermodule import ApiParserModule
import json

def parse_chemrxiv_by_keyword(api_parser_module, keywords):
    pass
def parse_wos_by_title(api_parser_module, title):
    return api_parser_module.parse("wos", title)

if __name__ == "__main__":
    api_parser_module = ApiParserModule()
    with open("data/paperbot_clean_titles.json", "r", encoding = "ascii") as f:
        article_titles = json.load(f)
    parsed_articles = []
    for title in article_titles:
        title = title.replace('"', "")
        title = title.replace("<sup>", "")
        title = title.replace("</sup>", "")
        title = title.encode("ascii", "ignore")
        title = title.decode()
        parsed_articles.append(api_parser_module.parse("wos", title))

    test = 0