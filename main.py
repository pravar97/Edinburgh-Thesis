import hashlib
import json
import random

from flask import Flask, render_template, request

import itertools
from flask_wtf import FlaskForm
from werkzeug.utils import redirect

from wtforms import StringField, SubmitField

from flask_bootstrap import Bootstrap

import pandas as pd

app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = 'bdd9761c62d68ea530872f8848107c21'


class BinOp:
    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.op = op


class TriOp:
    def __init__(self, lhs, mid, rhs):
        self.lhs = lhs
        self.mid = mid
        self.rhs = rhs


class NegOP:

    def __init__(self, stmt):
        self.stmt = stmt


class Parser:

    def __init__(self, tokens):
        self.i = 0
        self.tokens = tokens
        self.end = False

    def getToken(self):
        if self.i >= len(self.tokens):
            self.end = True
            return 'end'
        else:
            return self.tokens[self.i]

    def expect(self, c):
        token = self.getToken()
        if c == token:
            self.i += 1
        else:
            raise Exception("Expected " + c + " but received " + token)

    def parse(self):
        output = self.parseStmt()  # Get root node of tree, using LL recursive parsing
        if self.i < len(self.tokens):
            raise Exception("Additional tokens at end of statement are invalid")
        return output

    def parseStmt(self):

        lhs = self.parseStmt1()
        mid, rhs = self.parseStmtR()
        if rhs is None:
            return lhs
        else:
            return TriOp(lhs, mid, rhs)

    def parseStmtR(self):

        token = self.getToken()
        if token == '?':
            self.i += 1
            mid = self.parseStmt1()
            self.expect(':')
            rhs = self.parseStmt1()
            end = self.parseStmtR()
            if None in end:
                return mid, rhs
            else:
                return mid, TriOp(rhs, end[0], end[1])
        return None, None

    def parseStmt1(self):
        lhs = self.parseStmt2()
        op = self.getToken()
        rhs = self.parseStmt1R()
        if rhs is None:
            return lhs
        else:
            return BinOp(lhs, op, rhs)

    def parseStmt1R(self):
        token = self.getToken()
        if token == '↔':
            self.i += 1
            lhs = self.parseStmt2()
            op = self.getToken()
            rhs = self.parseStmt1R()
            if rhs is None:
                return lhs
            else:
                return BinOp(lhs, op, rhs)

    def parseStmt2(self):
        lhs = self.parseStmt3()
        op = self.getToken()
        rhs = self.parseStmt2R()
        if rhs is None:
            return lhs
        else:
            return BinOp(lhs, op, rhs)

    def parseStmt2R(self):
        token = self.getToken()
        if token == '→':
            self.i += 1
            lhs = self.parseStmt3()
            op = self.getToken()
            rhs = self.parseStmt2R()
            if rhs is None:
                return lhs
            else:
                return BinOp(lhs, op, rhs)

    def parseStmt3(self):
        lhs = self.parseStmt4()
        op = self.getToken()
        rhs = self.parseStmt3R()
        if rhs is None:
            return lhs
        else:
            return BinOp(lhs, op, rhs)

    def parseStmt3R(self):
        token = self.getToken()
        if token == '∨':
            self.i += 1
            lhs = self.parseStmt4()
            op = self.getToken()
            rhs = self.parseStmt3R()
            if rhs is None:
                return lhs
            else:
                return BinOp(lhs, op, rhs)

    def parseStmt4(self):
        lhs = self.parseStmt5()
        op = self.getToken()
        rhs = self.parseStmt4R()
        if rhs is None:
            return lhs
        else:
            return BinOp(lhs, op, rhs)

    def parseStmt4R(self):
        token = self.getToken()
        if token == '⊕':
            self.i += 1
            lhs = self.parseStmt5()
            op = self.getToken()
            rhs = self.parseStmt4R()
            if rhs is None:
                return lhs
            else:
                return BinOp(lhs, op, rhs)

    def parseStmt5(self):
        lhs = self.parseStmt6()
        op = self.getToken()
        rhs = self.parseStmt5R()
        if rhs is None:
            return lhs
        else:
            return BinOp(lhs, op, rhs)

    def parseStmt5R(self):
        token = self.getToken()
        if token == '∧':
            self.i += 1
            lhs = self.parseStmt6()
            op = self.getToken()
            rhs = self.parseStmt5R()
            if rhs is None:
                return lhs
            else:
                return BinOp(lhs, op, rhs)

    def parseStmt6(self):
        token = self.getToken()
        if token == '¬':
            self.i += 1
            return NegOP(self.parseStmt6())
        elif token == '(':
            self.i += 1
            output = self.parseStmt()
            self.expect(')')
            return output
        else:
            return self.parseIdent()

    def parseIdent(self):
        token = self.getToken()
        if self.end:
            raise Exception("Unexpected end of statement")
        if token not in ['(', ')', '¬', '∧', '∨', '→', '↔', '?', ':', '⊕']:
            self.i += 1
            return token
        else:
            raise Exception("Expected Identifier but got " + token)


