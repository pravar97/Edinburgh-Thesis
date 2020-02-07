from flask import Flask, render_template
import itertools
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap

import pandas as pd

app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

class BinOp:
    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.op = op


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
        if (c == token):
            self.i += 1
        else:
            raise Exception("Expected " + c + " but received " + token)

    def parse(self):
        output = self.parseStmt()
        if (self.i < len(self.tokens)):
            raise Exception("Additional tokens at end of statement are invalid")
        return output

    def parseStmt(self):
        lhs = self.parseStmt1()
        op = self.getToken()
        rhs = self.parseStmtR()
        if rhs is None:
            return lhs
        else:
            return BinOp(lhs, op, rhs)

    def parseStmtR(self):

        token = self.getToken()
        if token == '->' or token == '<->':
            self.parseImp()
            lhs = self.parseStmt1()
            op = self.getToken()
            rhs = self.parseStmtR()
            if rhs is None:
                return lhs
            else:
                return BinOp(lhs, op, rhs)

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
        if token == '|':
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
        if token == '&':
            self.i += 1
            lhs = self.parseStmt3()
            op = self.getToken()
            rhs = self.parseStmt2R()
            if rhs is None:
                return lhs
            else:
                return BinOp(lhs, op, rhs)

    def parseStmt3(self):
        token = self.getToken()
        if token == '~':
            self.i += 1
            return(NegOP(self.parseStmt3()))
        elif token == '(':
            self.i += 1
            output = self.parseStmt()
            self.expect(')')
            return output
        else:
            return self.parseIdent()

    def parseImp(self):
        token = self.getToken()
        if token == '->':
            self.i += 1
        else:
            self.expect('<->')

    def parseIdent(self):
        token = self.getToken()
        if self.end:
            raise Exception("Unexpected end of statement")
        if token not in ['(', ')', '~', '&', '|', '->', '<->']:
            self.i += 1
            return token
        else:
            raise Exception("Expected Identifier but got " + token)


def tokenize(stream):
    token = ""
    tokens = []
    identcount = 0


    i = 0
    while i < len(stream):

        c = stream[i]
        last = i + 1 == len(stream)
        pen = i + 2 == len(stream)
        penpen = i + 3 == len(stream)
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
        if c == '+' or c == '|':
            if token not in tokens:
                identcount += 1
            if identcount > 13:
                raise Exception("Too many atoms!")
            tokens.append(token)
            tokens.append("|")

            token = ""
        elif c.lower() == 'o' and not (' '+token)[-1].isalpha() and c2.lower() == 'r' and not c3.isalpha():
            if token not in tokens:
                identcount += 1
            if identcount > 13:
                raise Exception("Too many atoms!")
            tokens.append(token)
            tokens.append("|")

            token = ""
            i += 1
        elif c == '.' or c == '*' or c == '&':
            if token not in tokens:
                identcount += 1
            if identcount > 13:
                raise Exception("Too many atoms!")
            tokens.append(token)
            tokens.append("&")

            token = ""
        elif c.lower() == 'a' and not (' '+token)[-1].isalpha() and c2.lower() == 'n' and c3.lower() == 'd' and not c4.isalpha():
            if token not in tokens:
                identcount += 1
            if identcount > 13:
                raise Exception("Too many atoms!")
            tokens.append(token)
            tokens.append("&")
            token = ""
            i += 2

        elif c == '(':
            if token not in tokens:
                identcount += 1
            if identcount > 13:
                raise Exception("Too many atoms!")
            tokens.append(token)
            tokens.append("(")

            token = ""
        elif c == ')':
            if token not in tokens:
                identcount += 1
            if identcount > 13:
                raise Exception("Too many atoms!")
            tokens.append(token)
            tokens.append(")")

            token = ""
        elif c == '<' and c2 == '-' and c3 == '>':
            if token not in tokens:
                identcount += 1
            if identcount > 13:
                raise Exception("Too many atoms!")
            tokens.append(token)
            tokens.append("<->")
            i += 2

            token = ""

        elif c == '-' and c2 == '>':
            if token not in tokens:
                identcount += 1
            if identcount > 13:
                raise Exception("Too many atoms!")
            tokens.append(token)
            tokens.append("->")
            i += 1

            token = ""
        elif c == '!' or c == '~' or c == '-':
            if token not in tokens:
                identcount += 1
            if identcount > 13:
                raise Exception("Too many atoms!")
            tokens.append(token)
            tokens.append("~")

            token = ""
        elif c.lower() == 'n' and not (' '+token)[-1].isalpha() and c2.lower() == 'o' and c3.lower() == 't' and not c4.isalpha():
            if token not in tokens:
                identcount += 1
            if identcount > 13:
                raise Exception("Too many atoms!")
            tokens.append(token)
            tokens.append("~")
            token = ""
            i += 2
        elif c.isspace():
            if token not in tokens:
                identcount += 1
            if identcount > 13:
                raise Exception("Too many atoms!")

            tokens.append(token)
            token = ""


        else:
            token += c
        i += 1
    if token not in tokens:
        identcount += 1
    if identcount > 13:
        raise Exception("Too many atoms!")
    tokens.append(token)
    while ("" in tokens):
        tokens.remove("")
    return tokens

