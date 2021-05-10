import logging
import os
from collections.abc import Iterable

import numpy as np
from sympy import symbols, simplify
from sympy.logic.boolalg import And,Or, Not, Implies, Equivalent, distribute_and_over_or, distribute_or_over_and, is_cnf,to_cnf

logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "INFO"),
    format='%(levelname)s: %(message)s'
)


def Biconditional(a,b):
    """
    rewrite biconditional as a new premise consisting of two implies according to formula in Peter Norvig & Stuart Russel Chapter 7
    replacing alpha <=> beta with (alpha => beta) and (beta => alpha)
    """
    return And(Implies(a,b),Implies(b,a))

def dissociate(op, args):
    """Given an associative op, return a flattened list result such
    that Expr(op, *result) means the same as Expr(op, *args).
    >>> dissociate('&', [A & B])
    [A, B]
    """
    result = []

    def collect(subargs):
        for arg in subargs:
            if arg.func == op:
                collect(arg.args)
            else:
                result.append(arg)

    collect(args)
    return result

def associate(op, args):
    """Given an associative op, return an expression with the same
    meaning as Expr(op, *args), but flattened -- that is, with nested
    instances of the same op promoted to the top level.
    >>> associate('&', [(A&B),(B|C),(B&C)])
    (A & B & (B | C) & B & C)
    >>> associate('|', [A|(B|(C|(A&B)))])
    (A | B | C | (A & B))
    """
    args = dissociate(op, args)
    
    if len(args) == 0:
        return op.identity
    elif len(args) == 1:
        return args[0]
    else:
        return op(*args)

def remove_all(item, seq):
    """Return a copy of seq (or string) with all occurrences of item removed."""
    if isinstance(seq, str):
        return seq.replace(item, '')
    elif isinstance(seq, set):
        rest = seq.copy()
        rest.remove(item)
        return rest
    else:
        return [x for x in seq if x != item]

def PL_resolution(premises,alpha):
    alpha = to_cnf(~alpha)
    alpha = dissociate(And,[alpha])
    clauses = alpha
    for i in premises:
        clauses += dissociate(And,[i])
    new = set()
    while True:
        n = len(clauses)
        pairs = [(clauses[i], clauses[j])
                for i in range(n) for j in range(i + 1, n)]
        for (ci, cj) in pairs:
            resolvents = PL_resolve(ci, cj)
            if False in resolvents:
                return True
            new = new.union(set(resolvents))
        if new.issubset(set(clauses)):
            return False
        for c in new:
            if c not in clauses:
                clauses.append(c)

def PL_resolve(ci,cj):
    clauses = []
    ci = dissociate(Or, [ci]) #Disjuncts
    cj = dissociate(Or, [cj]) #Disjuncts
    for di in ci:
        for dj in cj:
            if di == ~dj:
                clauses.append(associate(Or, list(set(remove_all(di, ci) + remove_all(dj, cj)))))
    return clauses
def satisfiable(expr, algorithm=None, all_models=False):
    """Check satisfiability of a propositional sentence. Returns a model when it succeeds.
    XXX TODO: Only for testing purposes. We cannot use this library, we must implement this ourselves.
    """
    from sympy.logic.inference import satisfiable as spsatisfiable
    return spsatisfiable(expr, algorithm=algorithm, all_models=all_models)

def get_remainders(beliefs, formula):
    """Return a set of remainders (subsets) of the KB that do not imply the given formula.
    The return value is a set of sets.
    """
    associated = associate(And, beliefs | set([Not(formula)]))
    if satisfiable(associated):
        logging.debug(f'Formula {Not(formula)} satisfiable with {beliefs}')
        return set([frozenset(beliefs)]) # Using frozenset to be able to nest a set into a set
    logging.debug(f'Formula {Not(formula)} not satisfiable with {beliefs}')
    all_remainders = set()
    for belief in beliefs:
        # Recursively test all possible subsets by removing one belief at a time
        remainders_excluding_belief = get_remainders(beliefs - set([belief]), formula)
        for remainder in remainders_excluding_belief:
            if remainder:
                all_remainders.add(remainder)
    return all_remainders