def tokenize(stream):
    token = ""
    tokens = []
    identcount = 0

    i = 0
    while i < len(stream):  # Loop through all characters

        c = stream[i]  # current character
        last = i + 1 == len(stream)  # Check if we are at last
        pen = i + 2 == len(stream)  # Check if we are at 2nd last
        penpen = i + 3 == len(stream)  # Check if we are at 3rd last

        # Get up to 3 future characters depending where we are in stream
        if not last:
            c2 = stream[i + 1]
            if not pen:
                c3 = stream[i + 2]
                if not penpen:
                    c4 = stream[i + 3]
                else:
                    c4 = 'a'
            else:
                c3 = 'a'
                c4 = 'a'
        else:
            c2 = 'a'
            c3 = 'a'
            c4 = 'a'

        if c == '+' or c == '∨' or c == '|':
            if token not in tokens:
                identcount += 1
            if identcount > 13:  # Enforce bounds of number of atoms
                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("∨")  # Add operator

            token = ""  # Reset for next atom
        elif c.lower() == 'o' and not (' ' + token)[-1].isalpha() and c2.lower() == 'r' and not c3.isalpha():
            if token not in tokens:
                identcount += 1
            if identcount > 13:  # Enforce bounds of number of atoms
                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("∨")  # Add operator

            token = ""  # Reset for next atom
            i += 1  # Increment loop counter more to cover additional chars in this notation

        elif c == '.' or c == '*' or c == '∧' or c == '&':
            if token not in tokens:
                identcount += 1
            if identcount > 13:   # Enforce bounds of number of atoms
                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("∧")  # Add operator

            token = ""  # Reset for next atom

        elif c.lower() == 'a' and not (' ' + token)[-1].isalpha() and c2.lower() == 'n' and c3.lower() == 'd' and not c4.isalpha():
            if token not in tokens:
                identcount += 1
            if identcount > 13:   # Enforce bounds of number of atoms
                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("∧")  # Add operator
            token = ""  # Reset for next atom
            i += 2  # Increment loop counter more to cover additional chars in this notation

        elif c == '^' or c == '⊕':
            if token not in tokens:
                identcount += 1
            if identcount > 13:  # Enforce bounds of number of atoms
                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("⊕")  # Add operator

            token = ""  # Reset for next atom

        elif c.lower() == 'x' and not (' ' + token)[-1].isalpha() and c2.lower() == 'o' and c3.lower() == 'r' and not c4.isalpha():
            if token not in tokens:
                identcount += 1
            if identcount > 13:  # Enforce bounds of number of atoms
                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("⊕")  # Add operator
            token = ""  # Reset for next atom
            i += 2  # Increment loop counter more to cover additional chars in this notation

        elif c == '→':
            if token not in tokens:
                identcount += 1
            if identcount > 13:  # Enforce bounds of number of atoms
                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("→")  # Add operator

            token = ""  # Reset for next atom

        elif c == '↔':
            if token not in tokens:
                identcount += 1
            if identcount > 13:   # Enforce bounds of number of atoms
                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("↔")  # Add operator

            token = ""  # Reset for next atom

        elif c == '<' and (c2 == '-' or c2 == '=') and c3 == '>':
            if token not in tokens:
                identcount += 1
            if identcount > 13:   # Enforce bounds of number of atoms
                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("↔")  # Add operator
            i += 2  # Increment loop counter more to cover additional chars in this notation

            token = ""  # Reset for next atom

        elif (c == '-' or c == '=') and c2 == '>':
            if token not in tokens:
                identcount += 1
            if identcount > 13:   # Enforce bounds of number of atoms
                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("→")  # Add operator
            i += 1  # Increment loop counter more to cover additional chars in this notation

            token = ""  # Reset for next atom

        elif c == '(':
            if token not in tokens:
                identcount += 1
            if identcount > 13:   # Enforce bounds of number of atoms
                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("(")  # Add operator

            token = ""  # Reset for next atom
        elif c == ')':
            if token not in tokens:
                identcount += 1
            if identcount > 13:   # Enforce bounds of number of atoms
                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append(")")  # Add operator

            token = ""  # Reset for next atom
        elif c == '?':
            if token not in tokens:
                identcount += 1
            if identcount > 13:   # Enforce bounds of number of atoms
                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("?")  # Add operator

            token = ""  # Reset for next atom
        elif c == ':':
            if token not in tokens:
                identcount += 1
            if identcount > 13:   # Enforce bounds of number of atoms
                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append(":")  # Add operator

            token = ""  # Reset for next atom
        elif c == '!' or c == '~' or c == '-' or c == '¬':
            if token not in tokens:
                identcount += 1
            if identcount > 13:   # Enforce bounds of number of atoms
                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("¬")  # Add operator

            token = ""  # Reset for next atom
        elif c.lower() == 'n' and not (' ' + token)[
            -1].isalpha() and c2.lower() == 'o' and c3.lower() == 't' and not c4.isalpha():
            if token not in tokens:
                identcount += 1
            if identcount > 13:   # Enforce bounds of number of atoms
                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("¬")  # Add operator
            token = ""  # Reset for next atom
            i += 2  # Increment loop counter more to cover additional chars in this notation
        elif c.isspace():
            if token not in tokens:
                identcount += 1
            if identcount > 13:   # Enforce bounds of number of atoms
                raise Exception("Too many atoms!")

            tokens.append(token)  # Add atom preceding current operator
            token = ""  # Reset for next atom

        else:
            token += c
        i += 1  # Increment loop counter
    if token not in tokens:
        identcount += 1
    if identcount > 13:   # Enforce bounds of number of atoms
        raise Exception("Too many atoms!")
    tokens.append(token)  # Add last token
    while "" in tokens:
        tokens.remove("")  # Remove empty tokens
    return tokens