class ast:
    def __init__(self, astTree):
        self.astTree = astTree
        self.terminals = {}
        self.sTerminals = {}
        self.treePrint = self.ASTPrint(astTree)
        self.iTable = {}
        self.lhsStr = ""
        self.rhsStr = ""

    def ASTPrint(self, tree):

        global maxTerminalSize
        if isinstance(tree, BinOp):
            return tree.op + "(" + self.ASTPrint(tree.lhs) + "," + self.ASTPrint(tree.rhs) + ")"
        elif isinstance(tree, NegOP):
            return "Negate" + "(" + self.ASTPrint(tree.stmt) + ")"
        else:
            self.terminals[tree] = False


        return str(tree)

    def isTrue(self, tree):
        assignments = self.terminals
        if isinstance(tree, BinOp):
            lhs = self.isTrue(tree.lhs)
            rhs = self.isTrue(tree.rhs)
            if tree.op == '|':
                return lhs or rhs
            elif tree.op == '&':
                return lhs and rhs
            elif tree.op == '->':
                return (not lhs) or rhs
            elif tree.op == '<->':
                return (not lhs or rhs) and (lhs or not rhs)
        elif isinstance(tree, NegOP):
            return not self.isTrue(tree.stmt)
        else:
            self.lhsStr = tree
            if assignments == None:
                self.iTable[self.lhsStr] = int(input("Please enter 1 or 0 to assign value to atom:" + tree + '\n')) == 1
                return int(input("Please enter 1 or 0 to assign value to atom:" + tree + '\n')) == 1
            else:
                return assignments[tree]


    def printTruthTable(self):
        tree = self.astTree
        terminals = self.terminals

        output = {}
        for k in terminals:

            output[k] = []

        output['Result'] = []


        possAssigns = list(itertools.product([0, 1], repeat=len(terminals)))
        for i in possAssigns:
            j = 0

            for k in terminals:

                terminals[k] = bool(i[j])
                output[k].append(i[j])
                j += 1

            output['Result'].append(int(self.isTrue(tree)))

        return output
def rmDI(tree):
    if isinstance(tree, NegOP):

            return NegOP(rmDI(tree.stmt))

    if isinstance(tree, BinOp):
        if tree.op == '<->':
            a = rmDI(tree.lhs)
            b = rmDI(tree.rhs)
            return BinOp(BinOp(NegOP(a), '|', b), '&', BinOp(a, '|', NegOP(b)))
        return BinOp(rmDI(tree.lhs), tree.op, rmDI(tree.rhs))
    return tree

def rmSI(tree):
    if isinstance(tree, NegOP):
        return NegOP(rmSI(tree.stmt))
    if isinstance(tree, BinOp):
        if tree.op == '->':
            a = rmSI(tree.lhs)
            b = rmSI(tree.rhs)
            return BinOp(NegOP(a), '|', b)
        return BinOp(rmSI(tree.lhs), tree.op, rmSI(tree.rhs))
    return tree

def rmB(tree):

    if isinstance(tree, NegOP):
        if isinstance(tree.stmt, BinOp):
            if tree.stmt.op == '|':
                return rmB(BinOp(NegOP(rmB(tree.stmt.lhs)), '&', NegOP(rmB(tree.stmt.rhs))))
            else:
                return rmB(BinOp(NegOP(rmB(tree.stmt.lhs)), '|', NegOP(rmB(tree.stmt.rhs))))
        else:
            return NegOP(rmB(tree.stmt))

    elif isinstance(tree, BinOp):
        return BinOp(rmB(tree.lhs), tree.op, rmB(tree.rhs))
    return tree

def rmN(tree):

    if isinstance(tree, NegOP):
        if isinstance(tree.stmt, NegOP):
            return rmN(tree.stmt.stmt)

        return NegOP(rmN(tree.stmt))
    if isinstance(tree, BinOp):
        return BinOp(rmN(tree.lhs), tree.op, rmN(tree.rhs))
    return tree

def genCNF(tree):

    if isinstance(tree, BinOp):
        if tree.op == '|':
            if isinstance(tree.lhs, BinOp):
                if tree.lhs.op == '&':
                    return BinOp(BinOp(genCNF(tree.lhs.lhs), '|', genCNF(tree.rhs)), '&', BinOp(genCNF(tree.lhs.rhs), '|', genCNF(tree.rhs)))
            if isinstance(tree.rhs, BinOp):
                if tree.rhs.op == '&':
                    return BinOp(BinOp(genCNF(tree.lhs), '|', genCNF(tree.rhs.lhs)), '&', BinOp(genCNF(tree.lhs), '|', genCNF(tree.rhs.rhs)))
            return BinOp(genCNF(tree.lhs), '|', genCNF(tree.rhs))
        return BinOp(genCNF(tree.lhs), '&', genCNF(tree.rhs))
    if isinstance(tree, NegOP):
        return NegOP(genCNF(tree.stmt))
    return tree

