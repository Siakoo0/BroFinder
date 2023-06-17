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
import uuid

import logging
import threading
import json

class AmazonScraper(Scraper):
    pass