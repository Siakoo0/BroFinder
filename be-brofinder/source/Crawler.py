from source.utils.Singleton import Singleton
from source.crawlers.scrapers.Scraper import Scraper

from tests.Test import TestSuite

from importlib import import_module
from inspect import isabstract
from dotenv import load_dotenv

import glob
from typing import List

import logging

class Crawler(metaclass=Singleton):
    scrapers : List[Scraper] = []

    def __init__(self) -> None:
        # Classi da escludere durante il discovery degli Scrapers
        excluded_classes = [
            "source.crawlers.scrapers.AmazonScraper",
            "source.crawlers.scrapers.EbayScraper"
        ]

        # Impostazione del logger ROOT ad un ascolto di qualsiasi tipologia di logger.
        logging.getLogger().setLevel(logging.NOTSET)

        # Caricamento del file di configurazione
        load_dotenv(".env")

        # Per ogni file contenuto all'interno della cartella "scrapers", seleziona tutti i file python 
        for fname in glob.glob("./source/**/scrapers/*.py", recursive=True):
            # Costruisco il percorso per importare il modulo
            class_name_string = fname.replace(".py", "").replace("\\", ".").replace("/", ".").strip(".")
            
            # Importo il modulo
            module = import_module(class_name_string)

            # Prelevo la classe dal modulo e la istanzio se non è astratta
            my_class = getattr(module, class_name_string.split(".")[-1])
            
            # Se non è una classe astratta
            if not isabstract(my_class) and "__" not in fname and class_name_string not in excluded_classes:
                class_instance : Scraper  = my_class()
                Crawler.scrapers.append(class_instance)

    def start(self):
        try:
            # tests = TestSuite()
            # tests.run()
            
            for scraper in Crawler.scrapers:
                scraper.search("portatile")
            
        except Exception as e:
            print("Errore avvenuto all'interno del codice.", e)
