from threading import Thread
from source.database.mongodb.entities.Product import Product


class Updater(Thread):
    def __init__(self, channel) -> None:
        self.channel = channel
        
        Thread.__init__(self, daemon=True)
        
    # def run(self):
    #     while True:
    #         prods = Product.getAll({""})