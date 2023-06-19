from typing import List
from source.crawlers.entities.Product import Product
from source.crawlers.scrapers.Scraper import Scraper

import json
from bs4 import BeautifulSoup, ResultSet, Tag

class TrovaPrezziScraper(Scraper):

    def search(self, product: str) -> List[Product]:
        search_url = self.prepareSearchURL(f"{self.base_url}/api/v3/categories/-1/autocomplete", {"term" : product})

        req = self.request(search_url)

        pages = self.__fetchPages(req.text)
        print(pages)

        with open("pagetrovaprezzi.html", "w+", encoding="utf-8") as file:
            file.write(req.text)

        return []

    def __fetchPages(self, page):
        data = json.loads(page)["data"]
        return [f'{self.base_url}{link["attributes"]["path"]}' for link in data]

    @property
    def base_url(self):
        return "https://www.trovaprezzi.it"