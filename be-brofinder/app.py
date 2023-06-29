from source.Crawler import Crawler
# import asyncio

from source.api.FlaskServer import FlaskServer

if __name__ == "__main__":
    # crawler = Crawler()
    # crawler.start()

    FlaskServer("localhost", "80").start()

    while True:
        pass