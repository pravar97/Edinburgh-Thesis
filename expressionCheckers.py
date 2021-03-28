from ast_class import *


def isSubBinOp(op, tree):
    if isinstance(tree, BinOp):
        if tree.op == op:  # Check if 'or' operator and keep recursing if it is
            return isSubBinOp(op, tree.lhs) and isSubBinOp(op, tree.rhs)
        else:
            return False  # If it is an 'and' operator then this is not a disjunction
    if isinstance(tree, NegOP):
        return type(tree.stmt) == str  # Check if expression is a negation with only an atom as subtree

    return type(tree) == str  # single atoms can be disjunctions


def is_in_form(f, tree):
    if f == 'CNF':
        op = '∧'
        opp_op = '∨'
    else:
        op = '∨'
        opp_op = '∧'
    if isinstance(tree, BinOp):
        if tree.op == op:  # Check if we have an 'and' operator
            return is_in_form(f, tree.lhs) and is_in_form(f, tree.rhs)  # Keep recursing while we see 'and's
        else:
            return isSubBinOp(opp_op, tree)   # If tree is 'or', then check if its a disjunction
    if isinstance(tree, NegOP):  # If a negation it should only negate a single atom in CNF
        return type(tree.stmt) == str

    return type(tree) == str  # Single atoms are in CNF always


def isEQ(a, b, hint=None):
    desc2tree = {'Expression is a tautology': BinOp('a', '∨', NegOP('a')),
                 'Expression is inconsistent': BinOp('a', '∧', NegOP('a'))}
    a = desc2tree.get(a, a)
    b = desc2tree.get(b, b)
    tt = ast(BinOp(a, '⊕', b)).printTruthTable()
    eq = 1 not in tt['Result']
    if hint is None:
        return eq
    trues = []
    falses = []
    if not eq:
        eg = tt['Result'].index(1)
        for atom in tt:
            if atom == 'Result':
                continue
            if tt[atom][eg]:
                trues.append(atom)
            else:
                falses.append(atom)

    return eq, trues, falses