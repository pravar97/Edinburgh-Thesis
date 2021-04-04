from generators import *
from expressionManipulations import *
from expressionCheckers import *
import unittest


class TestStringMethods(unittest.TestCase):

    def test_VeryEasy(self):

        self.all_diff_test(5, 'VeryEasy')

    def test_Easy(self):

        self.all_diff_test(10, 'Easy')

    def test_Medium(self):

        self.all_diff_test(15, 'Medium')

    def test_Hard(self):

        self.all_diff_test(20, 'Hard')

    def test_VeryHard(self):

        self.all_diff_test(25, 'VeryHard')

    def all_diff_test(self, diff, diff_text):

        for i in range(10000):

            tree = genRanTree(diff)
            with self.subTest(diff_text + '_rmTo_isEQ_' + str(i)):

                actual = rmTO(tree)
                self.assertTrue(isEQ(actual, tree))

            with self.subTest(diff_text + '_rmTo_correctForm_' + str(i)):

                actual = rmTO(tree)
                self.assertFalse('?' in tree2str(actual))

            with self.subTest(diff_text + '_rmXOR_isEQ_' + str(i)):

                actual = rmXOR(rmTO(tree))
                self.assertTrue(isEQ(actual, tree))

            with self.subTest(diff_text + '_rmXOR_correctForm_' + str(i)):

                actual = rmXOR(rmTO(tree))
                self.assertFalse('⊕' in tree2str(actual))

            with self.subTest(diff_text + '_rmDI_isEQ_' + str(i)):

                actual = rmDI(rmXOR(rmTO(tree)))
                self.assertTrue(isEQ(actual, tree))

            with self.subTest(diff_text + '_rmDI_correctForm_' + str(i)):

                actual = rmDI(rmXOR(rmTO(tree)))
                self.assertFalse('↔' in tree2str(actual))

            with self.subTest(diff_text + '_rmSI_isEQ_' + str(i)):

                actual = rmSI(rmDI(rmXOR(rmTO(tree))))
                self.assertTrue(isEQ(actual, tree))

            with self.subTest(diff_text + '_rmSI_correctForm_' + str(i)):

                actual = rmSI(rmDI(rmXOR(rmTO(tree))))
                self.assertFalse('→' in tree2str(actual))

            with self.subTest(diff_text + '_rmB_isEQ_' + str(i)):

                actual = rmB(rmSI(rmDI(rmXOR(rmTO(tree)))))
                self.assertTrue(isEQ(actual, tree))

            with self.subTest(diff_text + '_rmN_isEQ_' + str(i)):

                actual = rmN(rmB(rmSI(rmDI(rmXOR(rmTO(tree))))))
                self.assertTrue(isEQ(actual, tree))

            with self.subTest(diff_text + '_distribute_AND_isEQ_' + str(i)):

                actual = distribute('∧', rmN(rmB(rmSI(rmDI(rmXOR(rmTO(tree)))))))
                self.assertTrue(isEQ(actual, tree))

            with self.subTest(diff_text + '_distribute_OR_isEQ_' + str(i)):

                actual = distribute('∨', rmN(rmB(rmSI(rmDI(rmXOR(rmTO(tree)))))))
                self.assertTrue(isEQ(actual, tree))

            with self.subTest(diff_text + '_simCNF_isEQ_' + str(i)):

                actual = simCNF(tree)
                self.assertTrue(isEQ(actual, tree))

            with self.subTest(diff_text + '_simDNF_isEQ_' + str(i)):

                actual = simDNF(tree)
                self.assertTrue(isEQ(actual, tree))

            with self.subTest(diff_text + '_simCNF_correctForm_' + str(i)):
                actual = simCNF(tree)
                self.assertTrue(is_in_form('CNF', actual))

            with self.subTest(diff_text + '_simDNF_correctForm_' + str(i)):
                actual = simDNF(tree)
                self.assertTrue(is_in_form('DNF', actual))




if __name__ == '__main__':
    unittest.main()