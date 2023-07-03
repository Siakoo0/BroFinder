from source.crawlers.Crawler import Crawler
from source.api.FlaskServer import FlaskServer

from source.database.redis.RedisAgent import RedisAgent
from queue import Queue

from threading import Thread
import logging

from dotenv import load_dotenv

class App:
  def __init__(self) -> None:
      # Caricamento del file di configurazione
      load_dotenv(".env")
  
  def run(self):
    logging.basicConfig(level=logging.NOTSET, format='[ %(name)s@%(module)s::%(funcName)s ] [ %(asctime)s ] [ %(levelname)s ] - %(message)s')
    
    FlaskServer("localhost", port="8080").start()
    
    # Queue Producer    
    queues = {
      "crawler/search_queue": Queue(),
      "crawler/to_update" : Queue()
    }
    
    # Queue Consumer
    Crawler("RequestCrawler1", queues["crawler/search_queue"]).start()
    Crawler("UpdateCrawler1", queues["crawler/to_update"]).start()
    Crawler("UpdateCrawler2", queues["crawler/to_update"]).start()
    
    while True: pass

if __name__ == "__main__":
  app = App()
  app.run()
  