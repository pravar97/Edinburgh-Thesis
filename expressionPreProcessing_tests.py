from expressionPreProcessing import *
from expressionManipulations import *
import unittest


class TestStringMethods(unittest.TestCase):

    def test_parse1(self):

        p = Parser([])
        with self.assertRaises(Exception):
            p.parse()

    def test_parse2(self):

        p = Parser(['(', 'A'])
        with self.assertRaises(Exception):
            p.parse()

    def test_parse3(self):

        p = Parser(['(', 'A', ')'])
        actual = p.parse()
        expected = 'A'
        self.assertEqual(expected, actual)

    def test_parse4(self):

        p = Parser(['A'])
        actual = p.parse()
        expected = 'A'
        self.assertEqual(expected, actual)

    def test_parse5(self):

        p = Parser(['∧'])
        with self.assertRaises(Exception):
            p.parse()

    def test_parse6(self):

        p = Parser(['¬', 'A'])
        actual = tree2str(p.parse())
        expected = '¬A'
        self.assertEqual(expected, actual)

    def test_parse7(self):

        p = Parser(['A', '∧', 'B', '∧', 'C'])
        actual = tree2str(p.parse())
        expected = 'A ∧ B ∧ C'
        self.assertEqual(expected, actual)

    def test_parse8(self):

        p = Parser(['A', '∧', 'B'])
        actual = tree2str(p.parse())
        expected = 'A ∧ B'
        self.assertEqual(expected, actual)

    def test_parse9(self):

        p = Parser(['A', '⊕', 'B', '⊕', 'C'])
        actual = tree2str(p.parse())
        expected = 'A ⊕ B ⊕ C'
        self.assertEqual(expected, actual)

    def test_parse10(self):

        p = Parser(['A', '⊕', 'B'])
        actual = tree2str(p.parse())
        expected = 'A ⊕ B'
        self.assertEqual(expected, actual)

    def test_parse11(self):

        p = Parser(['A', '∨', 'B', '∨', 'C'])
        actual = tree2str(p.parse())
        expected = 'A ∨ B ∨ C'
        self.assertEqual(expected, actual)

    def test_parse12(self):

        p = Parser(['A', '∨', 'B'])
        actual = tree2str(p.parse())
        expected = 'A ∨ B'
        self.assertEqual(expected, actual)

    def test_parse13(self):

        p = Parser(['A', '→', 'B', '→', 'C'])
        actual = tree2str(p.parse())
        expected = 'A → (B → C)'
        self.assertEqual(expected, actual)

    def test_parse14(self):

        p = Parser(['A', '→', 'B'])
        actual = tree2str(p.parse())
        expected = 'A → B'
        self.assertEqual(expected, actual)

    def test_parse15(self):

        p = Parser(['A', '↔', 'B', '↔', 'C'])
        actual = tree2str(p.parse())
        expected = 'A ↔ (B ↔ C)'
        self.assertEqual(expected, actual)

    def test_parse16(self):

        p = Parser(['A', '↔', 'B'])
        actual = tree2str(p.parse())
        expected = 'A ↔ B'
        self.assertEqual(expected, actual)

    def test_parse17(self):

        p = Parser(['A', '?', 'B', ':', 'C', '?', 'D', ':', 'E'])
        actual = tree2str(p.parse())
        expected = '(A ? B : (C ? D : E))'
        self.assertEqual(expected, actual)

    def test_parse18(self):

        p = Parser(['A', '?', 'B', ':', 'C'])
        actual = tree2str(p.parse())
        expected = '(A ? B : C)'
        self.assertEqual(expected, actual)

    def test_parse19(self):

        p = Parser(['A', 'B'])
        with self.assertRaises(Exception):
            p.parse()

    def test_tokenize1(self):

        actual = tokenize('aaaa')
        expected = ['AAAA']
        self.assertEqual(expected, actual)

    def test_tokenize2(self):

        actual = tokenize('a||b+c or d&&e.f and g⊕h xor i → j ↔ k <-> l ->')
        expected = ['A', '∨', 'B', '∨', 'C', '∨', 'D', '∧', 'E', '∧', 'F', '∧',
                    'G', '⊕', 'H', '⊕', 'I', '→', 'J', '↔', 'K', '↔', 'L', '→']
        self.assertEqual(expected, actual)

    def test_tokenize3(self):

        actual = tokenize('not !(a)?b:c d')
        expected = ['¬', '¬', '(', 'A', ')', '?', 'B', ':', 'C', 'D']
        self.assertEqual(expected, actual)

    def test_tokenize4(self):

        with self.assertRaises(Exception):
            tokenize('a.b.c.d.e.f.g.h.i.j.k.l|m||o||n')

    def test_tokenize5(self):

        with self.assertRaises(Exception):
            tokenize('a.b.c.d.e.f.g.h.i.j.k.l||m||o|n')

    def test_tokenize6(self):

        with self.assertRaises(Exception):
            tokenize('a.b.c.d.e.f.g.h.i.j.k.l|m|o or n')

    def test_tokenize7(self):

        with self.assertRaises(Exception):
            tokenize('a.b.c.d.e.f.g.h.i.j.k.l|m|o→n')

    def test_tokenize8(self):

        with self.assertRaises(Exception):
            tokenize('a.b.c.d.e.f.g.h.i.j.k.l|m|o↔n')

    def test_tokenize9(self):

        with self.assertRaises(Exception):
            tokenize('a.b.c.d.e.f.g.h.i.j.k.l|m|o<->n')

    def test_tokenize10(self):

        with self.assertRaises(Exception):
            tokenize('a.b.c.d.e.f.g.h.i.j.k.l|m|o->n')

    def test_tokenize11(self):

        with self.assertRaises(Exception):
            tokenize('a.b.c.d.e.f.g.h.i.j.k.l|m|o(n')

    def test_tokenize12(self):

        with self.assertRaises(Exception):
            tokenize('a.b.c.d.e.f.g.h.i.j.k.l|m|o)n')

    def test_tokenize13(self):

        with self.assertRaises(Exception):
            tokenize('a.b.c.d.e.f.g.h.i.j.k.l|m|o?n')

    def test_tokenize14(self):

        with self.assertRaises(Exception):
            tokenize('a.b.c.d.e.f.g.h.i.j.k.l|m|o:n')

    def test_tokenize15(self):

        with self.assertRaises(Exception):
            tokenize('a.b.c.d.e.f.g.h.i.j.k.l|m|o.n')

    def test_tokenize16(self):

        with self.assertRaises(Exception):
            tokenize('a.b.c.d.e.f.g.h.i.j.k.l|m|o.n')

    def test_tokenize17(self):

        with self.assertRaises(Exception):
            tokenize('a.b.c.d.e.f.g.h.i.j.k.l|m|o&&n')

    def test_tokenize18(self):

        with self.assertRaises(Exception):
            tokenize('a.b.c.d.e.f.g.h.i.j.k.l|m|o⊕n')

    def test_tokenize19(self):

        with self.assertRaises(Exception):
            tokenize('a.b.c.d.e.f.g.h.i.j.k.l|m o')


if __name__ == '__main__':
    unittest.main()
