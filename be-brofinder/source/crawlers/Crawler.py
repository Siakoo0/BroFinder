"""
    Crawler.py
"""

import glob

from typing import List

from importlib import import_module
from inspect import isabstract

from source.utils.Logger import Logger

from concurrent.futures import ThreadPoolExecutor
from source.crawlers.scrapers.Scraper import Scraper

# from tests.Test import TestSuite

from threading import Thread

class Crawler(Thread):
    def __init__(self,
                 name, 
                 queue,
                 excluded_classes = [
                    # "source.crawlers.scrapers.AmazonScraper",
                    "source.crawlers.scrapers.EbayScraper"
                 ],
                ) -> None:

        # Impostazione del logger ROOT ad un ascolto di qualsiasi tipologia di logger.
        self.logger = Logger.createLogger(name)


        self.scrapers : List[Scraper] = []
        self.queue = queue
        self.excluded_classes = excluded_classes

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
            my_class = getattr(module, class_name_string.split(".")[-1])

            # Se non è una classe astratta
            if  not isabstract(my_class) and \
                "__" not in fname and \
                class_name_string not in self.excluded_classes:
                class_instance : Scraper  = my_class(self.logger)
                self.scrapers.append(class_instance)

    def run(self):
        while True:
            item = self.queue.get()
            self.logger.debug(f"Ho estratto l'elemento {item} da una coda con {self.queue.qsize()}")
            
            with ThreadPoolExecutor(len(self.scrapers)) as worker:
                for scraper in self.scrapers:
                    worker.submit(scraper.search, item)
