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
            expire_date = datetime.now() - timedelta(minutes=ProductParams.EXPIRATION_TIME)
            
            prods = Product.getAll(
                {
                    "scheduled_update" : {"$eq" : None},
                    "updated_at" : {"$lt" : expire_date}
                }
            )[:25]
            
            # Limito il numero di risultati a 25 in maniera da partizionare il lavoro a turni
            # BUG CREA DUPLICATI
            
            for prod in prods:
                prod_ent = Product.get(prod["url"])
                prod_ent.setScheduledUpdate(True)
                
                self.queue.put(prod_ent.convert())
                
                self.logger.debug("Il prodotto {} è stato schedulato per l'aggiornamento.".format(prod["url"]))
                
                
            time.sleep(60*10)
            
            self.logger.debug("Ripresa tra 5 minuti dell'aggiornamento dei prodotti.")
            
            