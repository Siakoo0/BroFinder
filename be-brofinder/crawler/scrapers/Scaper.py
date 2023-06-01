from abc import ABC, abstractmethod

from crawler.entities.Product import Product
from typing import List


class ScraperAbstractClass(ABC):
    @abstractmethod
    def search(self, product: str) -> List[Product]:
        pass
