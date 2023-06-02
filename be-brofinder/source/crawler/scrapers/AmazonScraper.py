from typing import List

from source.crawler.entities.Product import Product
from source.crawler.scrapers.Scraper import Scraper


from urllib.parse import urlencode
from requests import request, Response
from bs4 import BeautifulSoup

class AmazonScraper(Scraper):
    _uri = "https://www.amazon.it/s?k="
    
    def search(self, product: str) -> List[Product]:
        params = {"k" : product}
        response : Response = request(AmazonScraper._uri, urlencode(params))
        with open("file.html", "wb+", encoding="utf-8") as f:
            f.write(response.text)
            
        bs = BeautifulSoup(response.text, "html.parser")
        pass