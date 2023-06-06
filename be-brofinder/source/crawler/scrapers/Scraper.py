from abc import ABC, abstractmethod
from typing import List
from requests import request

from source.crawler.helpers.UserAgentGenerator import UserAgentGenerator

from source.crawler.entities.Product import Product

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

class Scraper(ABC):
    @abstractmethod
    def search(self, product: str) -> List[Product]:
        pass

    @property
    @abstractmethod
    def base_url(self):
        pass

    def user_agent(self):
        return UserAgentGenerator.generate() 

    def getChromeInstance(self) -> Chrome:
        user_agent = self.user_agent()

        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument(f"--user-agent={user_agent}")
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")

        driver : Chrome = webdriver.Chrome(options=options, executable_path="tools")
        return driver


    # def makeRequest(self, url, method="get", params={}, options={}):
    #     headers : dict = {
    #         "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    #     } | options
        
    #     return  request(
    #         method=method, 
    #         url=url, 
    #         params=params, 
    #         headers=headers
    #     )
