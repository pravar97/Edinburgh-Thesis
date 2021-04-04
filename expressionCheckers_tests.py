from expressionCheckers import *
from trees import *
import unittest


class TestStringMethods(unittest.TestCase):

    def test_isSubBinOp1(self):
        actual = isSubBinOp('∧', BinOp('A', '∧', 'B'))
        self.assertTrue(actual)

    def test_isSubBinOp2(self):
        actual = isSubBinOp('∨', BinOp('A', '∧', 'B'))
        self.assertFalse(actual)

    def test_isSubBinOp3(self):
        actual = isSubBinOp('∧', NegOP('A'))
        self.assertTrue(actual)

    def test_isSubBinOp4(self):
        actual = isSubBinOp('∧', 'A')
        self.assertTrue(actual)

    def test_is_in_form1(self):
        actual = is_in_form('CNF', BinOp('A', '∧', 'B'))
        self.assertTrue(actual)

    def test_is_in_form2(self):
        actual = is_in_form('DNF', BinOp('A', '∨', 'B'))
        self.assertTrue(actual)

    def test_is_in_form3(self):
        actual = is_in_form('CNF', BinOp('A', '∨', 'B'))
        self.assertTrue(actual)

    def test_is_in_form4(self):
        actual = is_in_form('CNF', NegOP('A'))
        self.assertTrue(actual)

    def test_is_in_form5(self):
        actual = is_in_form('CNF', 'A')
        self.assertTrue(actual)

    def test_isEQ1(self):
        actual = isEQ(BinOp('A', '∨', 'B'), BinOp('A', '∧', 'B'))
        self.assertFalse(actual)

    def test_isEQ2(self):
        actual = isEQ(BinOp('A', '∨', 'B'), BinOp('A', '∧', 'B'), hint=True)
        expected = False, ['B'], ['A']
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
