from threading import Thread
from typing import Any

from importlib import import_module
import glob

from flask import Flask
from flask_restful import Api

from source.api.BaseResource import BaseResource

class FlaskServer(Thread):
    def __init__(self, hostname, port, queues) -> None:
        self.hostname = hostname
        self.port = port
        self.queues = queues
        
        self.app = Flask(__name__)
        
        self.api = Api(self.app)

        self.loadAPI()

        Thread.__init__(self, daemon=True)

    def loadAPI(self):
        excluded_classes = []

        for fname in glob.glob("./source/api/**/resources/*.py", recursive=True):
            # Costruisco il percorso per importare il modulo
            class_name_string = fname.replace(".py", "") \
                                     .replace("\\", ".") \
                                     .replace("/", ".") \
                                     .strip(".")

            # Importo il modulo
            module = import_module(class_name_string)

            # Prelevo la classe dal modulo e la istanzio se non è astratta
            resource = getattr(module, class_name_string.split(".")[-1])

            # Se non è una classe astratta
            if  "__" not in fname and \
                class_name_string not in excluded_classes:
                
                self.api.add_resource(
                    resource, 
                    *resource().urls, 
                    endpoint=class_name_string, 
                    resource_class_kwargs={
                        "queues":self.queues
                    }
                )

    def run(self) -> None:
        self.app.run(**{
            "host" : self.hostname,
            "port" : self.port,
            "debug" : True,
            "use_reloader" : False
        })