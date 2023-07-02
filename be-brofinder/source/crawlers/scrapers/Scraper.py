from abc import ABC, abstractmethod
from typing import List
from requests import get

from source.utils.UserAgentGenerator import UserAgentGenerator
from source.database.mongodb.entities.Product import Product

from selenium import webdriver
from selenium.webdriver import Chrome
from urllib.parse import urlencode

from source.utils.Logger import Logger

class Scraper(ABC):
    @abstractmethod
    async def search(self, product: str) -> List[Product]:
        pass

    @property
    @abstractmethod
    def base_url(self):
        pass

    def __init__(self, logger) -> None:
        self.logger = logger

    def prepareSearchURL(self, url : str, params : dict):
        return f"{url}?{urlencode(params)}"

    def user_agent(self):
        return UserAgentGenerator.generate()

    def request(self, url, headers={}):
        __headers = headers | {
            'User-Agent': self.user_agent()
        }

        return get(url, headers=__headers)

    def getChromeInstance(self) -> Chrome:
        options = webdriver.ChromeOptions()
        
        options.add_argument("--headless=new")
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")
        options.add_argument("--log-level=3")

        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        driver : Chrome = webdriver.Chrome(options=options)
        return driver
