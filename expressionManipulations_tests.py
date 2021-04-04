from expressionManipulations import *
from trees import *
import unittest


class TestStringMethods(unittest.TestCase):

    def test_tree2str1(self):

        actual = tree2str(NegOP(BinOp('A', '∧', 'B')))
        expected = '¬(A ∧ B)'
        self.assertEqual(expected, actual)

    def test_tree2str2(self):

        actual = tree2str(NegOP('A'))
        expected = '¬A'
        self.assertEqual(expected, actual)

    def test_tree2str3(self):

        actual = tree2str(BinOp(BinOp('A', '∨', 'B'), '∧', 'C'))
        expected = '(A ∨ B) ∧ C'
        self.assertEqual(expected, actual)

    def test_tree2str4(self):

        actual = tree2str(BinOp(BinOp('A', '∧', 'B'), '∧', 'C'))
        expected = 'A ∧ B ∧ C'
        self.assertEqual(expected, actual)

    def test_tree2str5(self):

        actual = tree2str(BinOp('A', '∧', 'B'))
        expected = 'A ∧ B'
        self.assertEqual(expected, actual)

    def test_tree2str6(self):

        actual = tree2str(BinOp('A', '∧', BinOp('B', '∨', 'C')))
        expected = 'A ∧ (B ∨ C)'
        self.assertEqual(expected, actual)

    def test_tree2str7(self):

        actual = tree2str(BinOp('A', '∧', BinOp('B', '∧', 'C')))
        expected = 'A ∧ B ∧ C'
        self.assertEqual(expected, actual)

    def test_tree2str8(self):

        actual = tree2str(TriOp('A', 'B', 'C'))
        expected = '(A ? B : C)'
        self.assertEqual(expected, actual)

    def test_tree2str9(self):

        actual = tree2str('A')
        expected = 'A'
        self.assertEqual(expected, actual)

    def test_rmTO1(self):

        actual = tree2str(rmTO(NegOP('A')))
        expected = tree2str(NegOP('A'))
        self.assertEqual(expected, actual)

    def test_rmTO2(self):
        actual = tree2str(rmTO(BinOp('A', '∧', 'B')))
        expected = tree2str(BinOp('A', '∧', 'B'))
        self.assertEqual(expected, actual)

    def test_rmTO3(self):

        actual = tree2str(rmTO(TriOp('A', 'B', 'C')))
        expected = 'A ∧ B ∨ ¬A ∧ C'
        self.assertEqual(expected, actual)

    def test_rmTO4(self):

        actual = tree2str(rmTO('A'))
        expected = 'A'
        self.assertEqual(expected, actual)

    def test_rmXOR1(self):
        actual = tree2str(rmXOR(NegOP('A')))
        expected = tree2str(NegOP('A'))
        self.assertEqual(expected, actual)

    def test_rmXOR2(self):
        actual = tree2str(rmXOR(TriOp('A', 'B', 'C')))
        expected = tree2str(TriOp('A', 'B', 'C'))
        self.assertEqual(expected, actual)

    def test_rmXOR3(self):
        actual = tree2str(rmXOR(BinOp('A', '⊕', 'B')))
        expected = '¬A ∧ B ∨ ¬B ∧ A'
        self.assertEqual(expected, actual)

    def test_rmXOR4(self):
        actual = tree2str(rmXOR(BinOp('A', '∧', 'B')))
        expected = 'A ∧ B'
        self.assertEqual(expected, actual)

    def test_rmXOR5(self):
        actual = tree2str(rmXOR('A'))
        expected = 'A'
        self.assertEqual(expected, actual)

    def test_rmDI1(self):
        actual = tree2str(rmDI(NegOP('A')))
        expected = tree2str(NegOP('A'))
        self.assertEqual(expected, actual)

    def test_rmDI2(self):
        actual = tree2str(rmDI(TriOp('A', 'B', 'C')))
        expected = tree2str(TriOp('A', 'B', 'C'))
        self.assertEqual(expected, actual)

    def test_rmDI3(self):
        actual = tree2str(rmDI(BinOp('A', '↔', 'B')))
        expected = '(A → B) ∧ (B → A)'
        self.assertEqual(expected, actual)

    def test_rmDI4(self):
        actual = tree2str(rmDI(BinOp('A', '∧', 'B')))
        expected = 'A ∧ B'
        self.assertEqual(expected, actual)

    def test_rmDI5(self):
        actual = tree2str(rmDI('A'))
        expected = 'A'
        self.assertEqual(expected, actual)

    def test_rmSI1(self):
        actual = tree2str(rmSI(NegOP('A')))
        expected = tree2str(NegOP('A'))
        self.assertEqual(expected, actual)

    def test_rmSI2(self):
        actual = tree2str(rmSI(TriOp('A', 'B', 'C')))
        expected = tree2str(TriOp('A', 'B', 'C'))
        self.assertEqual(expected, actual)

    def test_rmSI3(self):
        actual = tree2str(rmSI(BinOp('A', '→', 'B')))
        expected = '¬A ∨ B'
        self.assertEqual(expected, actual)

    def test_rmSI4(self):
        actual = tree2str(rmSI(BinOp('A', '∧', 'B')))
        expected = 'A ∧ B'
        self.assertEqual(expected, actual)

    def test_rmSI5(self):
        actual = tree2str(rmSI('A'))
        expected = 'A'
        self.assertEqual(expected, actual)

    def test_rmN1(self):
        actual = tree2str(rmN(NegOP(NegOP('A'))))
        expected = 'A'
        self.assertEqual(expected, actual)

    def test_rmN2(self):
        actual = tree2str(rmN(NegOP('A')))
        expected = '¬A'
        self.assertEqual(expected, actual)

    def test_rmN3(self):
        actual = tree2str(rmN(BinOp('A', '∧', 'B')))
        expected = 'A ∧ B'
        self.assertEqual(expected, actual)

    def test_rmN4(self):
        actual = tree2str(rmN(TriOp('A', 'B', 'C')))
        expected = '(A ? B : C)'
        self.assertEqual(expected, actual)

    def test_rmN5(self):
        actual = tree2str(rmN('A'))
        expected = 'A'
        self.assertEqual(expected, actual)

    def test_distribute1(self):
        actual = tree2str(distribute('∧', BinOp(BinOp('A', '∧', 'B'), '∨', 'C')))
        expected = '(A ∨ C) ∧ (B ∨ C)'
        self.assertEqual(expected, actual)

    def test_distribute2(self):
        actual = tree2str(distribute('∧', BinOp('A', '∨', BinOp('B', '∧', 'C'))))
        expected = '(A ∨ B) ∧ (A ∨ C)'
        self.assertEqual(expected, actual)

    def test_distribute3(self):
        actual = tree2str(distribute('∧', BinOp('A', '∨', 'B')))
        expected = 'A ∨ B'
        self.assertEqual(expected, actual)

    def test_distribute4(self):
        actual = tree2str(distribute('∧', BinOp('A', '∧', 'B')))
        expected = 'A ∧ B'
        self.assertEqual(expected, actual)

    def test_distribute5(self):
        actual = tree2str(distribute('∧', NegOP('A')))
        expected = '¬A'
        self.assertEqual(expected, actual)

    def test_distribute6(self):
        actual = tree2str(distribute('∧', 'A'))
        expected = 'A'
        self.assertEqual(expected, actual)

    def test_distribute7(self):
        actual = tree2str(distribute('∨', 'A'))
        expected = 'A'
        self.assertEqual(expected, actual)

    def test_list2cons1(self):
        actual = tree2str(list2con(['A']))
        expected = 'A'
        self.assertEqual(expected, actual)

    def test_list2cons2(self):
        actual = tree2str(list2con(['A', 'B']))
        expected = 'A ∧ B'
        self.assertEqual(expected, actual)

    def test_list2DNF1(self):
        actual = tree2str(list2DNF([['A', 'B']]))
        expected = 'A ∧ B'
        self.assertEqual(expected, actual)

    def test_list2DNF2(self):
        actual = tree2str(list2DNF([['A', 'B'], ['C']]))
        expected = 'A ∧ B ∨ C'
        self.assertEqual(expected, actual)

    def test_simCNF1(self):
        actual = simCNF(BinOp('A', '∧', NegOP('A')))
        expected = 'Expression is inconsistent'
        self.assertEqual(expected, actual)

    def test_simCNF2(self):
        actual = simCNF(BinOp('A', '∨', NegOP('A')))
        expected = 'Expression is a tautology'
        self.assertEqual(expected, actual)

    def test_simCNF3(self):
        actual = simCNF('A')
        expected = 'A'
        self.assertEqual(expected, actual)

    def test_findMatch1(self):
        actual = findMatch('111', '100')
        self.assertIsNone(actual)

    def test_findMatch2(self):
        actual = findMatch('11', '10')
        expected = '1_'
        self.assertEqual(expected, actual)

    def test_termsEqual1(self):
        actual = termsEqual('11', '10')
        self.assertFalse(actual)

    def test_termsEqual2(self):
        actual = termsEqual('11', '11')
        self.assertTrue(actual)

    def test_terms2Con(self):
        actual = tree2str(terms2Con('_10', 'ABC'))
        expected = 'B ∧ ¬C'
        self.assertEqual(expected, actual)

    def test_implicants2DNF(self):
        actual = tree2str(implicants2DNF(['1_', '_1'], 'AB'))
        expected = 'A ∨ B'
        self.assertEqual(expected, actual)

    def test_simDNF1(self):
        actual = tree2str(simDNF('A'))
        expected = 'A'
        self.assertEqual(expected, actual)

    def test_simDNF2(self):
        actual = simDNF(BinOp('A', '∧', NegOP('A')))
        expected = 'Expression is inconsistent'
        self.assertEqual(expected, actual)

    def test_simDNF3(self):
        actual = simDNF(BinOp('A', '∨', NegOP('A')))
        expected = 'Expression is a tautology'
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
