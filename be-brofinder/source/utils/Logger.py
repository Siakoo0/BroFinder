import logging

class Logger:
    @staticmethod
    def createLogger(name) -> logging.Logger:
        logger = logging.getLogger(name+"Logger")
        logger.setLevel(logging.NOTSET)

        return logger