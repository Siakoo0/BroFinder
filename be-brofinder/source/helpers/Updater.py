from threading import Thread
from queue import Queue
from datetime import datetime, timedelta

from source.database.mongodb.entities.Product import Product, ProductParams
from source.utils.Logger import Logger

import time

class Updater(Thread):
    def __init__(self, queue : Queue) -> None:
        self.queue = queue
        self.logger = Logger.createLogger("ProductUpdater")
        Thread.__init__(self, daemon=True)
        
    def run(self):
        while True:
            self.logger.debug(f"Prendo tutti i prodotti scaduti da oltre {ProductParams.EXPIRATION_TIME} minuti.")
            expire_date = datetime.now() - timedelta(minutes=ProductParams.EXPIRATION_TIME)
            
            prods = Product.getAll(
                {
                    "updated_at" : {"$lt" : expire_date}
                }
            )[:75]
            
            # Limito il numero di risultati a 25 in maniera da partizionare il lavoro a turni
            
            for prod in prods:
                prod_ent = Product.get(prod["url"])
                prod["scheduled_fetch"] = True
                prod_ent.update(prod)
                
                self.queue.put(prod)
                
                self.logger.debug("Il prodotto {} è stato schedulato per l'aggiornamento.".format(prod["url"]))
                
                
            self.logger.debug("Ripresa tra 5 minuti dell'aggiornamento dei prodotti.")
            time.sleep(60*5)
            
            
            