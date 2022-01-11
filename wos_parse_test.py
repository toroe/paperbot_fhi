"""
import csv
with open("data/keywords.csv", mode='r') as inp:
    reader = csv.reader(inp)
    one_dict_from_csv = {rows[0]:rows[1] for rows in reader}
with open("data/keywordss.csv", mode='r') as inp:
    reader = csv.reader(inp)
    two_dict_from_csv = {rows[0]:rows[1] for rows in reader}
with open("data/keywordsss.csv", mode='r') as inp:
    reader = csv.reader(inp)
    three_dict_from_csv = {rows[0]:rows[1] for rows in reader}
print(three_dict_from_csv)
new_keys = {}
new_keys["wos"] = one_dict_from_csv
new_keys["arxiv"] = three_dict_from_csv
new_keys["chemrxiv"] = two_dict_from_csv
with open("data/merged_keywords.csv", "w") as csv_f:
    writer = csv.writer(csv_f)
    for key, value in new_keys.items():
        writer.writerow([key, value])
        """
import webbrowser

webbrowser.open("http://gateway.webofknowledge.com/gateway/Gateway.cgi?GWVersion=2&SrcApp=PARTNER_APP&SrcAuth=LinksAMR&KeyUT=WOS:000423197900018&DestLinkType=CitingArticles&DestApp=ALL_WOS&UsrCustomerID=6992c4ee433f66f92fb5ad6d074df405")