from typing import List

from selenium.webdriver import Chrome
from bs4 import BeautifulSoup, ResultSet, Tag
from urllib.parse import urlencode
from json import loads

import requests

from concurrent.futures import ThreadPoolExecutor
from queue import Queue

from source.crawlers.entities.Product import Product
from source.crawlers.scrapers.Scraper import Scraper
import uuid

import logging
import threading

from source.crawlers.utils.Logger import Logger

class AmazonScraper(Scraper):
    @property
    def base_url(self):
        return "https://www.amazon.it"

    def request(self, url, headers={}):
        headers = headers | {
            'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7'
        }

        return super().request(url, headers)

    def search(self, product: str) -> List[Product]:
        params : dict = {"k" : product}
        url : str = "{}/s?{}".format(self.base_url, urlencode(params))

        req = self.request(url)

        pages = self._fetchPages(req.text, url)

        # Per ogni pagina estrapola tutti i prodotti e le raccogli in un vettore.
        futures = []

        with ThreadPoolExecutor(10) as pool:
            for page in pages:
                print("Submite page: ", page)
                futures.append(pool.submit(self.extractFromPage, page))

        products = []

        for future in futures:
            products += future.result()

        with open("result.json", "w+", encoding="utf-8") as file:
            file.write(products)

        print("Risultato stampato!")

    # Funzione che estrapola gli elementi
    def extractFromPage(self, url):
        thread_name = threading.current_thread().name

        response = self.request(url)
        bs : BeautifulSoup = BeautifulSoup(response.text, "html.parser")

        product_links : ResultSet[Tag] = bs.select('[data-component-type="s-search-results"] [data-asin]:not([data-asin=""]) a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal[href*="/dp/"]')
        
        product_links : List[str] = [self.base_url + product.get("href").split("/ref")[0] for product in product_links]
    
        # Tolgo di mezzo i siti ripetuti derivata dalla ricerca del crawler
        product_links = list(dict.fromkeys(product_links))
        
        products : List[Product] = []

        for product in product_links:
            self.logger.debug(f'Thread {thread_name} sta effettuando il fetching del prodotto: {product}')
            
            self.extractInfoProduct(product, products)
        
        print("Prodotti terminati: ", products)

        return products

    def _fetchPages(self, response, base_url):
        bs = BeautifulSoup(response, "html.parser")
        last_page = bs.select_one(".s-pagination-item.s-pagination-ellipsis + .s-pagination-item.s-pagination-disabled").getText()

        return [f"{base_url}&page={num}" for num in range(1, int(last_page)+1)]

    def extractInfoProduct(self, product_url : str, product_list : list):
        chrome = self.getChromeInstance()
        chrome.get(product_url)

        bs = BeautifulSoup(chrome.page_source, "html.parser")
        chrome.quit()

        product_info = {
            "name" : ["#productTitle"],
            "price" : ["span.a-price", "#price"],
            "description" : ["#feature-bullets", "#bookDescription_feature_div"]
        }

        for key, possibleTags in product_info.items():
            foundBool = False
            
            for selector in possibleTags:
                product_info[key] : Tag = bs.select_one(selector)
                
                if product_info[key]:
                    foundBool = True
                    product_info[key] : Tag = product_info[key].text
                    break
            
            if not foundBool:
                product_info[key] = ""

        product_info["url"] = product_url
        product_info["reviews"] = []
        

        product_list.append(product_info)

        # try:
            
        #     #feature-bullets o #bookDescription_feature_div

        #     images_tag_script = bs.select_one("#imageBlock_feature_div > script:nth-child(3)")

        #     if images_tag_script:
        #         images_tag_script = images_tag_script.text
                
        #         # Prelevo le immagini del prodotto, qualsiasi dimensione
        #         text = images_tag_script.split("var data = ")[1].split(";")[0].replace("'", "\"").split("\"colorImages\": ")[1].split('"colorToAsin"')[0].strip().rstrip(",")

        #         product_info["images"] = [img["hiRes"] for img in loads(text)["initial"]]
        #     else:
        #         product_info["images"] = []




        # except Exception as e:
        #     errors[product_url] = str(e)

        