class ast:
    def __init__(self, astTree):
        # Class data for tree
        self.astTree = astTree
        self.terminals = {}
        self.sTerminals = {}
        self.treePrint = self.ASTPrint(astTree)
        self.iTable = {}
        self.lhsStr = ""
        self.rhsStr = ""

    def ASTPrint(self, tree):  # Function for printing out the tree

        global maxTerminalSize

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
            if assignments == None:  # If there are no assignments, never true in this tool
                self.iTable[self.lhsStr] = int(input("Please enter 1 or 0 to assign value to atom:" + tree + '\n')) == 1
                return int(input("Please enter 1 or 0 to assign value to atom:" + tree + '\n')) == 1
            else:
                return assignments[tree]  # Get the atom value when in base case

    def printTruthTable(self):
        tree = self.astTree
        terminals = self.terminals

        output = {}
        for k in terminals:
            output[k] = []  # Make columns for truth table

        output['Result'] = []

        possAssigns = list(itertools.product([0, 1], repeat=len(terminals)))  # Make a list of every true/false
        # combination

        for i in possAssigns:  # Loop through each true/false combination
            j = 0

            for k in terminals:  # Fill in the atoms column
                terminals[k] = bool(i[j])
                output[k].append(i[j])
                j += 1

            output['Result'].append(int(self.isTrue(tree)))  # Calculate statement evaluation and fill in the results
            # column

        return output


