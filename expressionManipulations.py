from ast_class import *
import pandas as pd

def tree2str(tree):
    pres = {'→': 3, '↔': 4, '∧': 0, '∨': 2, '⊕': 1}  # Keep track of precedences
    if isinstance(tree, NegOP):
        if isinstance(tree.stmt, BinOp):
            return "¬(" + tree2str(tree.stmt) + ")"  # We negate the entire expression
        else:
            return "¬" + tree2str(tree.stmt)  # This negation does not require brackets
    if isinstance(tree, BinOp):
        out = ""
        if isinstance(tree.lhs, BinOp):
            if pres[tree.lhs.op] > pres[tree.op] or pres[tree.lhs.op] > 2 and pres[tree.op] > 2:
                out += "(" + tree2str(
                    tree.lhs) + ")"  # Need brackets since the precedence of sub tree is higher than parent tree
            else:
                out += tree2str(tree.lhs)
        else:
            out += tree2str(tree.lhs)  # No brackets since it won't make a difference
        out += " " + tree.op + " "
        if isinstance(tree.rhs, BinOp):
            if pres[tree.rhs.op] > pres[tree.op] or pres[tree.rhs.op] > 2 and pres[tree.op] > 2:
                out += "(" + tree2str(tree.rhs) + ")"
            else:
                out += tree2str(tree.rhs)
        else:
            out += tree2str(tree.rhs)
        return out
    if isinstance(tree, TriOp):
        return "(" + tree2str(tree.lhs) + " ? " + tree2str(tree.mid) + " : " + tree2str(tree.rhs) + ")"
    else:
        return str(tree)


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

    if isinstance(tree, TriOp):
        return TriOp(rmXOR(tree.lhs), rmXOR(tree.mid), rmXOR(tree.rhs))

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

    if isinstance(tree, TriOp):
        return TriOp(rmDI(tree.lhs), rmDI(tree.mid), rmDI(tree.rhs))

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

    if isinstance(tree, TriOp):
        return TriOp(rmSI(tree.lhs), rmSI(tree.mid), rmSI(tree.rhs))


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


def distribute(op, tree):
    if op == '∧':
        opp_op = '∨'
    else:
        opp_op = '∧'
        
    if isinstance(tree, BinOp):  # Apply distributivity property to expressions
        if tree.op == opp_op:
            if isinstance(tree.lhs, BinOp):
                if tree.lhs.op == op:
                    return BinOp(BinOp(distribute(op, tree.lhs.lhs), opp_op, distribute(op, tree.rhs)), op,
                                 BinOp(distribute(op, tree.lhs.rhs), opp_op, distribute(op, tree.rhs)))
            if isinstance(tree.rhs, BinOp):
                if tree.rhs.op == op:
                    return BinOp(BinOp(distribute(op, tree.lhs), opp_op, distribute(op, tree.rhs.lhs)), op,
                                 BinOp(distribute(op, tree.lhs), opp_op, distribute(op, tree.rhs.rhs)))
            return BinOp(distribute(op, tree.lhs), opp_op, distribute(op, tree.rhs))
        return BinOp(distribute(op, tree.lhs), op, distribute(op, tree.rhs))
    if isinstance(tree, NegOP):
        return NegOP(distribute(op, tree.stmt))
    return tree


def list2con(cons):

    if len(cons) == 1:
        return cons[0]
    else:
        return BinOp(cons[0], '∧', list2con(cons[1:]))


def list2DNF(dnf):

    if len(dnf) == 1:
        return list2con(dnf[0])
    else:
        return BinOp(list2con(dnf[0]), '∨', list2DNF(dnf[1:]))


def simCNF(tree):

    dnf = simDNF(NegOP(tree))
    if dnf == 'Expression is a tautology':
        return 'Expression is inconsistent'
    elif dnf == 'Expression is inconsistent':
        return 'Expression is a tautology'

    return rmN(rmB(NegOP(dnf)))


def findMatch(alist, blist):

    already_matched = False
    out = ''
    for a, b in zip(alist, blist):
        if a == b:
            out += a
            continue
        else:
            if already_matched:
                return None
            already_matched = True
            out += '_'
    return out


def termsEqual(alist, blist):

    for a, b in zip(alist, blist):
        if a != b and a != '_' and b != '_':
            return False
    return True


def terms2Con(terms, atoms):

    out = []
    for t, a in zip(terms, atoms):
        if t == '_':
            continue
        elif t == '1':
            out.append(a)
        else:
            out.append(NegOP(a))

    return list2con(out)


def implicants2DNF(implicants, atoms):

    if len(implicants) == 1:
        return terms2Con(implicants[0], atoms)
    return BinOp(terms2Con(implicants[0], atoms), '∨', implicants2DNF(implicants[1:], atoms))


