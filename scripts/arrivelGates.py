import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



from scripts import makeTransitions, utils

TOTAL_GATES = 4
SIZE_ORDER = ["X1", "X2", "X4", "X8"]
curente_stage = ["X1"] * TOTAL_GATES

mt = makeTransitions.Make_transitions(SIZE_ORDER)

transitions = mt.transitions(curente_stage)

def oposite_transition(gate: int, curente_stage: list):
    

print("Transições geradas:")
for t in transitions:
    pass