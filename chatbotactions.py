from mattermostdriver import Driver
import os
class ChatBot:
    def __init__(self):
        self.driver = Driver
        token = os.environ["CHATBOT_TOKEN"]
        self.driver = Driver(options={"url": "thmm.rz-berlin.mpg.de","token":token, "debug": True})
        self.driver.login()

    def post_relevant_article(self, article):
        channel_id = "138hexmf4tfrdmsz6o9pzieftc"
        attachment = {"attachments": [{"pretext": "Please assess the article for relevancy", 
                        "actions":[{"id": "upvote","name": "Relevant","integration": 
                        {"url": "http://localhost:5001/update_article_ranking/","context": {"action":"upvote"}}},{"id": "downvote","name": "Not relevant","integration": {"url": "http://localhost:5001/update_article_ranking/","context": {"action":"downvote"}}}]}]}
        message = "Title: " + article["title"] + "\n Authors: " + article["authors"] + "\n Journal: " + article["journal"]
        self.driver.post.create_post(options={"channel_id":channel_id, "message":message, "props":attachment})
if __name__ == "__main__":
    new = ChatBot()
    test = 0