def rmTO(tree):
    if isinstance(tree, NegOP):
        return NegOP(rmTO(tree.stmt))

    if isinstance(tree, BinOp):  # Apply double implication equivalent

        return BinOp(rmTO(tree.lhs), tree.op, rmTO(tree.rhs))
    if isinstance(tree, TriOp):
        a = rmTO(tree.lhs)
        b = rmTO(tree.mid)
        c = rmTO(tree.rhs)
        return BinOp(BinOp(a, '∧', b), '∨', BinOp(NegOP(a), '∧', c))
    return tree


def rmXOR(tree):
    if isinstance(tree, NegOP):
        return NegOP(rmXOR(tree.stmt))

    if isinstance(tree, BinOp):  # Apply double implication equivalent
        if tree.op == '⊕':
            a = rmXOR(tree.lhs)
            b = rmXOR(tree.rhs)
            return BinOp(BinOp(NegOP(a), '∧', b), '∨', BinOp(NegOP(b), '∧', a))
        return BinOp(rmXOR(tree.lhs), tree.op, rmXOR(tree.rhs))
    return tree


def rmDI(tree):
    if isinstance(tree, NegOP):
        return NegOP(rmDI(tree.stmt))

    if isinstance(tree, BinOp):  # Apply double implication equivalent
        if tree.op == '↔':
            a = rmDI(tree.lhs)
            b = rmDI(tree.rhs)
            return BinOp(BinOp(a, '→', b), '∧', BinOp(b, '→', a))
        return BinOp(rmDI(tree.lhs), tree.op, rmDI(tree.rhs))
    return tree


def rmSI(tree):
    if isinstance(tree, NegOP):
        return NegOP(rmSI(tree.stmt))
    if isinstance(tree, BinOp):  # Apply single implication equivalent
        if tree.op == '→':
            a = rmSI(tree.lhs)
            b = rmSI(tree.rhs)
            return BinOp(NegOP(a), '∨', b)
        return BinOp(rmSI(tree.lhs), tree.op, rmSI(tree.rhs))
    return tree


def rmB(tree):

    # Moving negations inwards
    if isinstance(tree, NegOP):  # First check if negation
        if isinstance(tree.stmt, BinOp):
            if tree.stmt.op == '∨':
                return rmB(BinOp(NegOP(rmB(tree.stmt.lhs)), '∧', NegOP(rmB(tree.stmt.rhs))))  # Swap operator
            else:
                return rmB(BinOp(NegOP(rmB(tree.stmt.lhs)), '∨', NegOP(rmB(tree.stmt.rhs))))  # Swap operator
        else:
            return NegOP(rmB(tree.stmt))

    # If not negation we do nothing, and traverse
    elif isinstance(tree, BinOp):
        return BinOp(rmB(tree.lhs), tree.op, rmB(tree.rhs))
    return tree


def rmN(tree):

    # Remove repeated negations, only one or 0 negations needed in a row
    if isinstance(tree, NegOP):
        if isinstance(tree.stmt, NegOP):
            return rmN(tree.stmt.stmt)

        return NegOP(rmN(tree.stmt))
    if isinstance(tree, BinOp):
        return BinOp(rmN(tree.lhs), tree.op, rmN(tree.rhs))
    if isinstance(tree, TriOp):
        return TriOp(rmN(tree.lhs), rmN(tree.mid), rmN(tree.rhs))
    return tree


def genCNF(tree):
    if isinstance(tree, BinOp):  # Apply distributivity property to statements
        if tree.op == '∨':
            if isinstance(tree.lhs, BinOp):
                if tree.lhs.op == '∧':
                    return BinOp(BinOp(genCNF(tree.lhs.lhs), '∨', genCNF(tree.rhs)), '∧',
                                 BinOp(genCNF(tree.lhs.rhs), '∨', genCNF(tree.rhs)))
            if isinstance(tree.rhs, BinOp):
                if tree.rhs.op == '∧':
                    return BinOp(BinOp(genCNF(tree.lhs), '∨', genCNF(tree.rhs.lhs)), '∧',
                                 BinOp(genCNF(tree.lhs), '∨', genCNF(tree.rhs.rhs)))
            return BinOp(genCNF(tree.lhs), '∨', genCNF(tree.rhs))
        return BinOp(genCNF(tree.lhs), '∧', genCNF(tree.rhs))
    if isinstance(tree, NegOP):
        return NegOP(genCNF(tree.stmt))
    return tree


