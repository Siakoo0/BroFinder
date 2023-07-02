from queue import Queue
from json import loads

from source.utils.Logger import Logger


class QSubscriber:
    def __init__(self, topic, queue = Queue()) -> None:
        
        self.topic = topic
        self.name = self.topic.replace("_", " ")\
                              .replace("/", "")\
                              .title()\
                              .replace(" ", "")
        
        self.logger = Logger.createLogger(f"{self.name}Subscriber")
        
        self.__queue = queue
        
    def setQueue(self, queue):
        self.logger.debug("Impossibile cambiare la coda inizializzata dal subscriber")
    
    def getQueue(self):
        return self.__queue
        
    def produce(self, message):
        self.logger.debug("Ricezione di un messaggio nel canale: {}, caricamento".format(self.topic, message))
        
        self.__queue.put(loads(message["data"]))
        