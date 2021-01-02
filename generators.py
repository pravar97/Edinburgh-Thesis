import pandas as pd

from statementCheckers import *
from werkzeug.utils import redirect
import random


def gen_stmt(tree):
    pres = {'→': 3, '↔': 4, '∧': 0, '∨': 2, '⊕': 1}  # Keep track of precedences
    if isinstance(tree, NegOP):
        if isinstance(tree.stmt, BinOp):
            return "¬(" + gen_stmt(tree.stmt) + ")"  # We negate the entire statement
        else:
            return "¬" + gen_stmt(tree.stmt)  # This negation does not require brackets
    if isinstance(tree, BinOp):
        out = ""
        if isinstance(tree.lhs, BinOp):
            if pres[tree.lhs.op] > pres[tree.op] or pres[tree.lhs.op] > 2 and pres[tree.op] > 2:
                out += "(" + gen_stmt(
                    tree.lhs) + ")"  # Need brackets since the precedence of sub tree is higher than parent tree
            else:
                out += gen_stmt(tree.lhs)
        else:
            out += gen_stmt(tree.lhs)  # No brackets since it won't make a difference
        out += " " + tree.op + " "
        if isinstance(tree.rhs, BinOp):
            if pres[tree.rhs.op] > pres[tree.op] or pres[tree.rhs.op] > 2 and pres[tree.op] > 2:
                out += "(" + gen_stmt(tree.rhs) + ")"
            else:
                out += gen_stmt(tree.rhs)
        else:
            out += gen_stmt(tree.rhs)
        return out
    if isinstance(tree, TriOp):
        return "(" + gen_stmt(tree.lhs) + " ? " + gen_stmt(tree.mid) + " : " + gen_stmt(tree.rhs) + ")"
    else:
        return str(tree)


def genRanTree(s):
    if s > 19:  # Base case: return a single atom
        return 'xyzabcdefg'[random.randint(0, 9)]  # Randomly select an atom
    elif s > 14:
        return NegOP('xyzabcdefg'[random.randint(0, 9)])
    elif s > 13:
        ran = random.randint(0, 2)
    elif s > 6:
        ran = random.randint(0, 3)
    elif s > 0:
        ran = random.randint(0, 5)
    else:
        ran = random.randint(0, 6)

    if ran == 6:
        a = genRanTree(s + 20)
        b = genRanTree(s + 20)
        c = genRanTree(s + 20)
        return TriOp(a, b, c)
    elif ran > 3:
        a = genRanTree(s + 14)
        b = genRanTree(s + 14)
        return BinOp(a, ['↔', '⊕'][ran % 2], b)
    elif ran == 3:
        a = genRanTree(s + 7)
        b = genRanTree(s + 7)
        return BinOp(a, '→', b)
    elif ran > 0:
        a = genRanTree(s + 6)
        b = genRanTree(s + 6)
        return BinOp(a, ['∨', '∧'][ran % 2], b)
    else:
        return NegOP(genRanTree(s + 1))


def genQuestion(difficulty):
    if not random.randint(0,2):
        return genTruthTable(difficulty)
    while True:  # Keep making statements until appropriate
        curTree = genRanTree(difficulty)  # Generate random statement with difficulty parameter
        curAST = ast(curTree)
        u_results = curAST.printTruthTable()['Result']  # Get the results column from the statement's truth table
        # Only be okay this data if its satisfiable, not a tautology and is not already in CNF
        if 1 in u_results and 0 in u_results and not isCNF(curTree):
            return curTree


def genTruthTable(difficulty):
    numAtoms = {10: 2, 5: 2, 0: 3, -5: 4, -10: 4}[difficulty]
    output = {}
    for k in 'abcdef'[:numAtoms]:
        output[k] = []  # Make columns for truth table

    output['Result'] = []

    possAssigns = list(itertools.product([0, 1], repeat=numAtoms))  # Make a list of every true/false
    # combination

    for i in possAssigns:  # Loop through each true/false combination
        j = 0

        for k in 'abcdef'[:numAtoms]:  # Fill in the atoms column
            output[k].append(i[j])
            j += 1

        output['Result'].append(random.randint(0, 1))  # random result
    if 1 not in output['Result']:
        output['Result'][random.randint(0, len(possAssigns)-1)] = 1
    if 0 not in output['Result']:
        output['Result'][random.randint(0, len(possAssigns)-1)] = 0

    solution = None
    for i, k in enumerate(output['Result']):
        if k == 1:
            atoms = []
            for a in output:
                if a != 'Result':
                    if output[a][i]:
                        atoms.append(a)
                    else:
                        atoms.append(NegOP(a))
            subtree = atoms[0]
            for a in atoms[1:]:
                subtree = BinOp(subtree, '∧', a)
            if solution is None:
                solution = subtree
            else:
                solution = BinOp(solution, '∨', subtree)
    pdTable = pd.DataFrame(output)  # Create a table data structure from truth table dictionary
    table = pdTable.head(len(output['Result'])).to_html(col_space=50, classes='Table')  # Generate HTML

    return table, solution
