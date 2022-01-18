from mattermostdriver import Driver
import os
class ChatBot:
    def __init__(self):
        self.driver = Driver
        #token = os.environ["CHATBOT_TOKEN"]
        debug_token = "xyfx9uf93fn6jn7qs97975to9o"
        self.driver = Driver(options={"token":debug_token, "scheme": "http"})
        self.driver.login()

    def post_relevant_article(self, article):
        channel_id = "138hexmf4tfrdmsz6o9pzieftc"
        debug_channel = "u7km46zfofrpzf3q7m344mj5kw"
        attachment = {"attachments": [{"pretext": "Please assess the article for relevancy", 
                        "actions":[{"id": "upvote","name": "Relevant","integration": 
                        {"url": "http://localhost:5001/update_article_ranking/","context": {"action":"upvote"}}},{"id": "downvote","name": "Not relevant","integration": {"url": "http://localhost:5001/update_article_ranking/","context": {"action":"downvote"}}}]}]}
        message = "Title: " + article["title"] + "\n Authors: " + article["authors"] + "\n Journal: " + article["journal"]
        self.driver.post.create_post(options={"channel_id":debug_channel, "message":message, "props":attachment})
        