def simDNF(tree):

    minTerms = []
    astTree = ast(tree)
    tt = astTree.printTruthTable()
    keys = list(tt.keys())[:-1]
    tautology = True
    inconsistent = True
    for i, r in enumerate(tt['Result']):

        if r:
            inconsistent = False
            minTerm = ''
            for k in keys:

                minTerm += str(tt[k][i])
            minTerms.append(minTerm)
        else:
            tautology = False

    if tautology:
        return 'Expression is a tautology'
    elif inconsistent:
        return 'Expression is inconsistent'

    minTerms.sort(key=lambda x: x.count('1'))
    groups = []
    cs = minTerms[0].count('1')
    group = {minTerms[0]}
    for minTerm in minTerms[1:]:
        mtc = minTerm.count('1')
        if mtc > cs:
            groups.append(group)
            group = set()
            cs = mtc
        group.add(minTerm)
    if group:
        groups.append(group)

    prime_implicants = set()

    while groups:

        groups2 = []
        prime_implicants_sub = set().union(*groups)
        for i, g1 in enumerate(groups[:-1]):
            g2 = groups[i+1]
            group = set()
            for mt1 in g1:
                for mt2 in g2:
                    isMatch = findMatch(mt1, mt2)
                    if isMatch is not None:
                        group.add(isMatch)
                        prime_implicants_sub.discard(mt1)
                        prime_implicants_sub.discard(mt2)
            groups2.append(group)
        groups = groups2
        prime_implicants = prime_implicants.union(prime_implicants_sub)

    essential_implicants = set()
    for minTerm in minTerms:
        seen = False
        epi = None
        for pi in prime_implicants:
            if termsEqual(minTerm, pi):
                if seen:
                    break
                seen = True
                epi = pi

        if seen and epi is not None:
            essential_implicants.add(epi)

    return implicants2DNF(list(essential_implicants), keys)


def convertTo(form, astTree, do_presteps=True, return_tree=False, return_tree_and_steps=False):
    if form == 'CNF':
        op = '∧'
        opp_op = ''
    else:
        opp_op = '∧'
        op = '∨'

    steps = {'Step': [''], 'Expression': [tree2str(astTree)]}
    if do_presteps:
        noN = rmN(astTree)
        if tree2str(noN) != tree2str(astTree):
            steps['Step'].append(' Remove redundant negation(s) ')
            steps['Expression'].append(tree2str(noN))
        noTo = rmTO(noN)
        if tree2str(noN) != tree2str(noTo):
            steps['Step'].append('Remove Ternary operator(s) ')
            steps['Expression'].append(tree2str(noTo))
        noNnoTo = rmN(noTo)
        if tree2str(noNnoTo) != tree2str(noTo):
            steps['Step'].append(' Remove redundant negation(s) ')
            steps['Expression'].append(tree2str(noNnoTo))
        noXOR = rmXOR(noNnoTo)
        if tree2str(noNnoTo) != tree2str(noXOR):
            steps['Step'].append(' Eliminate ⊕')
            steps['Expression'].append(tree2str(noXOR))
        noNnoXOR = rmN(noXOR)
        if tree2str(noNnoXOR) != tree2str(noXOR):
            steps['Step'].append(' Remove redundant negation(s) ')
            steps['Expression'].append(tree2str(noNnoXOR))
        noDi = rmDI(noNnoXOR)
        if tree2str(noNnoXOR) != tree2str(noDi):
            steps['Step'].append(' Eliminate ↔ ')
            steps['Expression'].append(tree2str(noDi))
        noSi = rmSI(noDi)
        if tree2str(noSi) != tree2str(noDi):
            steps['Step'].append(' Eliminate →')
            steps['Expression'].append(tree2str(noSi))
        noNnoSi = rmN(noSi)
        if tree2str(noNnoSi) != tree2str(noSi):
            steps['Step'].append(' Remove redundant negation(s) ')
            steps['Expression'].append(tree2str(noNnoSi))
        noB = rmB(noNnoSi)
        if tree2str(noB) != tree2str(noNnoSi):
            steps['Step'].append('Move ¬ inwards')
            steps['Expression'].append(tree2str(noB))
        noNnoB = rmN(noB)
        if tree2str(noNnoB) != tree2str(noB):
            steps['Step'].append(' Remove redundant negation(s) ')
            steps['Expression'].append(tree2str(noNnoB))

        init = noNnoB
    else:
        init = astTree

    result = distribute(op, init)

    while tree2str(result) != tree2str(init):  # Keep looping to make sure the expression is really in CNF

        steps['Step'].append('Distribute ' + opp_op + ' over ' + op)
        steps['Expression'].append(tree2str(result))
        init = result
        result = distribute(op, init)  # Create a tree that is in CNF

    if form == 'CNF':
        result_sim = simCNF(result)
    else:
        result_sim = simDNF(result)

    if return_tree:
        return result_sim
    if tree2str(result) != tree2str(result_sim):
        steps['Step'].append('Simplify ' + form)
        steps['Expression'].append(tree2str(result_sim))
    pdTable = pd.DataFrame(steps)  # Create a table data structure from truth table dictionary
    out = [pdTable.head(len(steps['Step'])).to_html(col_space=50, classes='Table', index=False, justify='center'), result_sim]
    if return_tree_and_steps:
        return out[0], out[1]
    else:
        return out[0]
