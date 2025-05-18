import unittest
from src.objdump_analyzer import ObjdumpAnalyzer

class TestObjdumpAnalyzer(unittest.TestCase):

    def test_initialization(self):
        analyzer = ObjdumpAnalyzer('sample.o', 'riscv-objdump')
        self.assertEqual(analyzer.obj_file, 'sample.o')
        self.assertEqual(analyzer.architecture, 'riscv-objdump')
