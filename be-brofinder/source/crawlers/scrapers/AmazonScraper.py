import asyncio
import time
import aiohttp

from time import sleep
from bs4 import BeautifulSoup, ResultSet, Tag
from typing import List

from uuid import uuid4

from source.crawlers.scrapers.Scraper import Scraper

from source.crawlers.entities.Product import Product
from source.crawlers.entities.Review import Review

class AmazonScraper(Scraper):
    """
        AmazonScraper, modulo per fare lo Scraping dei prodotti di
    """

    @property
    def base_url(self):
        return "https://www.amazon.it"

    def request(self, url, headers : dict = {}):
        headers = headers | {
            'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7'
        }

        return super().request(url, headers)

    def __fetchPages(self, response, base_url):
        bs = BeautifulSoup(response, "html.parser")
        last_page = bs.select_one(".s-pagination-item.s-pagination-ellipsis + .s-pagination-item.s-pagination-disabled").getText()

        last_page = min(5, int(last_page)+1)

        return [f"{base_url}&page={num}" for num in range(1, last_page)]

    def search(self, product) -> str:
        start = time.time()

        params : dict = {"k" : product}
        url : str = self.prepareSearchURL(self.base_url + "/s", params)
        fetched_pages = False
        error_bool = False

        time_wait = 0

        while not fetched_pages and not error_bool:
            if time_wait >= 10: error_bool = True
            try:
                req = self.request(url)
                pages = self.__fetchPages(req.text, url)
                fetched_pages = True
            except:
                time_wait+=1
                sleep(time_wait)

        if not error_bool:
            # Start Async Part
            asyncio.run(self.startFetch(pages))

        end = time.time()

        print("Tempo impiegato: {}s".format(end - start))

    def getHeaders(self):
        return {
            'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
            'User-Agent': self.user_agent()
        }

    # async def saveFile(self, async_request):
    #     await asyncio.sleep(5)
    #     with open(f"{uuid4()}_amazon.html", "w+", encoding="utf-8") as file:
    #         file.write(await async_request.text())

    async def extractFromPage(self, async_response):
        text = await async_response.text()
        url = str(async_response.url)

        bs : BeautifulSoup = BeautifulSoup(text, "html.parser")
        product_links : ResultSet[Tag] = bs.select('[data-component-type="s-search-results"] [data-asin]:not([data-asin=""]) a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal[href*="/dp/"]')

        self.logger.info(f"Inizio il fetching dei prodotti dalla pagina {async_response.url}")

        product_links : ResultSet[Tag] = bs.select('[data-component-type="s-search-results"] [data-asin]:not([data-asin=""]) a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal[href*="/dp/"]')

        product_links : List[str] = [self.base_url + product.get("href").split("/ref")[0] for product in product_links]

        # Tolgo di mezzo i siti ripetuti derivata dalla ricerca del crawler
        product_links = list(dict.fromkeys(product_links))

        self.logger.info(f"Estrapolazione link completata con successo nell'url {url}.")
        self.logger.debug(f"Il numero di link estrapolati della pagina {url} sono: {len(product_links)}")

        products_fetch_tasks = [asyncio.create_task(product) for product in product_links]

        products = await asyncio.gather(*products_fetch_tasks)

        return products

    async def fetchProduct(self, product_url : str):
        product_ent = await Product.find(product_url)

        if product_ent and not product_ent.isExpired(15):
            return

        product_info = {
            "name" : ["#productTitle"],
            "price" : ["#apex_desktop span.a-price .a-offscreen", "#price"],
            "description" : ["#feature-bullets ul", "#bookDescription_feature_div"],
            "reviews_summary" : ['.AverageCustomerReviews span[data-hook="rating-out-of-text"]']
        }



    async def startFetch(self, pages : List[str]):
        async with aiohttp.ClientSession(headers=self.getHeaders()) as session:
            self.logger.info("Sto creando le varie task")

            pages_task = [asyncio.create_task(session.get(page)) for page in pages]

            self.logger.info("Attendo le varie task")
            results = await asyncio.gather(*pages_task)
            self.logger.info("Finite le varie task")

            products_fetch_req = [asyncio.create_task(self.extractFromPage(res)) for res in results]

            products = await asyncio.gather(*products_fetch_req)
            print(products)

        print("LEL, funziona!")