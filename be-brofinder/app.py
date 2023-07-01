from source.Crawler import Crawler
# import asyncio

from source.api.FlaskServer import FlaskServer
"""
// Search

const search = [
  {
    "id": 234567890,
    "key" : "portatile macbook",
    "datetime_pub": 12367213768362871
  }
]

"""
if __name__ == "__main__":
    crawler = Crawler()
    crawler.start()

    FlaskServer("localhost", "80").start()

    while True:
      pass