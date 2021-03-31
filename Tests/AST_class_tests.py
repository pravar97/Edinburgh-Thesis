from ast_class import *
from trees import *
import unittest


class TestStringMethods(unittest.TestCase):

    def test_ASTPrint1(self):

        tree = ast(BinOp('A', '∨', 'B'))
        actual = tree.ASTPrint(BinOp('A', '∨', 'B'))
        expected = '(A∨B)'
        self.assertEqual(expected, actual)

    def test_ASTPrint2(self):

        tree = ast(TriOp('A', 'B', 'C'))
        actual = tree.ASTPrint(TriOp('A', 'B', 'C'))
        expected = '(A?B:C)'
        self.assertEqual(expected, actual)

    def test_ASTPrint3(self):

        tree = ast(NegOP('A'))
        actual = tree.ASTPrint(NegOP('A'))
        expected = '¬(A)'
        self.assertEqual(expected, actual)

    def test_isTrue1(self):
        tree = ast(BinOp('A', '∨', 'B'))
        actual = tree.isTrue(BinOp('A', '∨', 'B'))
        expected = False
        self.assertEqual(expected, actual)

    def test_isTrue2(self):
        tree = ast(BinOp('A', '⊕', 'B'))
        actual = tree.isTrue(BinOp('A', '⊕', 'B'))
        expected = False
        self.assertEqual(expected, actual)

    def test_isTrue3(self):
        tree = ast(BinOp('A', '∧', 'B'))
        actual = tree.isTrue(BinOp('A', '∧', 'B'))
        expected = False
        self.assertEqual(expected, actual)

    def test_isTrue4(self):
        tree = ast(BinOp('A', '→', 'B'))
        actual = tree.isTrue(BinOp('A', '→', 'B'))
        expected = True
        self.assertEqual(expected, actual)

    def test_isTrue5(self):
        tree = ast(BinOp('A', '↔', 'B'))
        actual = tree.isTrue(BinOp('A', '↔', 'B'))
        expected = True
        self.assertEqual(expected, actual)

    def test_isTrue6(self):
        tree = ast(TriOp('A', 'B', 'C'))
        actual = tree.isTrue(TriOp('A', 'B', 'C'))
        expected = False
        self.assertEqual(expected, actual)

    def test_isTrue7(self):
        tree = ast(NegOP('A'))
        actual = tree.isTrue(NegOP('A'))
        expected = True
        self.assertEqual(expected, actual)

    def test_printTruthTables(self):
        tree = ast('A')
        actual = tree.printTruthTable()
        expected = {'A': [0, 1], 'Result': [0, 1]}
        self.assertDictEqual(expected, actual)

    def test_makeSeq(self):
        tree = ast('A')
        actual = tree.makeSeq(2)
        expected = ['0', '1']
        self.assertEqual(expected, actual)







if __name__ == '__main__':
    unittest.main()
