from generators import *

import unittest


class TestStringMethods(unittest.TestCase):

    def test_makeSeq1(self):

        actual = makeSeq(2)
        expected = ['0', '1']
        self.assertEqual(expected, actual)

    def test_makeSeq2(self):

        actual = makeSeq(4)
        expected = ['00', '01', '11', '10']
        self.assertEqual(expected, actual)

    def test_genMinTerms(self):

        actual = genMinTerms(TriOp('A', 'B', BinOp('C', '∧', 'D')))
        expected = {'0011', '0111', '1100', '1101', '1110', '1111'}
        self.assertEqual(expected, actual)

    def test_kmap2tree(self):

        actual = simDNF(kmap2tree({'0': [0, 1], '1': [0, 1]}, 'A', 'B', '01'))
        expected = 'A'
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()