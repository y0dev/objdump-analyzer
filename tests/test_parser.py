import unittest
from src.parser import ObjdumpParser

class TestObjdumpParser(unittest.TestCase):

    def test_parse_line(self):
        parser = ObjdumpParser(registers=['a0'])
        parser.parse_line("1000: lw a0, 0(a1)")
