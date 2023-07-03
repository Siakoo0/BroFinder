import asyncio
import time
import aiohttp, re

from json import loads
from time import sleep
from bs4 import BeautifulSoup, ResultSet, Tag
from typing import List

from concurrent.futures import ThreadPoolExecutor

from source.crawlers.scrapers.Scraper import Scraper

from random import randint
from source.database.mongodb.entities.Product import Product
from source.database.mongodb.entities.Review import Review


class AmazonScraper(Scraper):
    """
        AmazonScraper, modulo per fare lo Scraping dei prodotti di
    """

    @property
    def base_url(self):
        return "https://www.amazon.it"

    def request(self, url, headers : dict = {}):
        headers = self.getHeaders() | headers

        return super().request(url, headers)

    def __fetchPages(self, response, base_url):
        bs = BeautifulSoup(response, "html.parser")
        last_page = bs.select(".s-pagination-item")[-2].getText()

        last_page = min(5, int(last_page)+1)

        return [f"{base_url}&page={num}" for num in range(1, last_page)]

    def search(self, product) -> str:
        start = time.time()
        
        # Da migliorare la search
        
        loop = asyncio.new_event_loop()

        loop.run_until_complete(self.startFetch(product))

        loop.close()

        end = time.time()

        print("Tempo impiegato: {}s".format(end - start))

    def getHeaders(self):
        headers = {
            'User-Agent': self.user_agent(),
            'Accept-Language': 'en-US, en;q=0.5'
        }
        return headers

    def extractFromPage(self, response, url, search_text):
        async def getProductsSource(prods : List[str]):
            async with aiohttp.ClientSession(headers=self.getHeaders()) as req:
                prods_task = [asyncio.create_task(req.get(prod)) for prod in prods]

                prods_result = await asyncio.gather(*prods_task)

                prods_source = [(await prod.text(), str(prod.url), search_text)for prod in prods_result]

            return prods_source

        fetched = False  
        sleep_time = 0

        while not fetched and sleep_time < 5:
            bs : BeautifulSoup = BeautifulSoup(response, "html.parser")

            product_links : ResultSet[Tag] = bs.select('[data-component-type="s-search-results"] [data-asin]:not([data-asin=""]) h2 a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal[href*="/dp/"]')

            product_links : List[str] = [self.base_url + product.get("href").split("/ref")[0] for product in product_links]

            self.logger.info(f"Estrapolazione link completata con successo nell'url {url}, trovati {len(product_links)}.")

            fetched = len(product_links) > 0

            if not fetched:
                sleep_time+=5
                time.sleep(sleep_time)
                response = self.request(url).text

        if not fetched: return

        # Avvio del loop Async

        loop = asyncio.new_event_loop()
        products_source = loop.run_until_complete(getProductsSource(product_links))
        loop.close()

        results = []

        with ThreadPoolExecutor(10) as pool:
            for product in products_source:
                pool.submit(self.fetchProduct, results, *product)

    def fetchProduct(self, products : list, source_page : str, url : str, product_search):
        def getReviewsSource():
            reviews_url = re.sub("\/dp\/", "/product-reviews/", url)
            self.logger.info(f"Preparazione URL per fetching Recensioni del prodotto {url}")

            chrome = self.getChromeInstance()
            chrome.get(reviews_url)
            page = chrome.page_source
            try:
                chrome.close()            
            except:
                pass

            return page

        self.logger.info("Inizio fetching prodotto {}".format(url))

        source = BeautifulSoup(source_page, "html.parser")
        product_ent = Product.get(url)

        if product_ent is not None and not product_ent.isExpired(15):
            return

        product_info = {
            "url" : url,
            "reviews" : [],
            "images" : [],
            "keyword": product_search
        }

        info = {
            "url" : url,
            "reviews" : [],
            "images" : []
        }

        info_selector = {
            "name" : ["#productTitle"],
            # Price bug, se non trova nulla non può convertire
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
                        info[key] = re.sub(' +', ' ', product_info[key])
                        break

                    if not foundBool:
                        product_info[key] = ""
                        info[key] = ""

        def extractImages():
            checkScriptTag = lambda elem: 'm.media-amazon.com/images' in elem.text

            images_tag_script = list(filter(checkScriptTag, source.select("#imageBlock_feature_div script")))

            product_info["images"] = []
            if images_tag_script:
                images_tag_script = images_tag_script[0].text

                # Prelevo le immagini del prodotto, qualsiasi dimensione
                text = images_tag_script.split("var data = ")[1].split(";")[0].replace("'", "\"").split("\"colorImages\": ")[1].split('"colorToAsin"')[0].strip().rstrip(",")

                prior_to_extract = ["hiRes", "large", "main"]

                for img in loads(text)["initial"]:
                    key = "hiRes"
                    index_key = 0
                    while img[key] is None and index_key < len(prior_to_extract):
                        index_key+=1
                        key = prior_to_extract[index_key]

                    product_info["images"].append(img[key])
                    info["images"].append(img[key])

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
                info['reviews'].append(review_dict)
            
        review = getReviewsSource()

        with ThreadPoolExecutor(max_workers=10) as pool:
            pool.submit(extractData)
            pool.submit(extractImages)
            pool.submit(extractReviews, review, url, product_info["reviews"])

        product_info["price"] = float(product_info["price"].strip("€").replace(",", ".")) 

        prod = Product(**product_info)
        prod.save()
        
        products.append(prod)

    async def startFetch(self, product):
        params : dict = {"k" : product}
        url : str = self.prepareSearchURL(self.base_url + "/s", params)

        fetched = False

        while not fetched:
            try:
                pages = self.__fetchPages(self.getPageSource(url), url)
                fetched = True
            except:
                wait_time = randint(2, 4)
                self.logger.info(f"Fetching fallito, riprovo a fare la richiesta tra {wait_time} secondi.")
                time.sleep(wait_time)

        futures = []

        self.logger.info(msg="Generazione delle richieste associate alle pagine.")

        with ThreadPoolExecutor(4) as pool:
            for page in pages:
                futures.append(pool.submit(self.getPageSource, page))

        self.logger.info("Richieste eseguite, conversione in sorgente html.")

        pages = [(future.result(), url, product) for future in futures]

        self.logger.info("Terminata conversione, inizio analisi ed estrapolazione delle pagine.")

        with ThreadPoolExecutor(5) as pool:
            for page in pages:
                pool.submit(self.extractFromPage, *page)