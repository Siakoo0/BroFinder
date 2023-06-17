from typing import List
from bs4 import BeautifulSoup, ResultSet, Tag
from pprint import pprint

from concurrent.futures import ThreadPoolExecutor

from source.crawlers.entities.Product import Product
from source.crawlers.scrapers.Scraper import Scraper

from urllib.parse import urlencode

import uuid
import json
import os

class EbayScraper(Scraper):
    
    @property
    def base_url(self):
        return "https://www.ebay.it/sch/i.html"
    
    def request(self, url, headers={}):
        headers = headers | {
            'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7'
        }

        return super().request(url, headers)
    
    def search(self, product: str) -> List[Product]:
        
        params : dict = {"_nkw" : product}
        url : str = "{}?{}".format(self.base_url, urlencode(params))
        
        response = self.request(url)
        
        pages = self._fetchPages(response)

        #Array che conterra tutti i prodotti
        products = []
        
        #in ogni pagine estrapola tutti i prodotti e le reccoglie nell'array sopra dichiarato
        with ThreadPoolExecutor(5) as pool:#classe che permette di utilizzare i Thread dalla pool
            for page in pages:
                pool.submit(self.extractFromPage, page, products)
                return
                
                
        with open("result.json", "w+", encoding="utf-8") as file:
            json.dump(products, file)
        print("Risultato stampato!")
        
        
        
    
    #Funzione che estrapola gli elementi
    def extractFromPage(self, url, products : List[Product]):
        # self.logger.info(f"Inizio il fetching dei prodotti dalla pagina {url}")
        
        response = self.request(url)
        soup : BeautifulSoup = BeautifulSoup(response.text, 'html.parser')
        
        product_links : ResultSet[Tag] = soup.select('.srp-river-results .clearfix .s-item__link')
        
        product_links : List[str] = [product.get("href").split("?")[0] for product in product_links]
        
        # self.logger.info(f"Estrapolazione link completata con successo nell'url {url}.")
        # self.logger.debug(f"Il numero di link estrapolati della pagina {url} sono: {len(product_links)}")
        
        products_list : List[Product] = []
        
        for product in product_links:
            with ThreadPoolExecutor(20) as pool:
                pool.submit(self.extractInfoProduct, product, products_list)
                return
                
        file = f".test_files/success/{uuid.uuid4()}.json"
    
        with open(file, "w+", encoding="utf-8") as fp:
            json.dump(products_list, fp)

        # self.logger.info(f'Terminato il fetching dei prodotti, salvataggio dei risultati nel file: {file}')
        
        products.append(products_list)
        
    def extractInfoProduct(self, product_url : str, product_list : list):
        # print(f"Inizio fetching del prodotto {product_url}")
        
        chrome = self.getChromeInstance()
        chrome.get(product_url)
        
        soup = BeautifulSoup(chrome.page_source, "html.parser")
        chrome.quit()
        
        descr_prod_1 = soup.select_one('.ux-expandable-textual-display-block-inline.hide span span.ux-textspans').text.strip()
        
        descr_prod = soup.select('.x-about-this-item .ux-labels-values__values')[1:]
        
        product_info = {
            "name" : [".x-item-title__mainTitle span"],
            "price" : [".x-price-primary span span.ux-textspans"]
        }
        
        for key, possibleTags in product_info.items():
            foundBool = False
            
            for selector in possibleTags:
                product_info[key] : Tag = soup.select_one(selector)
                
                if product_info[key]:
                    foundBool = True
                    product_info[key] : Tag = product_info[key].text.strip()
                    break
            
            if not foundBool:
                product_info[key] = ""
            
        descr_prod_2 = []
          
        for prod in descr_prod:
            descr_prod_2.append(prod.text)
        
        descr_prod = descr_prod_1 + " " + " ".join(descr_prod_2)
        product_info["description"] = descr_prod
        product_info["url"] = product_url
        product_info["reviews"] = []
        
        product_list.append(product_info)
        pprint(product_list)
        
    
    
    def _fetchPages(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        page_links = [a.get("href") for a in soup.select('.pagination__item')]
        
        if len(page_links) >= 1:
            return page_links[:1] #Limita a 4 elementi
        else:
            return page_links
    
    
    
    
    
