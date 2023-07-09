import glob

from typing import List

from importlib import import_module
from inspect import isabstract

from source.utils.Logger import Logger

from concurrent.futures import ThreadPoolExecutor
from source.crawlers.scrapers.Scraper import Scraper

# from tests.Test import TestSuite

from threading import Thread

class CrawlerMode:
    SEARCH = 1
    FETCH_URL = 2

class Crawler(Thread):
    def __init__(self,
                 name, 
                 queue,
                 excluded_classes = [
                    # "source.crawlers.scrapers.AmazonScraper",
                    # "source.crawlers.scrapers.EbayScraper"
                 ],
                 mode: CrawlerMode = CrawlerMode.SEARCH,
                ) -> None:

        # Impostazione del logger ROOT ad un ascolto di qualsiasi tipologia di logger.
        self.logger = Logger.createLogger(name)

        self.scrapers : List[Scraper] = []
        
        self.queue = queue
        self.excluded_classes = excluded_classes
        
        self.mode = mode        

        self.loadScrapers()
        
        Thread.__init__(self, daemon=True)


    def loadScrapers(self):
        # Per ogni file contenuto all'interno della cartella "scrapers", seleziona tutti i file py
        for fname in glob.glob("./source/**/scrapers/*.py", recursive=True):
            # Costruisco il percorso per importare il modulo
            class_name_string = fname.replace(".py", "") \
                                     .replace("\\", ".") \
                                     .replace("/", ".") \
                                     .strip(".")

            # Importo il modulo
            module = import_module(class_name_string)

            # Prelevo la classe dal modulo e la istanzio se non è astratta
            scraper = getattr(module, class_name_string.split(".")[-1])

            # Se non è una classe astratta
            if  not isabstract(scraper) and \
                "__" not in fname and \
                class_name_string not in self.excluded_classes:
                class_instance : Scraper  = scraper(self.logger)
                self.scrapers.append(class_instance)

    def run(self):
        while True:
            item = self.queue.get()
            
            with ThreadPoolExecutor(2) as worker:
                for scraper in self.scrapers:
                    if self.mode == CrawlerMode.SEARCH:
                        worker.submit(scraper.search, item["text"])
                    elif self.mode == CrawlerMode.FETCH_URL and scraper.base_url in item["url"]:
                        if scraper.base_url in item["url"]:
                            worker.submit(scraper.extractProduct, item)