class Knowledge_base():
    """ Knowledge base is a set of sentences, where sentence refer to an assertions that we believe to be true in the world
    proposition symbol true or false
    complex sentences consists of propositional symbols and logical connectives
    
    """
    def __init__(self):
        self.premises = self.fetch_initial_axioms()

    def fetch_initial_axioms(self):
        """"
        Example premises is from exercises from lecture 9
        """
        p, q, s, r = symbols("p q s r")
        premises = [Implies(Not(p),q),Implies(q,p),Implies(p,And(r,s))]
        premises = [to_cnf(prem) for prem in premises]
        ranks = np.arange(len(premises))
        return list(zip(premises,ranks))

    def fetch_sample_thesis(self):
        """"
        Example premises is from exercises from lecture 9.
        Thesis should end up with empty resolution, hence be True.
        """
        p, q, s, r = symbols("p q s r")
        return And(p,And(s,r))

    def add_premise(self,sentence,rank):
        if is_cnf(sentence):
            self.premises.append((sentence,rank))
        else:
            self.premises.append((to_cnf(sentence), rank))



    def to_clauses(self,premises=None):
        """
        OBS: DOES NOT WORK YET!  

        turn premises into disjunctions of literals
        """
        clauses = []
        if not premises: #Performs on KB
            premises = self.premises
        for prem in premises:
            if prem[0].func == And:
                for clause in prem[0].args:
                    clauses.append(clause)
            else:
                clauses.append(prem[0])
        return clauses

    def contract(self, formula):
        max_remainder_length = 0
        new_beliefs = None

        # remove from the KB formulas identical to the one being contracted
        self.premises[:] = [premise for premise in self.premises if premise[0] != formula]

        # get a set of belief sets that do not imply the formula being contracted
        all_remainders = get_remainders(
            {premise[0] for premise in self.premises},
            formula
        )
        print(f'\n--  Possible remainders  --')
        for remainder in all_remainders:
            if isinstance(remainder, Iterable):
                print(set(remainder))
            else: # just watching out for bugs
                raise TypeError(f'Received type {type(remainder)} instead of Iterable: {remainder}')
            if len(remainder) > max_remainder_length:
                new_beliefs = remainder
                max_remainder_length = len(remainder)
        print(f'---------------------------')
        print(f'--   Chosen remainder    --')
        print(f'{set(new_beliefs)}')
        print(f'---------------------------\n')

    def __repr__(self):
        output = '=============  KB  ===============\n'
        for premise in sorted(self.premises, key=lambda x: float(x[1])):
            output += f' ({premise[1]:.2f}) {premise[0]}\n'
        return output + '=================================='


def main1():
    KB = Knowledge_base()

    #Use sympy to return boolean value
    x,y,r,s = symbols("x y r s")
    ###Resolve test
    alpha = KB.fetch_sample_thesis()
    premises = []
    for premis in KB.premises:
        premises += [premis[0]]
    print("Resolution: ",PL_resolution(premises,alpha))
    
    exp = Implies(x,y)
    print(exp.subs(x, False))

    #Example add a premise to KB
    [print(f"rank {prem[1]} {prem[0]}") for prem in KB.premises]
    KB.add_premise(exp,5)
    print("#"*20)
    [print(f"rank {prem[1]} {prem[0]}") for prem in KB.premises]
    print("#" * 20)

    #Try to make to_clause function to work with example from book:
    """Example from book: Chapter 7.5.2 Proof by resolution (book version 4), subsection "Conjunctive normal form"
    B1, 1 ⇔ (P1, 2 ∨ P2, 1) should be turned into 3 clauses:
    (¬B1, 1 ∨ P1, 2 ∨ P2, 1) ∧ (¬P1, 2 ∨ B1, 1) ∧ (¬P2, 1 ∨ B1, 1)
    """
    b1, p1, p2 = symbols("b1 p1 p2")
    s = symbols("s")
    exp1 = Biconditional(b1, Or(p1, p2))
    exp2 = Or(s, s)
    ranks = np.arange(2)
    premises = [to_cnf(exp) for exp in [exp1, exp2]]
    init_exp = list(zip(premises, ranks))
    clauses = KB.to_clauses(init_exp)
    print(clauses)

    print('CONTRACTION')
    print(KB)
    KB.contract(s)
    print(KB)


if __name__ == "__main__":
    main1()