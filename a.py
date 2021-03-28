from ast_class import *
from expressionPreProcessing import *
from expressionManipulations import *
from generators import *
a = set()
a = a.intersection({1})
print(a)
if a:
    print(1)
# for _ in range(100):
#     print(gen_stmt(genRanCon(list('abcd'))))
p = Parser(tokenize(' ¬c ∧ b ∧ a ∨ ¬d ∨ ¬b '))
tree = p.parse()
print(tree2str(simDNF(tree)))

