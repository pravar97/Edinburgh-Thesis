from trees import BinOp, TriOp, NegOP
import itertools


class ast:
    def __init__(self, astTree, keys=None):
        # Class data for tree
        self.astTree = astTree
        self.terminals = {}
        self.sTerminals = {}
        self.treePrint = self.ASTPrint(astTree)
        if keys is not None:
            self.terminals = {key: False for key in keys}
        self.iTable = {}
        self.lhsStr = ""
        self.rhsStr = ""

    def ASTPrint(self, tree):  # Function for printing out the tree

        # Traversing the tree
        if isinstance(tree, BinOp):
            return "(" + self.ASTPrint(tree.lhs) + tree.op + self.ASTPrint(tree.rhs) + ")"
        if isinstance(tree, TriOp):
            return "(" + self.ASTPrint(tree.lhs) + "?" + self.ASTPrint(tree.mid) + ":" + self.ASTPrint(tree.rhs) + ")"
        elif isinstance(tree, NegOP):
            return "¬" + "(" + self.ASTPrint(tree.stmt) + ")"
        else:
            # Creates a dictionary of terminals for future use
            self.terminals[tree] = False

        return str(tree)

    def isTrue(self, tree):
        assignments = self.terminals
        if isinstance(tree, BinOp):
            # Get valuation of sub trees
            lhs = self.isTrue(tree.lhs)
            rhs = self.isTrue(tree.rhs)

            # Apply operators to the sub trees
            if tree.op == '∨':
                return lhs or rhs
            elif tree.op == '⊕':
                return lhs and not rhs or not lhs and rhs
            elif tree.op == '∧':
                return lhs and rhs
            elif tree.op == '→':
                return (not lhs) or rhs
            elif tree.op == '↔':
                return (not lhs or rhs) and (lhs or not rhs)

        elif isinstance(tree, TriOp):
            lhs = self.isTrue(tree.lhs)
            mid = self.isTrue(tree.mid)
            rhs = self.isTrue(tree.rhs)
            return (not lhs or mid) and (lhs or rhs)

        elif isinstance(tree, NegOP):
            return not self.isTrue(tree.stmt)
        else:  # Base case
            self.lhsStr = tree
            if assignments is None:  # If there are no assignments, never true in this tool
                self.iTable[self.lhsStr] = int(input("Please enter 1 or 0 to assign value to atom:" + tree + '\n')) == 1
                return int(input("Please enter 1 or 0 to assign value to atom:" + tree + '\n')) == 1
            else:
                return assignments[tree]  # Get the atom value when in base case

    def printTruthTable(self):
        tree = self.astTree
        terminals = self.terminals

        output = {}
        atoms = list(terminals.keys())
        atoms.sort()
        for k in atoms:
            output[k] = []  # Make columns for truth table

        output['Result'] = []

        possAssigns = list(itertools.product([0, 1], repeat=len(terminals)))  # Make a list of every true/false
        # combination

        for i in possAssigns:  # Loop through each true/false combination
            j = 0

            for k in atoms:  # Fill in the atoms column
                terminals[k] = bool(i[j])
                output[k].append(i[j])
                j += 1

            output['Result'].append(int(self.isTrue(tree)))  # Calculate statement evaluation and fill in the results
            # column

        return output

    def makeSeq(self, l):
        if l == 2:
            return ['0', '1']
        subseq = self.makeSeq(l/2)
        seq = ['0' + x for x in subseq]
        subseq.reverse()
        seq += ['1' + x for x in subseq]
        return seq

    def printKMap(self):

        terminals = self.terminals
        numrows = len(terminals) // 2
        numcols = len(terminals) - numrows
        atoms = list(terminals.keys())
        atoms.sort()
        colatoms = atoms[numrows:]
        rowatoms = atoms[:numrows]

        kmap = {}
        rowkeys = ['0']
        if numrows > 0:
            rowkeys = self.makeSeq(2 ** numrows)
        colkeys = self.makeSeq(2 ** numcols)
        for c in colkeys:
            kmap[c] = []
            for r in rowkeys:
                for a, k in zip(atoms, r+c):
                    terminals[a] = bool(int(k))
                kmap[c].append(int(self.isTrue(self.astTree)))

        return kmap, rowkeys, rowatoms, colatoms