def makeAtomsSet(tree, set):
    if isinstance(tree, BinOp):
        # Recurse until we just have atoms/ negated atoms
        set.update(makeAtomsSet(tree.lhs, set))
        set.update(makeAtomsSet(tree.rhs, set))
    elif isinstance(tree, NegOP):
        set.add('¬' + tree.stmt)  # Add this to atom set to indicate a negated atom
    else:
        set.add(tree)   # Add this to atom set

    return set


def simDis(tree, seen=[]):
    if isinstance(tree, BinOp):

        lhs, seen = simDis(tree.lhs, seen)
        if seen == 'delete clause':
            return None, seen  # if sub tree is redundant so is whole tree so keep returning delete
        rhs, seen = simDis(tree.rhs, seen)
        if seen == 'delete clause':
            return None, seen  # if sub tree is redundant so is whole tree so keep returning delete

        if lhs is None:
            return rhs, seen  # to delete left return just right
        if rhs is None:
            return lhs, seen  # to delete left return just right
        return BinOp(lhs, '∨', rhs), seen  # No action needed just return

    if isinstance(tree, NegOP):
        if tree.stmt in seen:
            return None, 'delete clause'  # Since we detect a tautology
        tree = '¬' + tree.stmt
    else:
        if '¬' + tree in seen:
            return None, 'delete clause'  # Since we detect a tautology
    if tree in seen:
        return None, seen  # We detect a repeated atom/negated atom, so None tells parent to delete the atom

    seen.append(tree)  # Update seen atoms for future reference
    return tree, seen


def simCon(tree, repeats=[]):
    if isinstance(tree, BinOp):
        if tree.op == '∨':  # If disjunction

            stmt, seen = simDis(tree, [])  # Simplify the disjunction
            if seen == 'delete clause':
                return "Statement is always True", repeats  # we detect disjunction is redundant, so return to parent
                # function this info

            stmtset = makeAtomsSet(stmt, set())  # Convert statement to set of atoms
            for r in repeats:
                if r.issubset(stmtset):  # If this disjunction has been repeated  or is a subset of a previous one
                    # its redundant
                    return "Statement is always True", repeats  # Indicate Redundancy to parent function
            repeats.append(stmtset)  # Add disjunction set to repeats for future reference
            return stmt, repeats
        if tree.op == '∧':

            # Traverse until not 'and' operator
            lhs, repeats = simCon(tree.lhs, repeats)
            rhs, repeats = simCon(tree.rhs, repeats)
            if lhs == "Statement is always True":
                return rhs, repeats  # if we delete the left sub tree, just return the right
            if rhs == "Statement is always True":
                return lhs, repeats  # if we delete the right sub tree, just return the left
            return BinOp(lhs, '∧', rhs), repeats  # Nothing gets deleted, return the statement

    stmtset = makeAtomsSet(tree, set())
    for r in repeats:
        if r.issubset(stmtset):  # Check if this single atom disjunction has been repeated or has been covered in
            # another disjunction
            return "Statement is always True", repeats
    repeats.append(stmtset)
    return tree, repeats


def delReps(tree, repeats):
    if isinstance(tree, BinOp):
        if tree.op == '∧':

            # Traverse the tree until we find something to delete
            lhs = delReps(tree.lhs, repeats)
            rhs = delReps(tree.rhs, repeats)
            if lhs == "Delete":
                return rhs
            if rhs == "Delete":
                return lhs

            # There was nothing to delete so function done
            return BinOp(lhs, '∧', rhs)

    for r in repeats:
        stmtset = makeAtomsSet(tree, set())  # Make set of atoms, where a set is a disjunction
        if r.issubset(stmtset) and r != stmtset:  # If there is a subset the disjunction is redundant, if the sets
            # are equal then don't delete since it is likely this is the only instance and is not a repeat,
            # the repeat of this would have already been removed in equal scenarios
            return "Delete"
    return tree


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
                out += "(" + gen_stmt(tree.lhs) + ")"  # Need brackets since the precedence of sub tree is higher than parent tree
            else:
                out += gen_stmt(tree.lhs)
        else:
            out += gen_stmt(tree.lhs)   # No brackets since it won't make a difference
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


