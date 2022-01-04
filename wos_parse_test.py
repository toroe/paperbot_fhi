from api_parser.apiparsermodule import ApiParserModule
import json

with open("paperbot_clean_titles.json", "r", encoding = "ascii") as f:
    article_titles = json.load(f)
api_parser = ApiParserModule()
article_list = []
for title in article_titles:
    title = title.replace('"', "")
    title = title.encode("ascii", "ignore")
    title = title.decode()
    article = api_parser.parse("wos", title)
    if article != None:
     article_list.append(article)
with open("parsed_articles.json", "w") as fp:
    json.dump(article_list, fp)
