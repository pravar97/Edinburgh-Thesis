from generators import *
import pandas as pd


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


def makeAtomsSet(tree):
    atomset = set()
    if isinstance(tree, BinOp):
        # Recurse until we just have atoms/ negated atoms
        atomset.update(makeAtomsSet(tree.lhs))
        atomset.update(makeAtomsSet(tree.rhs))
    else:
        if isinstance(tree, NegOP):
            tree = '¬' + tree.stmt
        atomset.add(tree)   # Add this to atom set
    return atomset


def makeConSet(tree):
    conset = set()
    if isinstance(tree,BinOp):
        if tree.op == '∧':
            conset.update(makeConSet(tree.lhs))
            conset.update(makeConSet(tree.rhs))
            return conset
    tset = makeAtomsSet(tree)

    if not [x for x in tset if '¬' + x in tset]:

        conset.add(frozenset(tset))

    return conset


def set2Dis(stmtset):
    stmtlist = list(stmtset)
    if stmtlist[0][0] == '¬':
        stmtlist[0] = NegOP(stmtlist[0][1])
    if len(stmtlist) == 1:
        return stmtlist[0]
    return BinOp(stmtlist[0], '∨', set2Dis(stmtlist[1:]))


def set2Con(stmtset):
    stmtlist = list(stmtset)
    if not stmtlist:
        return 'Statement is a tautology'
    if len(stmtlist) == 1:
        return set2Dis(stmtlist[0])
    return BinOp(set2Dis(stmtlist[0]), '∧', set2Con(stmtlist[1:]))


def simCNF(tree):

    conset = makeConSet(tree)
    consetlist = list(conset)
    consetlen = len(consetlist)
    for i in range(consetlen):
        for j in range(consetlen):
            if j == i:
                continue
            if consetlist[i].issubset(consetlist[j]):
                conset.remove(consetlist[j])

    return set2Con(conset)


def convertToCNF(astTree, justCNF=False):
    steps = {'Step': [''], 'Statement': [gen_stmt(astTree)]}
    if not justCNF:
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
    else:
        cnf1 = astTree
    while True:  # Keep looping to make sure the statement is really in CNF
        cnf = genCNF(cnf1)  # Create a tree that is in CNF
        if gen_stmt(cnf) == gen_stmt(cnf1):
            break
        else:
            steps['Step'].append('Distribute ∨ over ∧')
            steps['Statement'].append(gen_stmt(cnf))

            cnf1 = cnf

    CNF_sim = simCNF(cnf)

    if gen_stmt(cnf) != gen_stmt(CNF_sim):
        steps['Step'].append('Simplify CNF')
        steps['Statement'].append(gen_stmt(CNF_sim))
    pdTable = pd.DataFrame(steps)  # Create a table data structure from truth table dictionary

    return pdTable.head(len(steps['Step'])).to_html(col_space=50, classes='Table', index=False, justify='center')