def isEQ(tree):
    a = ast(tree)  # User tree
    bterminals = {}  # terminals of tree to compare
    for c in request.args.get('terminals'):  # Loop through all the terminals in the URL
        bterminals[c] = False  # Set the terminal false
    if not set(a.terminals).issubset(set(bterminals)):  # Check if the terminals are equal
        return False

    a.terminals = bterminals  # Since the terminals can be in different order, we set them the same to ensure we get the same results column

    return hashlib.md5(str(a.printTruthTable()['Result']).encode()).hexdigest() == request.args.get('results')  # Compare the hashes


def convertToCNF(astTree):

    steps = {'Step': [''], 'Statement': [gen_stmt(astTree)]}
    noN = rmN(astTree)
    if gen_stmt(noN) != gen_stmt(astTree):
        steps['Step'].append(' Remove redundant negation(s) ')
        steps['Statement'].append(gen_stmt(noN))
    noTo = rmTO(noN)
    if gen_stmt(noN) != gen_stmt(noTo):
        steps['Step'].append('Remove Ternary operator(s) ')
        steps['Statement'].append(gen_stmt(noTo))
    noNnoTo = rmN(noTo)
    if gen_stmt(noNnoTo) != gen_stmt(noTo):
        steps['Step'].append(' Remove redundant negation(s) ')
        steps['Statement'].append(gen_stmt(noNnoTo))
    noXOR = rmXOR(noNnoTo)
    if gen_stmt(noNnoTo) != gen_stmt(noXOR):
        steps['Step'].append(' Eliminate ⊕')
        steps['Statement'].append(gen_stmt(noXOR))
    noNnoXOR = rmN(noXOR)
    if gen_stmt(noNnoXOR) != gen_stmt(noXOR):
        steps['Step'].append(' Remove redundant negation(s) ')
        steps['Statement'].append(gen_stmt(noNnoXOR))
    noDi = rmDI(noNnoXOR)
    if gen_stmt(noNnoXOR) != gen_stmt(noDi):
        steps['Step'].append(' Eliminate ↔ ')
        steps['Statement'].append(gen_stmt(noDi))
    noSi = rmSI(noDi)
    if gen_stmt(noSi) != gen_stmt(noDi):
        steps['Step'].append(' Eliminate →')
        steps['Statement'].append(gen_stmt(noSi))
    noNnoSi = rmN(noSi)
    if gen_stmt(noNnoSi) != gen_stmt(noSi):
        steps['Step'].append(' Remove redundant negation(s) ')
        steps['Statement'].append(gen_stmt(noNnoSi))
    noB = rmB(noNnoSi)
    if gen_stmt(noB) != gen_stmt(noNnoSi):
        steps['Step'].append('Move ¬ inwards')
        steps['Statement'].append(gen_stmt(noB))
    noNnoB = rmN(noB)
    if gen_stmt(noNnoB) != gen_stmt(noB):
        steps['Step'].append(' Remove redundant negation(s) ')
        steps['Statement'].append(gen_stmt(noNnoB))

    cnf1 = noNnoB
    while True:  # Keep looping to make sure the statement is really in CNF
        cnf = genCNF(cnf1)  # Create a tree that is in CNF
        if gen_stmt(cnf) == gen_stmt(cnf1):
            break
        else:
            steps['Step'].append('Distribute ∨ over ∧')
            steps['Statement'].append(gen_stmt(cnf))

            cnf1 = cnf
    simCNFp = simCon(cnf, [])  # Simplyfy the CNF

    simCNF = delReps(simCNFp[0], simCNFp[1])  # Delete disjunctions that are subsets of others since some
    # can be missed out in simCon

    if gen_stmt(cnf) != gen_stmt(simCNF):
        steps['Step'].append('Simplify CNF')
        steps['Statement'].append(gen_stmt(simCNF))

    pdTable = pd.DataFrame(steps)  # Create a table data structure from truth table dictionary

    return pdTable.head(len(steps['Step'])).to_html(col_space=50, classes='Table', index=False, justify='center')


