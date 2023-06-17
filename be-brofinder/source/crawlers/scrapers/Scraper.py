from abc import ABC, abstractmethod
from typing import List
from requests import get

from source.utils.UserAgentGenerator import UserAgentGenerator
from source.crawlers.entities.Product import Product

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from source.utils.Logger import Logger

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
    
    def request(self, url, headers={}):
        user_agent = self.user_agent()
        __headers = headers | {
            'User-Agent': user_agent
        }
        return get(url, headers=__headers)

    def getChromeInstance(self) -> Chrome:
        user_agent = self.user_agent()

        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument(f"--user-agent={user_agent}")
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")
        options.add_argument("--log-level=3")

        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        driver : Chrome = webdriver.Chrome(options=options, executable_path="tools")
        return driver
    
    @property
    def logger(self):
        try:
            return self._logger
        except AttributeError:
            self._logger = Logger.createLogger("ScraperLogger")
            return self._logger