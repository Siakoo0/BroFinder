import logging
import sys
import threading

import inspect

class Logger:
    @staticmethod
    def createLogger(name) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.NOTSET)

        formatter = logging.Formatter('[ %(threadName)s@%(module)s::%(funcName)s ] [ %(asctime)s ] [ %(levelname)s ] - %(message)s', datefmt="")
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.NOTSET)
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

        return logger