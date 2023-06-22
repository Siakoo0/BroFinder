import asyncio
import time
import aiohttp, re

from json import loads
from time import sleep
from bs4 import BeautifulSoup, ResultSet, Tag
from typing import List

from concurrent.futures import ThreadPoolExecutor

from uuid import uuid4

from source.crawlers.scrapers.Scraper import Scraper
import json

from source.crawlers.entities.Product import Product
from source.crawlers.entities.Review import Review

from pyppeteer import launch

class AmazonScraper(Scraper):
    """
        AmazonScraper, modulo per fare lo Scraping dei prodotti di
    """

    @property
    def base_url(self):
        return "https://www.amazon.it"

    def request(self, url, headers : dict = {}):
        headers = self.getHeaders()

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

        loop = asyncio.new_event_loop()

        loop.run_until_complete(self.startFetch(url))

        loop.close()

        end = time.time()

        print("Tempo impiegato: {}s".format(end - start))

    def getHeaders(self):
        return {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'User-Agent': self.user_agent(),
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
        }

    def extractFromPage(self, response, url):
        async def getProductsSource(prods : List[str]):
            async with aiohttp.ClientSession(headers=self.getHeaders()) as req:
                prods_task = [asyncio.create_task(req.get(prod)) for prod in prods]

                prods_result = await asyncio.gather(*prods_task)

                prods_source = [(await prod.text(), str(prod.url))for prod in prods_result]

            return prods_source

        bs : BeautifulSoup = BeautifulSoup(response, "html.parser")

        product_links : ResultSet[Tag] = bs.select('[data-component-type="s-search-results"] [data-asin]:not([data-asin=""]) h2 a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal[href*="/dp/"]')

        product_links : List[str] = [self.base_url + product.get("href").split("/ref")[0] for product in product_links]

        self.logger.info(f"Estrapolazione link completata con successo nell'url {url}.")
        self.logger.debug(f"Il numero di link estrapolati della pagina {url} sono: {len(product_links)}")

        # Avvio del loop Async

        loop = asyncio.new_event_loop()
        products_source = loop.run_until_complete(getProductsSource(product_links))
        loop.close()

        results = []

        with ThreadPoolExecutor(10) as pool:
            for product in products_source:
                pool.submit(self.fetchProduct, results, *product)
                return

    def fetchProduct(self, products : list, source_page : str, url : str):
        async def getReviewsSource():
            reviews_url = re.sub("\/dp\/", "/product-reviews/", url)

            self.logger.info(f"Preparazione URL per fetching Recensioni del prodotto {url}")

            reviews_list = [self.prepareSearchURL(reviews_url, {"pageNumber" : page}) for page in range(1,6)]

            print(reviews_list)

            async with aiohttp.ClientSession(headers=self.getHeaders()) as session:
                reviews_task = [
                    asyncio.create_task(session.get(url)) for url in reviews_list
                ]

                pages = await asyncio.gather(*reviews_task)
                pages = [(await page.text(), str(page.url)) for page in pages]

            return pages

        self.logger.info("Inizio fetching prodotto {}".format(url))

        source = BeautifulSoup(source_page, "html.parser")
        product_ent = Product.find(url)

        if product_ent is not None and not product_ent.isExpired(15):
            return

        product_info = {
            "url" : url,
            "reviews" : []
        }

        info_selector = {
            "name" : ["#productTitle"],
            "price" : ["#apex_desktop span.a-price .a-offscreen", "#price"],
            "description" : ["#feature-bullets ul", "#bookDescription_feature_div"],
            "reviews_summary" : ['.AverageCustomerReviews span[data-hook="rating-out-of-text"]']
        }

        def extractData():
            for key in info_selector.keys():
                possible_tags = info_selector[key]
                foundBool = False

                for selector in possible_tags:
                    product_info[key] : Tag = source.select_one(selector)

                    if product_info[key]:
                        foundBool = True
                        product_info[key] : str = product_info[key].text.strip()
                        product_info[key] = re.sub(' +', ' ', product_info[key])
                        break

                    if not foundBool:
                        product_info[key] = ""

        def extractImages():
            checkScriptTag = lambda elem: 'm.media-amazon.com/images' in elem.text

            images_tag_script = list(filter(checkScriptTag, source.select("#imageBlock_feature_div script")))

            if images_tag_script:
                images_tag_script = images_tag_script[0].text

                # Prelevo le immagini del prodotto, qualsiasi dimensione
                text = images_tag_script.split("var data = ")[1].split(";")[0].replace("'", "\"").split("\"colorImages\": ")[1].split('"colorToAsin"')[0].strip().rstrip(",")

                product_info["images"] = [img["hiRes"] for img in loads(text)["initial"] if img is not None]
            else:
                product_info["images"] = []

        def extractReviews(rev_page, url, reviews : list):
            source = BeautifulSoup(rev_page, "html.parser")
            reviews_elems = source.select('[data-hook="review"]')

            has_reviews = len(reviews_elems) > 0

            if not has_reviews: return

            self.logger.info("Per l'URL {} ho trovato {} recensioni".format(url, len(reviews_elems)))

            for rev in reviews_elems:
                regex_vote = re.compile("^a-star-[1-5]$")

                vote_html_elem = rev.select_one(".a-icon-star").get("class")
                vote = list(filter(regex_vote.match, vote_html_elem))[0].split("-")[-1]

                review_dict = {
                    "text" : rev.select_one(".review-text").getText().strip().strip("\n"),
                    "vote" : int(vote),
                    "media" : [
                        image.get("src").replace("_SY88", "_SL1600_") for image in rev.select('.review-image-tile')
                    ],
                    "date" : rev.select_one('[data-hook="review-date"]').getText().split(" il ")[-1].strip().strip("\n")
                }

                reviews.append(Review(**review_dict))

        loop = asyncio.new_event_loop()
        reviews = loop.run_until_complete(getReviewsSource())
        loop.close()

        with ThreadPoolExecutor(max_workers=10) as pool:
            pool.submit(extractData)
            pool.submit(extractImages)
            print(len( reviews))
            for review in reviews:
                pool.submit(extractReviews, *review, product_info["reviews"])

        products.append(Product(**product_info, forceCreate=True))

    async def startFetch(self, url):
        browser = await launch()
        page = await browser.newPage()
        await page.goto(url)

        self.logger.info("Avvio dell'attività di fetching delle pagine Amazon.")

        source = await page.content()
        print(source)

        self.__fetchPages(source, url)

        return

        async with aiohttp.ClientSession(headers=self.getHeaders()) as session:
            self.logger.info(msg="Generazione delle richieste associate alle pagine.")

            pages_task = [asyncio.create_task(session.get(page)) for page in pages]
            results = await asyncio.gather(*pages_task)

            self.logger.info("Richieste eseguite, conversione in sorgente html.")

            pages = [(await page.text(), str(page.url)) for page in results]

        self.logger.info("Terminata conversione, inizio analisi ed estrapolazione delle pagine.")

        with ThreadPoolExecutor(5) as pool:
            for page in pages:
                pool.submit(self.extractFromPage, *page)
                return