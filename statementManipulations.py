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
        print(tset)
        conset.add(frozenset(tset))
    print(conset)
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

def simCon2(tree):

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


def simDis(tree, seen=None):
    if seen is None:
        seen = []
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


def simCon(tree, repeats=None):
    if repeats is None:
        repeats = []
    if isinstance(tree, BinOp):
        if tree.op == '∨':  # If disjunction

            # stmt, seen = simDis(tree, [])  # Simplify the disjunction
            # if seen == 'delete clause':
            #     return "Statement is always True", repeats  # we detect disjunction is redundant, so return to parent
                # function this info

            stmtset = makeAtomsSet(tree)  # Convert statement to set of atoms
            if len([x for x in stmtset if '¬' + x in stmtset]) > 0:
                return "Statement is always True", repeats
            else:
                stmt = set2Dis(stmtset)
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

    stmtset = makeAtomsSet(tree)
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
        stmtset = makeAtomsSet(tree)  # Make set of atoms, where a set is a disjunction
        if r.issubset(stmtset) and r != stmtset:  # If there is a subset the disjunction is redundant, if the sets
            # are equal then don't delete since it is likely this is the only instance and is not a repeat,
            # the repeat of this would have already been removed in equal scenarios
            return "Delete"
    return tree


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
    #simCNFp = simCon(cnf, [])  # Simplyfy the CNF

    #simCNF = delReps(simCNFp[0], simCNFp[1])  # Delete disjunctions that are subsets of others since some
    simCNF = simCon2(cnf)
    # can be missed out in simCon

    if gen_stmt(cnf) != gen_stmt(simCNF):
        steps['Step'].append('Simplify CNF')
        steps['Statement'].append(gen_stmt(simCNF))
    pdTable = pd.DataFrame(steps)  # Create a table data structure from truth table dictionary

    return pdTable.head(len(steps['Step'])).to_html(col_space=50, classes='Table', index=False, justify='center')