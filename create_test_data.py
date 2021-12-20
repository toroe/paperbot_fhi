import random
def create_test_data(k):
    article_collection = []
    for i in range(k):
        article = {}
        article["doi"] = f"DOI-{str(i)}"
        article["title"] = f"Test{str(i)}"
        article["abstract"] = "Lorem Ipsum 123"
        article["authors"] = [f"TestName{random.randint(1,10)}" for i in range(3)]
        article["authors"] = list(dict.fromkeys(article["authors"]))
        article["keywords"] = [f"TestKeyword{random.randint(1,10)}" for i in range(3)]
        article["keywords"] = list(dict.fromkeys(article["keywords"]))
        article["references"] = [f"DOI-{random.randint(1,100)}" for i in range(10)]
        article["references"] = list(dict.fromkeys(article["references"]))
        if article["doi"] in article["references"]:
            article["references"].remove(article["doi"])
        article_collection.append(article)
    return article_collection
