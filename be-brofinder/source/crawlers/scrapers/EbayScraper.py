from typing import List
from bs4 import BeautifulSoup, ResultSet, Tag
from pprint import pprint

from concurrent.futures import ThreadPoolExecutor

from source.crawlers.entities.Product import Product
from source.crawlers.scrapers.Scraper import Scraper
from source.crawlers.entities.Review import Review

from urllib.parse import urlencode

import uuid
from json import dump
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
        
        pages = self._fetchPages(response, 4)

        #Array che conterra tutti i prodotti
        products = []
        
        #in ogni pagine estrapola tutti i prodotti e le reccoglie nell'array sopra dichiarato
        with ThreadPoolExecutor(5) as pool:#classe che permette di utilizzare i Thread dalla pool
            for page in pages:
                pool.submit(self.extractFromPage, page, products)
                return
                 
        with open("result.json", "w+", encoding="utf-8") as file:
            dump(products, file)
        print("Risultato stampato!")
        
        
    #Funzione che estrapola gli elementi
    def extractFromPage(self, url, products : List[Product]):
        self.logger.info(f"Inizio il fetching dei prodotti dalla pagina {url}")
        
        response = self.request(url)
        soup : BeautifulSoup = BeautifulSoup(response.text, 'html.parser')
        
        product_links : ResultSet[Tag] = soup.select('.srp-river-results .clearfix .s-item__link')
        
        product_links : List[str] = [product.get("href").split("?")[0] for product in product_links]
        
        self.logger.info(f"Estrapolazione link completata con successo nell'url {url}.")
        self.logger.debug(f"Il numero di link estrapolati della pagina {url} sono: {len(product_links)}")
        
        products_list : List[Product] = []
        
        product_links = product_links[:2]
        print(product_links)
        for product in product_links:
            with ThreadPoolExecutor(10) as pool:
                pool.submit(self.extractInfoProduct, product, products_list)
                
        file = f".test_files/success/{uuid.uuid4()}.json"
    
        with open(file, "w+", encoding="utf-8") as fp:
            dump(products_list, fp)

        self.logger.info(f'Terminato il fetching dei prodotti, salvataggio dei risultati nel file: {file}')
        
        products.append(products_list)
        
    def extractInfoProduct(self, product_url : str, product_list : list):
        print(f"Inizio fetching del prodotto {product_url}")
        
        page = self.request(product_url)
        soup = BeautifulSoup(page.text, "html.parser")
        
        
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
            
        
        descr_prod_1 = soup.select_one('.ux-expandable-textual-display-block-inline.hide span span.ux-textspans')
        if descr_prod_1 is not None:
            descr_prod_1 = descr_prod_1.text.strip()
        else:
            descr_prod_1 = soup.select_one('#ABOUT_THIS_ITEM0-0-1-5\[1\[0\]\]-7\[0\[\@condition-0\]\]-18-1-ux-infotip-overlay > span.infotip__mask > span > span > div > span').text.strip()
            
        descr_prod = soup.select('.x-about-this-item .ux-labels-values__values')[1:]      
        descr_prod_2 = []
        
        for prod in descr_prod:
            if prod.text == "Non applicabile":
               prod.text.replace('Non applicabile', '')
            else: 
                descr_prod_2.append(prod.text)
        
        description_prod = descr_prod_1 + " " + ", ".join(descr_prod_2)
        
        product_info["description"] = description_prod
        product_info["url"] = product_url
        
        product_list.append(product_info)
        
        with ThreadPoolExecutor(3) as pool:
            pool.submit(extractReviews, page.text)
            pool.submit(extractImages, page.text)
            pass
        
        
        def extractReviews(source: BeautifulSoup, reviews : list):
            
            soup = BeautifulSoup(source, 'html.parser')
            
            review_page = soup.select_one('#STORE_INFORMATION0-0-51-43-10-tabpanel-0 > div > div > a').get('href')
            response = self.request(review_page)
            bs = BeautifulSoup(response.text, 'html.parser')
            
            pages = self._fetchPages(response, 5)
            
            for page in pages:
                response = self.request(page)
                bs = BeautifulSoup(response.text, 'html.parser')
                reviews_elem = bs.select('#feedback-cards > tbody > tr')
                i = 1 
                for rev in reviews_elem:
                    review_dict = {
                        "text": rev.select_one('.card__comment span').text.strip(),
                        "vote": None,
                        "media": [],
                        "date": rev.select_one(f'#feedback-cards > tbody > tr:nth-child({i}) > td:nth-child(3) > div:nth-child(1) > span')
                    }
                    i += 1

            reviews.append(Review(**review_dict))
            
            
        def extractImages(source):
            pass
        
        
    
    def _fetchPages(self, response, count):
        soup = BeautifulSoup(response.text, "html.parser")
        page_links = [a.get("href") for a in soup.select('.pagination__item')]
        
        if len(page_links) >= count:
            return page_links[:count] #Limita a tot. elementi
        else:
            return page_links
        
        
        
    
    
    
    
    
