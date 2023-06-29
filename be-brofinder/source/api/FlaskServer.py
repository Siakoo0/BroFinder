from collections.abc import Callable, Iterable, Mapping
from threading import Thread
from typing import Any

from flask import Flask
from flask_restful import Api, Resource

import glob

from importlib import import_module

from source.api.BaseResource import BaseResource


class FlaskServer(Thread):
    def __init__(self, hostname, port) -> None:
        self.hostname = hostname
        self.port = port
        
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
            my_class = getattr(module, class_name_string.split(".")[-1])

            # Se non è una classe astratta
            if  "__" not in fname and \
                class_name_string not in excluded_classes:
                
                resource : BaseResource  = my_class()
                self.api.add_resource(resource, resource.urls)

    def run(self) -> None:
        self.app.run(**{
            "host" : self.hostname,
            "port" : self.port,
            "debug" : True,
            "use_reloader" : False
        })