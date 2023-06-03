from typing import List

from source.crawler.entities.Product import Product
from source.crawler.scrapers.Scraper import Scraper

from requests import request, Response, Session
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from urllib.parse import urlencode

class AmazonScraper(Scraper):
    _uri = "https://www.amazon.it/s?"
    
    def search(self, product: str) -> List[Product]:
        options : Options = Options()
        # options.add_argument("--headless")
        driver : Chrome = webdriver.Chrome(options=options, executable_path="tools")
        params = {"k" : product}
        driver.get(AmazonScraper._uri + urlencode(params))
        input()
        response : str = driver.page_source

        with open("file.html", "w+", encoding="utf-8") as f:
            f.write(response)
            
        bs = BeautifulSoup(response, "html.parser")
        print(bs)
        pass