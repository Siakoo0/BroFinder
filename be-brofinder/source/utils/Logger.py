import logging

class Logger:
    @staticmethod
    def createLogger(name) -> logging.Logger:
        logger = logging.getLogger(name+"Logger")

        handler_cmdline = logging.StreamHandler()
        handler_cmdline.setLevel(logging.DEBUG)
        
        logger.addHandler(handler_cmdline)
        
        formatter = logging.Formatter(
            fmt='[ %(name)s@%(module)s::%(funcName)s ] [ %(asctime)s ] [ %(levelname)s ] - %(message)s'
        )        
        
        handler_cmdline.setFormatter(formatter)
        
        logger.setLevel(logging.DEBUG)        

        return logger