def genQuestion(difficulty):

    while True:  # Keep making statements until appropriate
        curCNF = genRanTree(difficulty)  # Generate random statement with difficulty parameter
        desc = gen_stmt(curCNF)  # convert tree to text form
        curAST = ast(curCNF)

        terminals = "".join(list(curAST.terminals.keys()))  # Get a list of terminals in a single string
        u_results = curAST.printTruthTable()['Result']  # Get the results column from the statement's truth table
        if 1 in u_results and 0 in u_results and not isCNF(curCNF):  # Only be okay this data if its satisifiable, not a tautolgy and is not already in CNF
            break

    results = hashlib.md5(str(u_results).encode()).hexdigest()  # Hash the results column
    # Redirect to Questions page with relevant question data as URL parameters
    return redirect('/q?difficulty=' + str(
        difficulty) + '&statement=' + desc + '&terminals=' + terminals + '&results=' + results)


def updateStats(stats, difficulty, correctness):

    diffmap = {10: 'very easy', 5: 'easy', 0: 'medium', -5: 'hard', -10: 'very hard'}
    stats[diffmap[difficulty]][correctness] += 1
    with open('stats.json', 'w') as f:
        json.dump(stats, f)

class HomeForm(FlaskForm):
    submit = SubmitField('Analyse Statements')
    ques = SubmitField('Answer Questions')
    les = SubmitField('Course Homepage')


class statementForm(FlaskForm):
    #  Set up buttons and text boxes
    input = StringField(' ')
    submit = SubmitField('Display Truth Table')
    genRan = SubmitField('Generate Random Statement')
    conCNF = SubmitField('Convert to CNF')
    goHome = SubmitField('Return to Homepage')


class QuestionsForm(FlaskForm):
    #  Set up buttons and text boxes
    input = StringField(' ')
    submit = SubmitField('Enter')
    next = SubmitField('Next Question')
    see = SubmitField('See sample solution')
    change = SubmitField('Change Difficulty')
    goHome = SubmitField('Return to Homepage')


class QuestionsDifficultyForm(FlaskForm):
    #  Set up buttons and text boxes
    e1 = SubmitField('Very Easy')
    e2 = SubmitField('Easy')
    submit = SubmitField('Medium')
    h1 = SubmitField('Hard')
    h2 = SubmitField('Very Hard')
    goHome = SubmitField('Return to Homepage')


class LessonsHomeForm(FlaskForm):
    learn = SubmitField('Course Webpage')
    submit = SubmitField('Return to Homepage')


@app.route('/', methods=['POST', 'GET'])
def home():
    form = HomeForm()  # Set up the form features for homepage

    # If a button has been clicked
    if form.validate_on_submit():

        if form.ques.data:  # If its Questions button, redirect the user
            return redirect('/choose_question_difficulty')
        elif form.les.data:
            return redirect('https://course.inf.ed.ac.uk/inf1a')
        else:
            return redirect('/statement_analyser')

    return render_template('home.html', form=form)  # Return the home page but with the new data generated


