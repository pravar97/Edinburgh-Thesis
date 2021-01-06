from flask import request
from ast_class import *
import hashlib

def isDis(tree):
    if isinstance(tree, BinOp):
        if tree.op == '∨':  # Check if 'or' operator and keep recursing if it is
            return isDis(tree.lhs) and isDis(tree.rhs)
        else:
            return False  # If it is an 'and' operator then this is not a disjunction
    if isinstance(tree, NegOP):
        return type(tree.stmt) == str  # Check if statement is a negation with only an atom as subtree

    return type(tree) == str  # single atoms can be disjunctions


def isCNF(tree):
    if isinstance(tree, BinOp):
        if tree.op == '∧':  # Check if we have an 'and' operator
            return isCNF(tree.lhs) and isCNF(tree.rhs)  # Keep recursing while we see 'and's
        else:
            return isDis(tree)   # If tree is 'or', then check if its a disjunction
    if isinstance(tree, NegOP):  # If a negation it should only negate a single atom in CNF
        return type(tree.stmt) == str

    return type(tree) == str  # Single atoms are in CNF always


def isEQ(a, b, hint=None):
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