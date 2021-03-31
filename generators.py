from expressionManipulations import *
from expressionCheckers import *
import random

def genRanTree(s=12):
    if s <= 1:
        return random.choice('PQRSABCDEF')  # Randomly select an atom
    op_choices = [('NegOP', 1)]
    if s >= 4:
        op_choices += [('BinOp', 2, '∨'), ('BinOp', 2, '∧')]
    if s >= 5:
        op_choices.append(('BinOp', 3, '→'))
    if s >= 11:
        op_choices.append(('TriOp', 7))
    if s >= 12:
        op_choices += [('BinOp', 8, '↔'), ('BinOp', 8, '⊕')]
    op = random.choice(op_choices)
    s -= op[1]
    if op[0] == 'NegOP':
        return NegOP(genRanTree(s))
    elif op[0] == 'TriOp':
        k = random.randint(1, (s - 2)//2)
        m = random.randint(1, s - 2 * k - 1)
        a = genRanTree(k)
        b = genRanTree(s - 2 * k - m)
        c = genRanTree(m)
        return TriOp(a, b, c)
    elif op[2] in '∨∧→':
        k = random.randint(1, s - 1)
        a = genRanTree(k)
        b = genRanTree(s - k)
        return BinOp(a, op[2], b)
    else:
        k = random.randint(1, (s - 1)//2)
        a = genRanTree(k)
        b = genRanTree((s - k)//2)
        return BinOp(a, op[2], b)



# def genRanTree(s):
#     if s > 19:  # Base case: return a single atom
#         return 'PQRSABCDEF'[random.randint(0, 9)]  # Randomly select an atom
#     elif s > 14:
#         return NegOP('PQRSABCDEF'[random.randint(0, 9)])
#     elif s > 13:
#         ran = random.randint(0, 2)
#     elif s > 6:
#         ran = random.randint(0, 3)
#     elif s > 0:
#         ran = random.randint(0, 5)
#     else:
#         ran = random.randint(0, 6)
#
#     if ran == 6:
#         a = genRanTree(s + 20)
#         b = genRanTree(s + 20)
#         c = genRanTree(s + 20)
#         return TriOp(a, b, c)
#     elif ran > 3:
#         a = genRanTree(s + 14)
#         b = genRanTree(s + 14)
#         return BinOp(a, ['↔', '⊕'][ran % 2], b)
#     elif ran == 3:
#         a = genRanTree(s + 7)
#         b = genRanTree(s + 7)
#         return BinOp(a, '→', b)
#     elif ran > 0:
#         a = genRanTree(s + 6)
#         b = genRanTree(s + 6)
#         return BinOp(a, ['∨', '∧'][ran % 2], b)
#     else:
#         return NegOP(genRanTree(s + 1))


def genQuestion(difficulty):
    choice = random.randint(0,2)
    if not choice:
        return genTruthTable(difficulty)
    elif choice == 1:
        return genKmap(difficulty)
    curTree = genRanTree(difficulty)
    while isEQ(curTree, BinOp('a', '∨', NegOP('a'))) \
            or isEQ(curTree, BinOp('a', '∧', NegOP('a'))) \
            or is_in_form('CNF', curTree)\
            or is_in_form('DNF', curTree):
        curTree = genRanTree(difficulty)
    print(tree2str(curTree))
    return curTree, 'sm'


def genTruthTable(difficulty):
    numAtoms = {5: 2, 10: 2, 15: 3, 20: 4, 25: 4}[difficulty]
    output = {}
    for k in 'ABCD'[:numAtoms]:
        output[k] = []  # Make columns for truth table

    output['Result'] = []

    possAssigns = list(itertools.product([0, 1], repeat=numAtoms))  # Make a list of every true/false
    # combination

    for i in possAssigns:  # Loop through each true/false combination
        j = 0

        for k in 'ABCD'[:numAtoms]:  # Fill in the atoms column
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
    solutionCNF = simCNF(solution)
    solutionDNF = simDNF(solution)
    if len(tree2str(solutionCNF)) > len(tree2str(solutionDNF)):
        solution = solutionDNF
    else:
        solution = solutionCNF
    pdTable = pd.DataFrame(output)  # Create a table data structure from truth table dictionary
    table = pdTable.head(len(output['Result'])).to_html(col_space=50, classes='Table')  # Generate HTML

    return table, solution, 'tt'


def makeSeq(l):
    if l == 2:
        return ['0', '1']
    subseq = makeSeq(l/2)
    seq = ['0' + x for x in subseq]
    subseq.reverse()
    seq += ['1' + x for x in subseq]
    return seq


def genMinTerms(tree):
    minTerms = set()
    astTree = ast(tree, keys='ABCD')
    tt = astTree.printTruthTable()
    keys = list(tt.keys())[:-1]

    for i, r in enumerate(tt['Result']):
        if r:
            minTerm = ''
            for k in keys:
                minTerm += str(tt[k][i])
            minTerms.add(minTerm)

    return minTerms


def genRanCon(atoms):

    i = random.randint(0, 1)
    if i:
        a = NegOP(atoms[0])
    else:
        a = atoms[0]
    if not len(atoms) - 1:
        return a
    return BinOp(a, '∧', genRanCon(atoms[1:]))


def makeDNF(difficulty):

    if not difficulty:
        seps = random.randint(1, 3)
        a = genRanCon('ABCD'[:seps])
        b = genRanCon('ABCD'[seps:])
        return BinOp(a, '∨', b)
    else:

        chars = random.sample('ABCD', k=random.randint(1,4))
        used = set(chars)
        a = genRanCon(chars)
        aminTerms = genMinTerms(a)
        while True:
            chars = random.sample('ABCD', k=random.randint(1, 4))
            b = genRanCon(chars)
            bminTerms = genMinTerms(b)
            if bminTerms ^ aminTerms:
                used = used.union(chars)
                break
        while True:
            chars = random.sample('ABCD', k=random.randint(1, 4)) + [x for x in 'ABCD' if x not in used]
            c = genRanCon(chars)
            cminTerms = genMinTerms(c)
            if cminTerms ^ aminTerms and cminTerms ^ bminTerms:
                break

    return BinOp(a, '∨', BinOp(b, '∨', c))


def kmap2tree(kmap, rows, cols, rowkeys):

    dislist = []
    for i, k in enumerate(kmap):
        for j, v in enumerate(kmap[k]):
            if v:
                conlist = []
                for code, atom in zip(rowkeys[j] + k, rows + cols):
                    if int(code):
                        conlist.append(atom)
                    else:
                        conlist.append(NegOP(atom))
                dislist.append(conlist)

    return list2DNF(dislist)


def genKmap(difficulty):

    if difficulty not in {15, 20}:
        numAtoms = {5: 2, 10: 3, 25: 4}[difficulty]
        atoms = 'ABCD'[:numAtoms]
        numrows = len(atoms) // 2
        numcols = len(atoms) - numrows
        colatoms = atoms[numrows:]
        rowatoms = atoms[:numrows]

        kmap = {}
        rowkeys = ['0']
        if numrows > 0:
            rowkeys = makeSeq(2 ** numrows)
        colkeys = makeSeq(2 ** numcols)
        inconsistent = tautology = True
        for c in colkeys:
            kmap[c] = []
            for r in rowkeys:
                v = random.randint(0, 1)
                kmap[c].append(v)
                if v:
                    inconsistent = False
                else:
                    tautology = False

        if inconsistent:
            kmap[random.choice(colkeys)][random.randint(0, len(rowkeys)-1)] = 1
        elif tautology:
            kmap[random.choice(colkeys)][random.randint(0, len(rowkeys)-1)] = 0
        tree = kmap2tree(kmap, rowatoms, colatoms, rowkeys)
    else:
        tree = makeDNF(difficulty)
        astTree = ast(tree)
        kmap, rowkeys, rowatoms, colatoms = astTree.printKMap()

    pdTable = pd.DataFrame(kmap, index=rowkeys)
    table = '<p style="font-size:20pt; font-width:900; position: absolute; margin-right: ' + str(
        50 + len(kmap) * 25) + 'px; right: ' \
                               '50vw; top: ' + str(160 + len(rowkeys) * 10.4) + 'px;">' + ''.join(rowatoms) + '</p> '
    table += '<p style="font-size:20pt; font-width:900;">' + ''.join(colatoms) + '</p> '
    table += pdTable.head(len(rowkeys)).to_html(col_space=50, classes='Table', index=len(rowkeys) > 1)
    return table, simDNF(tree), 'km'
