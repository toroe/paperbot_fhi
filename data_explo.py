import json
import csv
with open("parsed_articles.json", "r") as fp:
    articles = json.load(fp)
idx = 0
to_csv = []
for k,v in enumerate(articles):
    tmp = {}

    tmp["DOI"] = v["doi"]
    tmp["atitle"] = v["title"]
    to_csv.append(tmp)
key = to_csv[0].keys()
with open("amr_input.csv", "w", newline="") as out:
    dict_writer = csv.DictWriter(out, key)
    dict_writer.writeheader()
    dict_writer.writerows(to_csv)