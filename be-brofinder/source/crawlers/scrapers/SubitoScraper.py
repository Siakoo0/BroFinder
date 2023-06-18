from typing import List
from source.crawlers.entities.Product import Product
from source.crawlers.scrapers.Scraper import Scraper

from urllib.parse import urlencode
from bs4 import BeautifulSoup, ResultSet, Tag

class SubitoScraper(Scraper):
    
    @property
    def base_url(self):
        return "https://www.subito.it/"
    
    def search(self, product: str) -> List[Product]:
        params : dict = {"q" : product}
        base_url = f"{self.base_url}/annunci-italia/vendita/usato"

        products : list = []

        pages = self.__fetchPages(base_url, params)

        for num, page in enumerate(pages):
            with open(f"page{num}.html", "w+", encoding="utf-8") as file:
                self.logger.info("Fetched")
                file.write(page["text"])
            

    def __fetchPages(self, base_url, params):
        pages = []

        for page in range(1, 10):
            params["o"] = page
            url : str = "{}?{}".format(base_url, urlencode(params))
            resp = self.request(url)

            if "Su Subito trovi tutto. Questa pagina, però, non c'è..." not in resp.text:
                pages.append({"url" : url, "text": resp.text})

        return pages