def simDis(tree, seen=[]):

    if isinstance(tree, BinOp):

        lhs, seen = simDis(tree.lhs, seen)
        if seen == 'delete clause':
            return None, seen
        rhs, seen = simDis(tree.rhs, seen)
        if seen == 'delete clause':
            return None, seen

        if lhs is None:
            return rhs, seen
        if rhs is None:
            return lhs, seen
        return BinOp(lhs, '|', rhs), seen

    if isinstance(tree, NegOP):
        if tree.stmt in seen:
            return None, 'delete clause'
        tree = '~' + tree.stmt
    else:
        if '~' + tree in seen:
            return None, 'delete clause'
    if tree in seen:
        return None, seen

    seen.append(tree)
    return tree, seen

def simCon(tree, repeats=[]):

    if isinstance(tree, BinOp):
        if tree.op == '|':

            stmt, seen = simDis(tree)
            if seen == 'delete clause':
                return "Statement is always True"
            stmtstr = gen_stmt(stmt)
            if stmtstr in repeats:
                return "Statement is always True", repeats
            repeats.append(stmtstr)
            return stmt, repeats
        if tree.op == '&':

            lhs, repeats = simCon(tree.lhs, repeats)
            rhs, repeats = simCon(tree.rhs, repeats)
            if lhs == "Statement is always True":
                return rhs, repeats
            if rhs == "Statement is always True":
                return lhs, repeats
            return BinOp(lhs, '&', rhs)

    stmtstr = gen_stmt(tree)
    if stmtstr in repeats:
        return "Statement is always True", repeats
    repeats.append(stmtstr)
    return tree, repeats

def gen_stmt(tree):
    pres = {'->':0, '<->':0, '&':1, '|':2}
    if isinstance(tree, NegOP):
        if isinstance(tree.stmt, BinOp):
            return "~("+gen_stmt(tree.stmt)+") "
        else:
            return "~"+gen_stmt(tree.stmt) + " "
    if isinstance(tree, BinOp):
        out = ""
        if type(tree.lhs) == str:
            out += tree.lhs + " "
        elif isinstance(tree.lhs, NegOP):
            out += gen_stmt(tree.lhs) + " "
        elif pres[tree.lhs.op] > pres[tree.op]:
            out += "(" + gen_stmt(tree.lhs) + ") "
        else:
            out += gen_stmt(tree.lhs) + " "
        out += tree.op + " "
        if type(tree.rhs) == str:
            out += tree.rhs + " "
        elif isinstance(tree.rhs, NegOP):
            out += gen_stmt(tree.rhs) + " "
        elif pres[tree.rhs.op] > pres[tree.op]:
            out += "(" + gen_stmt(tree.rhs) + ") "
        else:
            out += gen_stmt(tree.rhs) + " "
        return out
    else:
        return tree + " "


class Statement(FlaskForm):
    input = StringField(' ', validators=[DataRequired()])
    submit = SubmitField('Enter')
    disTT = BooleanField('Display Truth Table')
    disCNF = BooleanField('Display conversion to CNF')


@app.route('/', methods=['POST', 'GET'])
def home():

    form = Statement()

    error = ""
    desc = ""
    s1 = ""
    s2 = ""
    s3 = ""
    s4 = ""
    if form.validate_on_submit():


        try:
            tokens = tokenize(form.input.data)
            parser = Parser(tokens)
            astTree = parser.parse()
            noDI = rmN(rmDI(astTree))
            noSI = rmN(rmSI(noDI))
            noB = rmN(rmB(noSI))

            cnf1 = noB
            while True:
                cnf = genCNF(cnf1)
                if gen_stmt(cnf) == gen_stmt(cnf1):
                    break
                else:

                    cnf1 = cnf
            if form.disCNF.data:
                s1 = '1. Eliminate   <->    : ' + gen_stmt(noDI)
                s2 = '2. Eliminate    ->    : ' + gen_stmt(noSI)
                s3 = '3. Move  ~   inwards  : ' + gen_stmt(noB)
                s4 = '4. Distribute | over & : ' + gen_stmt(simCon(cnf, [])[0])
            curAST = ast(astTree)
            output = curAST.printTruthTable()
            pdTable = pd.DataFrame(output)
            if True in output['Result']:
                if False in output['Result']:
                    desc = "Statement is satisfiable"
                else:
                    desc = "Statement is a tautology"
            else:
                desc = "Statement is unsatisfiable"
            if form.disTT.data:
                table = pdTable.head(len(output['Result'])).to_html(col_space=50, classes='Table')
            else:
                table = None
        except Exception as inst:
            error = str(inst)

            table = None
    else:
        table = None
    return render_template('home.html', form=form, table=table, error=error, desc=desc, s1=s1, s2=s2, s3=s3, s4=s4)

if __name__ == '__main__':
	app.run(debug=True)