# Paperbot 
This is the documentation for the FHI Paperbot.

## Quickstart
### Database
Make sure the database is running on the server.
```
sudo neo4j status
```
### Main Api
Start Main api 
```
python3 src/main.py
```
This will start the Paperbot REST Api on localhost:5001. Hostadress and Port are changeable.

### Kiosk
Make sure all npm packages are installed.
```
src/kiosk_frontend/ npm install
```
Start Kiosk
```
src/kiosk_frontend/ npm start
```
Kiosk will start on localhost:3000.
Refreshrate and amount articles pulled can be configured here:
https://github.com/toroe/paperbot_fhi/blob/507df358423695d35f828e4cc83a47405c8e77a3/src/kiosk_frontend/src/components/CardItems/CardItems.js#L4-L19

### Chatbot
To trigger timely chatbot messenges configure a cronjob on src/chatbotmodule.py. Arguments can be passed as follows:
https://github.com/toroe/paperbot_fhi/blob/507df358423695d35f828e4cc83a47405c8e77a3/src/chatbotmodule.py#L36-L41

### Api Scraper
Api scraper jobs can be configured with src/apiparsermodule.py. Arguments can be passed as follows:
https://github.com/toroe/paperbot_fhi/blob/507df358423695d35f828e4cc83a47405c8e77a3/src/apiparsermodule.py#L132-L139
