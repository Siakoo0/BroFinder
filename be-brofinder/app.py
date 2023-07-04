from source.api.FlaskServer import FlaskServer
from source.crawlers.Crawler import Crawler, CrawlerMode

from source.database.mongodb.entities.Product import Product

from source.helpers.Updater import Updater

from dotenv import load_dotenv

from queue import Queue
import logging

from requests import post

class App:
  def __init__(self) -> None:
      # Caricamento del file di configurazione
      load_dotenv(".env")
  
  def run(self):
    # Queue    
    queues = {
      "crawler/search_queue": Queue(),
      "crawler/updater": Queue()
    }
    
    # Queue Producer
    flask = FlaskServer("localhost", "8080", queues)
    flask.start()
    
    # Product Updater
    updater = Updater(queues["crawler/updater"])
    updater.start()
    
    # Queue Consumer
    crawlers = [
      Crawler(
        "RequestCrawler1", 
        queues["crawler/search_queue"]
      ),
      Crawler(
        "RequestCrawler2", 
        queues["crawler/search_queue"]
      ),
      Crawler(
        "UpdaterCrawler", 
        queues["crawler/updater"], 
        mode=CrawlerMode.FETCH_URL
      ),
      Crawler(
        "UpdaterCrawler1", 
        queues["crawler/updater"], 
        mode=CrawlerMode.FETCH_URL
      )
    ]
    
    for crawler in crawlers:
      crawler.start()
    
    # post("http://localhost:8080/api/search", data={
    #   "text" : "iphone 6",
    #   "user" : 199791044,
    #   "forward" : True
    # })
        
    while True: pass

if __name__ == "__main__":
  app = App()
  app.run()
  