from threading import Thread
from typing import Any

from importlib import import_module
import glob

from flask import Flask
from flask_restful import Api

import logging

class FlaskServer(Thread):
    def __init__(self, hostname, port) -> None:
        self.hostname = hostname
        self.port = port
        
        self.app = Flask(__name__)
        
        logging.getLogger("werkzeug").setLevel(logging.ERROR)
        
        self.api = Api(self.app)

        self.load_api()

        Thread.__init__(self, daemon=True)

    def load_api(self):
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
            my_class = getattr(module, class_name_string.split(".")[-1])

            # Se non è una classe astratta
            if  "__" not in fname and \
                class_name_string not in excluded_classes:
                
                resource = my_class()
                self.api.add_resource(resource, *resource.urls, endpoint=class_name_string)

    def run(self) -> None:
        self.app.run(**{
            "host" : self.hostname,
            "port" : self.port,
            "debug" : True,
            "use_reloader" : False
        })