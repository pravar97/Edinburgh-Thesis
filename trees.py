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