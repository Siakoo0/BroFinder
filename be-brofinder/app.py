from source.api.FlaskServer import FlaskServer
from source.crawlers.Crawler import Crawler
from source.database.redis.RedisAgent import RedisAgent

from dotenv import load_dotenv

from queue import Queue
import logging


class App:
  def __init__(self) -> None:
      # Caricamento del file di configurazione
      load_dotenv(".env")
  
  def run(self):
    # logging.basicConfig(level=logging.NOTSET, format='[ %(name)s@%(module)s::%(funcName)s ] [ %(asctime)s ] [ %(levelname)s ] - %(message)s')

    FlaskServer("localhost", port="8080").start()
    
    # Queue Producer    
    queues = {
      "crawler/search_queue": Queue()
    }
    
    redis = RedisAgent(**{
              "host" : "localhost",
              "port" : 6379,
              "queues" : queues
            })
    
    redis.start()
    
    # Queue Consumer
    Crawler("Crawler1", queues["crawler/search_queue"]).start()
    # Crawler("Crawler2", queues["crawler/search_queue"]).start()
    
    while True: pass

if __name__ == "__main__":
  app = App()
  app.run()
  