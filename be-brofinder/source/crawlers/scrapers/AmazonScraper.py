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

class AmazonProduct:
    def __init__(self) -> None:
        pass

    def get():
        return

class AmazonScraper(Scraper):
    @property
    def base_url(self):
        return "https://www.amazon.it"

    def search(self, product: str) -> List[Product]:
        # First fetching of pages
        pages_queue = Queue(10)
        chrome : Chrome = self.getChromeInstance()
        
        params : dict = {"k" : product}
        url : str = "{}/s?{}".format(self.base_url, urlencode(params))
        pages_queue.put(url)
        chrome.get(url)

        print(self._fetchPages(url, chrome.page_source))
    
        # with ThreadPoolExecutor(10) as pool:
        #     while pages_queue.qsize() > 0:
        #         elem = pages_queue.get()
            

    def _fetchPages(self, url : str, respose):
        bs = BeautifulSoup(respose, "html.parser")
        return [a.get("href") for a in bs.select('div[role="navigation"] .s-pagination-strip a:not(span[aria-disabled=false] + a)')]



    #region extractInfoProduct
    #  def extractInfoProduct(self, product, product_list : list):
    #     user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        
    #     options = webdriver.ChromeOptions()
    #     options.add_argument("--headless=new")
    #     options.add_argument(f"--user-agent={user_agent}")
    #     options.add_argument('log-level=3') 
    #     options.add_argument('window-size=1920x1080')
    #     options.add_argument("disable-gpu")

    #     driver : Chrome = webdriver.Chrome(options=options, executable_path="tools")

    #     driver.get(product)
    #     bs = BeautifulSoup(driver.page_source, "html.parser")
    #     images_tag_script  : str = bs.select_one("#imageBlock_feature_div > script:nth-child(3)").text 
    #     # Prelevo le immagini del prodotto, qualsiasi dimensione

    #     text = images_tag_script.split("var data = ")[1].split(";")[0].replace("'", "\"").split("\"colorImages\": ")[1].split('"colorToAsin"')[0].strip().rstrip(",")

    #     product_info = {
    #         "images" : [img["hiRes"] for img in loads(text)["initial"]]
    #     }
        
    #     product_list.append(product_info)
    #endregion
    
    # region search
    # def search(self, product: str) -> List[Product]:
    #     user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"

    #     options = webdriver.ChromeOptions()
    #     options.add_argument("--headless=new")
    #     options.add_argument(f"--user-agent={user_agent}")
    #     options.add_argument('log-level=3') 
    #     options.add_argument('window-size=1920x1080')
    #     options.add_argument("disable-gpu")

    #     driver : Chrome = webdriver.Chrome(options=options, executable_path="tools")

    #     params : dict = {"k" : product}
    #     url : str = "{}/s?{}".format(self.base_url, urlencode(params))

    #     driver.get(url)

    #     response : str = driver.page_source 
        
    #     bs = BeautifulSoup(response, "html.parser")

    #     productTags : ResultSet[Tag] = bs.select('[data-component-type="s-search-results"] [data-asin]:not([data-asin=""]) a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal[href*="/dp/"]')

    #     products : List[str] = [self.base_url + product.get("href").split("/ref")[0] for product in productTags]

    #     # Tolgo di mezzo i siti ripetuti derivata dalla ricerca del crawler
    #     products = list(dict.fromkeys(products))

    #     product_list = []

    #     with ThreadPoolExecutor(max_workers=10) as pool:
    #         for product in products:
    #             pool.submit(self.extractInfoProduct, product, product_list)
        
    #     print(product_list)
    #endregion
