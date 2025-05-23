from trees import BinOp, TriOp, NegOP


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
            raise Exception("Syntax Error: Expected " + c + " but received " + token)

    def parse(self):
        output = self.parseStmt()  # Get root node of tree, using LL recursive parsing
        if self.i < len(self.tokens):
            raise Exception("Syntax Error: Additional tokens at end of expression are invalid")
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
            raise Exception("Syntax Error: Unexpected end of expression")
        if token not in ['(', ')', '¬', '∧', '∨', '→', '↔', '?', ':', '⊕']:
            self.i += 1
            return token
        else:
            raise Exception("Syntax Error: Expected Identifier but got " + token)


def tokenize(stream):
    token = ""
    tokens = []
    identcount = 0
    stream = stream.upper()
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

        if c == '\\' and c2 == '/' or c == '|' and c2 == '|':
            if token not in tokens and token:
                identcount += 1
            if identcount > 13:  # Enforce bounds of number of atoms

                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("∨")  # Add operator

            token = ""  # Reset for next atom
            i += 1  # Increment loop counter more to cover additional chars in this notation
        elif c == '+' or c == '∨' or c == '|' or c == 'V':
            if token not in tokens and token:
                identcount += 1
            if identcount > 13:  # Enforce bounds of number of atoms

                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("∨")  # Add operator

            token = ""  # Reset for next atom
        elif c == 'O' and not (' ' + token)[-1].isalpha() and c2 == 'R' and not c3.isalpha():
            if token not in tokens and token:
                identcount += 1
            if identcount > 13:  # Enforce bounds of number of atoms

                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("∨")  # Add operator

            token = ""  # Reset for next atom
            i += 1  # Increment loop counter more to cover additional chars in this notation

        elif c == '/' and c2 == '\\' or c == '&' and c2 == '&':
            if token not in tokens and token:
                identcount += 1
            if identcount > 13:  # Enforce bounds of number of atoms

                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("∧")  # Add operator

            token = ""  # Reset for next atom
            i += 1  # Increment loop counter more to cover additional chars in this notation

        elif c == '.' or c == '*' or c == '∧' or c == '&':
            if token not in tokens and token:
                identcount += 1
            if identcount > 13:   # Enforce bounds of number of atoms

                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("∧")  # Add operator

            token = ""  # Reset for next atom

        elif c == 'A' and not (' ' + token)[-1].isalpha() and c2 == 'N' and c3 == 'D' and not c4.isalpha():
            if token not in tokens and token:
                identcount += 1
            if identcount > 13:   # Enforce bounds of number of atoms

                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("∧")  # Add operator
            token = ""  # Reset for next atom
            i += 2  # Increment loop counter more to cover additional chars in this notation

        elif c == '⊕':
            if token not in tokens and token:
                identcount += 1
            if identcount > 13:  # Enforce bounds of number of atoms

                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("⊕")  # Add operator

            token = ""  # Reset for next atom

        elif c == 'X' and not (' ' + token)[-1].isalpha() and c2 == 'O' and c3 == 'R' and not c4.isalpha():
            if token not in tokens and token:
                identcount += 1
            if identcount > 13:  # Enforce bounds of number of atoms

                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("⊕")  # Add operator
            token = ""  # Reset for next atom
            i += 2  # Increment loop counter more to cover additional chars in this notation

        elif c == '→':
            if token not in tokens and token:
                identcount += 1
            if identcount > 13:  # Enforce bounds of number of atoms

                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("→")  # Add operator

            token = ""  # Reset for next atom

        elif c == '↔':
            if token not in tokens and token:
                identcount += 1
            if identcount > 13:   # Enforce bounds of number of atoms

                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("↔")  # Add operator

            token = ""  # Reset for next atom

        elif c == '<' and (c2 == '-' or c2 == '=') and c3 == '>':
            if token not in tokens and token:
                identcount += 1
            if identcount > 13:   # Enforce bounds of number of atoms

                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("↔")  # Add operator
            i += 2  # Increment loop counter more to cover additional chars in this notation

            token = ""  # Reset for next atom

        elif (c == '-' or c == '=') and c2 == '>':
            if token not in tokens and token:
                identcount += 1
            if identcount > 13:   # Enforce bounds of number of atoms

                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("→")  # Add operator
            i += 1  # Increment loop counter more to cover additional chars in this notation

            token = ""  # Reset for next atom

        elif c == '(':
            if token not in tokens and token:
                identcount += 1
            if identcount > 13:   # Enforce bounds of number of atoms

                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("(")  # Add operator

            token = ""  # Reset for next atom
        elif c == ')':
            if token not in tokens and token:
                identcount += 1
            if identcount > 13:   # Enforce bounds of number of atoms

                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append(")")  # Add operator

            token = ""  # Reset for next atom
        elif c == '?':
            if token not in tokens and token:
                identcount += 1
            if identcount > 13:   # Enforce bounds of number of atoms

                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("?")  # Add operator

            token = ""  # Reset for next atom
        elif c == ':':
            if token not in tokens and token:
                identcount += 1
            if identcount > 13:   # Enforce bounds of number of atoms

                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append(":")  # Add operator

            token = ""  # Reset for next atom
        elif c == '!' or c == '~' or c == '-' or c == '¬':
            if token not in tokens and token:
                identcount += 1
            if identcount > 13:   # Enforce bounds of number of atoms

                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("¬")  # Add operator

            token = ""  # Reset for next atom
        elif c == 'N' and not (' ' + token)[
            -1].isalpha() and c2 == 'O' and c3 == 'T' and not c4.isalpha():
            if token not in tokens and token:
                identcount += 1
            if identcount > 13:   # Enforce bounds of number of atoms

                raise Exception("Too many atoms!")
            tokens.append(token)  # Add atom preceding current operator
            tokens.append("¬")  # Add operator
            token = ""  # Reset for next atom
            i += 2  # Increment loop counter more to cover additional chars in this notation
        elif c.isspace():
            if token not in tokens and token:
                identcount += 1
            if identcount > 13:   # Enforce bounds of number of atoms

                raise Exception("Too many atoms!")

            tokens.append(token)  # Add atom preceding current operator
            token = ""  # Reset for next atom

        else:
            token += c
        i += 1  # Increment loop counter

    if token not in tokens and token:
        identcount += 1
    if identcount > 13:   # Enforce bounds of number of atoms
        raise Exception("Too many atoms!")
    tokens.append(token)  # Add last token
    while "" in tokens:
        tokens.remove("")  # Remove empty tokens
    return tokens