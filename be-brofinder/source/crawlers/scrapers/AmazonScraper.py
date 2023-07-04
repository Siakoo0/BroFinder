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

from timeit import timeit


import uuid

class AmazonScraper(Scraper):
    """
        AmazonScraper, modulo per fare lo Scraping dei prodotti di
    """

    @property
    def base_url(self):
        return "https://www.amazon.it"

    def search(self, k_product):
        params : dict = {"k" : k_product}
        
        url : str = self.prepareSearchURL(self.base_url + "/s", params)

        urls = [f"{url}&page={num}" for num in range(2, 4)]
        urls.insert(0, url)
        
        with ThreadPoolExecutor(len(urls)) as workers:
            pages = workers.map(self.getPageSource, urls)
            pages = list(pages)
            
            products_links = workers.map(self.extractFromPage, pages)
            products_links = [item for items in list(products_links) for item in items]
            
        with ThreadPoolExecutor(min(15, len(products_links))) as workers:
            product_pages = workers.map(self.getPageSource, products_links)
            product_pages = list(product_pages)
            
            for product in product_pages:
                workers.submit(self.scrapeProduct, product, k_product)
        
    def extractFromPage(self, page):
        url, response = page
        fetched = False  
        sleep_time = 0
        
        while not fetched and sleep_time < 10:
            bs : BeautifulSoup = BeautifulSoup(response, "html.parser")

            product_links : ResultSet[Tag] = bs.select('[data-component-type="s-search-results"] [data-asin]:not([data-asin=""]) h2 a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal[href*="/dp/"]')

            product_links : List[str] = [self.base_url + product.get("href").split("/ref")[0] for product in product_links]

            self.logger.info(f"Estrapolazione link completata con successo nell'url {url}, trovati {len(product_links)}.")

            fetched = len(product_links) > 0

            if not fetched:
                sleep_time+=5
                time.sleep(sleep_time)
                response = self.getPageSource(url)

        if not fetched: return ()
        
        return product_links
    
    def extractProduct(self, data):
        product_ent = Product.get(data["url"])
        
        if product_ent is not None and not product_ent.isExpired():
            return
   
        self.scrapeProduct(self.getPageSource(data["url"]), data["data"][0]["keyword"]) 
        
        
        self.logger.info(f"Estrazione del prodotto completata.")
    
    def scrapeProduct(self, product_page, keyword):
        url, source = product_page
        
        product_ent = Product.get(url)
        
        if product_ent is not None and not product_ent.isExpired():
            return
        
        self.logger.info("Inizio fetching prodotto {}".format(url))
        source = BeautifulSoup(source, "html.parser")

        product_info = {
            "url" : url,
            "keyword": keyword,
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
                        product_info[key] = None

        def getReviewsSource(url):
            self.logger.info(f"Preparazione URL per fetching Recensioni del prodotto {url}")
            reviews_url = re.sub("\/dp\/", "/product-reviews/", url)
            
            url, page_source = self.getPageSource(reviews_url)
            source = BeautifulSoup(page_source, "html.parser")
            
            reviews_elems = source.select('[data-hook="review"]')
            has_reviews = len(reviews_elems) > 0

            if not has_reviews: 
                return

            self.logger.info("Per l'URL {} ho trovato {} recensioni".format(url, len(reviews_elems)))

            with ThreadPoolExecutor(10) as pool:
                reviews = pool.map(extractReview, reviews_elems)
                reviews = list(reviews)
                
            for review in reviews: product_info["reviews"].append(Review(**review))
                
        def extractReview(rev):
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

            return review_dict
            
        with ThreadPoolExecutor(max_workers=10) as pool:
            pool.submit(extractData)
            pool.submit(extractImages)
            pool.submit(getReviewsSource, url)
            
        try:
            product_info["reviews_summary"] = product_info["reviews_summary"].replace(" su ", "/")
        except:
            product_info["reviews_summary"] = None
            
        try:
            product_info["price"] = float(product_info["price"].strip("€").replace(",", ".")) 
        except:
            product_info["price"] = None
            
        prod = Product(**product_info)
        prod.save()
        
        self.logger.debug(f"Terminata la fase di fetching del prodotto {product_info['url']}")