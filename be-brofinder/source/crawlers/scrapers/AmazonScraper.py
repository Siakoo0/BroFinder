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
import json

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
        products = []

        with ThreadPoolExecutor(5) as pool:
            for page in pages:
                pool.submit(self.extractFromPage, page, products)


        with open("result.json", "w+", encoding="utf-8") as file:
            json.dump(products, file)

        print("Risultato stampato!")

    # Funzione che estrapola gli elementi
    def extractFromPage(self, url, products : List[Product]):
        self.logger.info(f"Inizio il fetching dei prodotti dalla pagina {url}")

        response = self.request(url)
        bs : BeautifulSoup = BeautifulSoup(response.text, "html.parser")

        product_links : ResultSet[Tag] = bs.select('[data-component-type="s-search-results"] [data-asin]:not([data-asin=""]) a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal[href*="/dp/"]')
        
        product_links : List[str] = [self.base_url + product.get("href").split("/ref")[0] for product in product_links]
    
        # Tolgo di mezzo i siti ripetuti derivata dalla ricerca del crawler
        product_links = list(dict.fromkeys(product_links))

        self.logger.info(f"Estrapolazione link completata con successo nell'url {url}.")
        self.logger.debug(f"Il numero di link estrapolati della pagina {url} sono: {len(product_links)}")
        
        products_list : List[Product] = []

        for product in product_links:
            with ThreadPoolExecutor(20) as pool:
                pool.submit(self.extractInfoProduct, product, products_list)
        
        file = f".test_files/success/{uuid.uuid4()}.json" 

        with open(file, "w+", encoding="utf-8") as fp:
            json.dump(products_list, fp)

        self.logger.info(f'Terminato il fetching dei prodotti, salvataggio dei risultati nel file: {file}')

        products.append(products_list)

    def _fetchPages(self, response, base_url):
        bs = BeautifulSoup(response, "html.parser")
        last_page = bs.select_one(".s-pagination-item.s-pagination-ellipsis + .s-pagination-item.s-pagination-disabled").getText()

        return [f"{base_url}&page={num}" for num in range(1, int(last_page)+1)]

    def extractInfoProduct(self, product_url : str, product_list : list):
        self.logger.info(f'Inizio fetching del prodotto: {product_url}')
        
    #     product_list.append(product_info)
    #endregion
    
    #region search
    # def search(self, product: str) -> List[Product]:
    #     user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"

        for key, possibleTags in product_info.items():
            foundBool = False
            
            for selector in possibleTags:
                product_info[key] : Tag = bs.select_one(selector)
                
                if product_info[key]:
                    foundBool = True
                    product_info[key] : Tag = product_info[key].text.strip()
                    break
            
            if not foundBool:
                product_info[key] = ""

        product_info["url"] = product_url
        product_info["reviews"] = []
        
 
        product_list.append(product_info)
        self.logger.info(f'Fine fetching del prodotto: {product_url}')

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

        

