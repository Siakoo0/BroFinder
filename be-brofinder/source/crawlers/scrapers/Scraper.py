from abc import ABC, abstractmethod
from typing import List
from requests import request

from source.crawlers.helpers.UserAgentGenerator import UserAgentGenerator

from source.crawlers.entities.Product import Product

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service

from webdriver_manager.chrome import ChromeDriverManager


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
