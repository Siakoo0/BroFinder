from abc import ABC, abstractmethod


class Entity(ABC):
    
    @property
    @abstractmethod
    def collection():
        pass
    
    def convert(self, elem):
        if hasattr(elem, "__dict__"):
            return elem.__dict__
        else:
            return elem

    @abstractmethod
    def save(self):
        pass
