import unittest
from unittest.suite import TestSuite
from unittest import TestCase

from source.crawlers.utils.Singleton import Singleton

class TestSuite(metaclass=Singleton):
    def __init__(self) -> None:
        self.runner = unittest.TextTestRunner(verbosity=2)

    def run(self):
        suite = unittest.defaultTestLoader.discover("tests")
        self.runner.run(suite)

    