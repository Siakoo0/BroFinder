from source.helpers.Singleton import Singleton
from source.utils.Logger import Logger

from typing import List
from time import sleep

import redis
from threading import Thread

from source.database.redis.QSubscriber import QSubscriber

class RedisAgent(Thread, metaclass=Singleton):
    def __init__(self, host:str="localhost", port:int=6379, queues:dict={}) -> None:
        self.logger = Logger.createLogger("RedisAgent")
        
        self.host = host
        self.port = port
        
        self.redis = None
        
        self.pubsubs_active : List[redis.client.PubSub] = []
        self.config_pubsub_list = []
        
        self.queues = queues
        
        Thread.__init__(self, daemon=True)
        
    def run(self):
        while True:
            connected = self.redis is not None
            
            if not connected:
                self.logger.debug(f"Connessione al database Redis in corso..")
                self.redis = redis.Redis(
                    host=self.host,
                    port=self.port,
                    decode_responses=True
                )   
                
            try:
                if not connected: self.logger.debug(f"Tentativo di connessione a Redis in corso..")
                
                self.redis.ping()
                
                if not connected: 
                    self.logger.debug(f"Tentativo di connessione a Redis avvenuto con successo")
                    
                    self.logger.debug(f"Reset PubSub database Redis")
                    self.resetPubSub()                    
                    
                    self.logger.debug(f"Configurazione Queues database Redis")
                    self.bootstrapQueues(self.queues)
                    
            except Exception as e:
                self.logger.debug(f"Connessione con Redis caduta, eccezione: {str(e)}, riprovo tra 5 secondi.")
                self.redis = None
                
            sleep(2)
                
    def resetConnection(self, exception, pubsub, thread):
        if self.redis is not None:
            try : self.redis.close()
            except: pass
        
        self.redis = None
        
    def addPubSub(self, pubsub):
        self.config_pubsub_list.append(pubsub)
        self.register_pubsub(pubsub) 
        
    def addQueueSubscriber(self, queue_subscriber : QSubscriber):
        channel = queue_subscriber.topic
        
        self.addPubSub({
            channel : queue_subscriber.produce    
        })

    def bootstrapQueues(self, topics : dict):
        queues = {}
        
        for topic, queue in topics.items():
            qsub = QSubscriber(topic, queue)
            self.addQueueSubscriber(queue_subscriber=qsub)
            queues[qsub.name] = qsub.getQueue()
            
        return queues
        
    def resetPubSub(self):
        for pubsub in self.pubsubs_active:
            pubsub["thread"].stop()
        self.pubsubs_active = []
         
    def register_pubsub(self, subscribe):
        
        pubsub = self.redis.pubsub()
        
        pubsub.subscribe(**subscribe)
        thread = pubsub.run_in_thread(
            sleep_time=0.001, 
            daemon=True, 
            exception_handler=self.resetConnection
        )
    
        self.pubsubs_active.append({
            "thread" : thread,
            "pubsub" : pubsub
        })
        
    def publish(self, topic, value):
        if self.redis is not None:
            self.redis.publish(topic, value)