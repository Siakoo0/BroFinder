from bson.objectid import ObjectId
# import asyncio


from source.entities.Search import Search

from source.crawlers.Crawler import Crawler

from source.api.FlaskServer import FlaskServer


class App:
  
  def __init__(self) -> None:
    pass
  
  def run(self):
    # crawler = Crawler()
    # crawler.start()
    FlaskServer("localhost", "8080").start()
    while True: pass

  
if __name__ == "__main__":
    app = App()
    app.run()