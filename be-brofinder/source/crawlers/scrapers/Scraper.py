from abc import ABC, abstractmethod
from typing import List
from requests import get

from source.utils.UserAgentGenerator import UserAgentGenerator
from source.crawlers.entities.Product import Product

from selenium import webdriver
from selenium.webdriver import Chrome
from urllib.parse import urlencode

from source.utils.Logger import Logger

class Scraper(ABC):
    logger = Logger.createLogger("ScraperLogger")

    @abstractmethod
    async def search(self, product: str) -> List[Product]:
        pass

    @property
    @abstractmethod
    def base_url(self):
        pass

    def prepareSearchURL(self, url : str, params : List[str]):
        return f"{url}?{urlencode(params)}"

    def user_agent(self):
        return UserAgentGenerator.generate()

    def request(self, url, headers={}):
        __headers = headers | {
            'User-Agent': self.user_agent()
        }

        return get(url, headers=__headers)

    def getChromeInstance(self) -> Chrome:
        user_agent = self.user_agent()

        options = webdriver.ChromeOptions()
        # options.add_argument("--headless=new")
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")
        options.add_argument("--log-level=3")

        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        driver : Chrome = webdriver.Chrome(options=options, executable_path="tools")
        return driver
