from typing import List

from crawler.entities.Product import Product
from crawler.scrapers.Scaper import ScraperAbstractClass

from requests import request, Response
from bs4 import BeautifulSoup

class AmazonScraper(ScraperAbstractClass):

    def search(self, product: str) -> List[Product]:
        pass