@app.route('/statement_analyser', methods=['POST', 'GET'])
def statementAnalyser():
    form = statementForm()  # Set up the form features for homepage

    # Make every form output initially empty
    error = desc = ""
    table = steps = None

    # If a button has been clicked
    if form.validate_on_submit():

        try:
            if form.goHome.data:  # Go back to home page if this button clicked
                return redirect("/", code=302)
            if form.genRan.data:  # If its the random statement gen button
                astTree = genRanTree(0)  # Get a random tree
                form.input.data = gen_stmt(astTree)  # Set the textbox to that random statement

            tokens = tokenize(form.input.data)  # Make a list of tokens based on textbox input
            if len(tokens) == 0:
                raise Exception("Input Field is empty")
            parser = Parser(tokens)
            astTree = parser.parse()  # Make a tree from the tokens list

            if form.conCNF.data:  # If the convert to CNF button is clicked
                steps = convertToCNF(astTree)

            # Generate a truth table
            curAST = ast(astTree)
            output = curAST.printTruthTable()
            print(curAST.ASTPrint(astTree))

            # Check whether statement is satisfiable, tautology or unsatisfiable
            if 1 in output['Result']:
                if 0 in output['Result']:
                    desc = "Statement is satisfiable"
                else:
                    desc = "Statement is a tautology"
            else:
                desc = "Statement is inconsistent"

            # Check if print truth table button is clicked
            if form.submit.data:
                result = gen_stmt(astTree)
                output[result] = output.pop('Result')
                pdTable = pd.DataFrame(output)  # Create a table data structure from truth table dictionary

                table = pdTable.head(len(output[result])).to_html(col_space=50, classes='Table')  # Generate HTML
                # code for tables
            else:
                table = None
        except Exception as inst:
            error = str(inst)  # Set error message from exceptions caught

            table = None

    return render_template('statementAnalyser.html', form=form, table=table, error=error, desc=desc,
                           steps=steps)  # Return the home page but with the new data generated


@app.route('/choose_question_difficulty', methods=['POST', 'GET'])
def questionsDifficulty():
    form = QuestionsDifficultyForm()  # Set the form objects
    if form.validate_on_submit():  # If a button has been clicked
        if form.goHome.data:  # Go back to home page if this button clicked
            return redirect("/", code=302)
        difficulty = 0  # Default difficulty (for Medium difficulty)
        if form.e1.data:  # If very easy clicked
            difficulty = 10
        elif form.e2.data:  # If easy clicked
            difficulty = 5
        elif form.h1.data:  # If hard clicked
            difficulty = -5
        elif form.h2.data:  # If very hard clicked
            difficulty = -10
        return genQuestion(difficulty)
    return render_template('questionsDifficulty.html', form=form)


@app.route('/q', methods=['POST', 'GET'])
def questions():

    # Set the form data to be blank except the question
    error = ""
    steps = None
    desc = request.args.get('statement')  # Get the question from URL
    form = QuestionsForm()

    difficulty = int(request.args.get('difficulty'))  # Get the required difficulty from URL
    if form.validate_on_submit():
        try:

            if form.goHome.data:
                return redirect("/", code=302)  # Go to home page
            if form.change.data:
                return redirect('/choose_question_difficulty')  # Change the difficulty
            if form.see.data:  # See the CNF conversion solutions
                parser = Parser(tokenize(desc))  # parse the statement
                astTree = parser.parse()
                steps = convertToCNF(astTree)

            if form.submit.data:  # If enter button is clicked

                tokens = tokenize(form.input.data)  # Get tokens of user input
                if len(tokens) == 0:
                    raise Exception("Input Field is empty")
                parser = Parser(tokens)
                astTree = parser.parse()  # Parse the user input
                with open('stats.json') as f:
                    stats = json.load(f)
                if isCNF(astTree):  # Check if user input is in CNF
                    if isEQ(astTree):  # Check if user input is equivalent to question
                        wrong = ''
                        right = 'Well done, your CNF is correct :)'
                        updateStats(stats, difficulty, 'right')
                    else:
                        updateStats(stats, difficulty, 'wrong')
                        wrong = 'Statement is in CNF but it is not equivalent'
                        right = ''
                else:
                    updateStats(stats, difficulty, 'wrong')
                    right = ''
                    if isEQ(astTree):
                        wrong = 'Statement is equivalent but it is not in CNF'
                    else:
                        wrong = 'Statement is not equivalent and is not in CNF'

                return render_template('questions.html', form=form, desc=desc, wrong=wrong, right=right)
            if form.next.data:  # Go to next question if next question clicked
                return genQuestion(difficulty)

        except Exception as inst:
            error = str(inst)

    return render_template('questions.html', form=form, desc=desc, error=error, steps=steps)


@app.route('/lessonsHome', methods=['POST', 'GET'])
def lessonsHome():
    form = LessonsHomeForm()
    if form.validate_on_submit():
        if form.learn.data:
            return  redirect("https://course.inf.ed.ac.uk/inf1a")
        else:
            return redirect("/", code=302)  # Go to home page

    return render_template('lessonsHome.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
