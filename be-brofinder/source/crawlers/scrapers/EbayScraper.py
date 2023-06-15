from typing import List
import bs4, requests, re
from pprint import pprint

from selenium.webdriver import Chrome

from source.crawlers.entities.Product import Product
from source.crawlers.scrapers.Scraper import Scraper

from urllib.parse import urlencode

class EbayScraper(Scraper):
    @property
    def base_url(self):
        return "https://www.ebay.it/sch/i.html"
    
    def search(self, product: str) -> List[Product]:
        
        driver : Chrome = self.getChromeInstance()
        
        params : dict = {"_nkw" : product}
        url : str = "{}?{}".format(self.base_url, urlencode(params))
        driver.get(url)
        
        response = driver.page_source
        soup = bs4.BeautifulSoup(response, 'html.parser') #questa funzione estrapola il testo della risposta ottenuta che sarà in formato html
        
        
        
        
        
        
        
        
        pass