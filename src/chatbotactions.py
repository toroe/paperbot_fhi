import argparse
import random
import logging
from mattermostdriver import Driver
from graphdriver import GraphDBDriver
import os
class ChatBot:
    def __init__(self, token, primary_channel_id):
        self.driver = Driver
        #token = os.environ["CHATBOT_TOKEN"]
        logging.basicConfig(
        filename="logs/api.log",
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
        self.primary_channel_id = primary_channel_id
        self.driver = Driver(options={"url": "thmm.rz-berlin.mpg.de", "port":  8065,"token":token,"scheme":"https"})
        self.driver.login()

    def post_relevant_article(self, article):
        
        attachment = {"attachments": [{"pretext": "Please assess the article for relevancy", 
                        "actions":[{"id": "upvote","name": "Relevant","integration": 
                        {"url": "http://localhost:5001/chatbot/update_article_ranking/","context": {"action":"upvote"}}},{"id": "downvote","name": "Not relevant","integration": {"url": "http://localhost:5001/update_article_ranking/","context": {"action":"downvote"}}}]}]}
        message = "Title: " + article["title"] + "\nDOI: " + article["doi"] +"\nAuthors: " + ", ".join(article["authors"]) + "\nJournal: " + article["journal"] + "\nPublication Year: " + str(article["publication_year"])
        result = self.driver.posts.create_post(options={"channel_id":self.primary_channel_id, "message":message, "props":attachment})
        result["article_doi"] = article["doi"]
        return result
    def get_user(self):
        user = self.driver.users.get_user(user_id="me")
        channel = self.driver.channels.get_channel(channel_id = self.primary_channel_id)
        return channel
    def post_message(self, message, channel_id):
        self.driver.posts.create_post(options={"channel_id":channel_id, "message":message})
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel_id", default="138hexmf4tfrdmsz6o9pzieftc", help="Channel ID article should be posted in")
    parser.add_argument("--db_connection", default="bolt://localhost:7687")
    args = parser.parse_args()
    db_driver = GraphDBDriver(args.db_connection, os.environ["NEO4J_USER"],os.environ["NEO4J_PASSWORD"])
    bot = ChatBot(token = os.environ["CHATBOT_TOKEN"],primary_channel_id=args.channel_id)
    articles = db_driver.get_relevant_articles()
    for article in articles:
        article["authors"] = db_driver.get_article_authors(article["doi"])
        article["journal"] = db_driver.get_article_journal(article["doi"])
    relevant_article = random.choice(articles)
    test = bot.get_user()
    debug = 0
    """
    result = bot.post_relevant_article(relevant_article)
    if (result["article_doi"] and result["id"]) is not None:
        logging.info("CHATBOTLOG: SUCCESSFULLY POSTED")
        db_driver.update_article_post(result["article_doi"], result["id"])
        """