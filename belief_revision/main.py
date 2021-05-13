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
   # >>> dissociate('&', [A & B])
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
    #>>> associate('&', [(A&B),(B|C),(B&C)])
    (A & B & (B | C) & B & C)
    #>>> associate('|', [A|(B|(C|(A&B)))])
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
    resolution = PL_resolution(beliefs, Not(formula))
    is_satisfiable = satisfiable(
        associate(And, beliefs | set([Not(formula)]))
    )
    if is_satisfiable != resolution:
        logging.warning(f'PL_resolution({beliefs}, {Not(formula)})={resolution} HOWEVER satisfiable={is_satisfiable}')
    else:
        logging.debug(f'PL_resolution({beliefs}, {Not(formula)})={resolution} AGREES with satisfiable={is_satisfiable}')
    # if resolution:
    if is_satisfiable:
        logging.debug(f'Formula {Not(formula)} is satisfiable with {beliefs}')
        return set([frozenset(beliefs)]) # Using frozenset to be able to nest a set into a set
    logging.debug(f'Formula {Not(formula)} is not satisfiable with {beliefs}')
    all_remainders = set()
    #Todo MADS: We want to keep beliefs with higher epistemic entrenchment. In order for us to use the entrenchment based contraction,
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

    def fetch_premises(self):
        return [premise[0] for premise in self.premises]
    def fetch_ranks(self):
        return [premise[1] for premise in self.premises]
    def fetch_initial_axioms(self):
        """"
        Example premises is from exercises from lecture 9
        """
        p, q, s, r = symbols("p q s r")
        premises = [Implies(Not(p),q),Implies(q,p),Implies(p,And(r,s))]
        # premises = [p, q, r, Implies(p,q), Implies(q,r)]
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

    def update_rank_of_existing_premise(self,sentence,rank,premises, ranks):
        """
        User tried to add a premise already in KB. User can either update it or leave it be.
        :param sentence: premise
        :param rank: user input rank (The potential new rank)
        :param premises:  [premise[0] for premise in self.premises]
        :param ranks:   [premise[1] for premise in self.premises]
        :return:
        """
        premise_idx = np.where(np.array(premises) == to_cnf(sentence))[0][0]
        print("Premise is already in knowledge base with rank {}".format(ranks[premise_idx]))
        update = input("Would you like to update the rank with {}. \n Type 'y' for yes and 'n' for no".format(rank))
        while update not in ['y', 'n']:
            update = input("Your input is not valid. Type 'y' for yes and 'n' for no")
        if update == "y":
            self.premises.remove(self.premises[premise_idx])
            self.premises.append((sentence, rank))

    def add_premise(self,sentence,rank):
        """
        :param sentence: sentence to be added
        :param rank: rank corresponding to sentence.
        :return:
        """
        assert isinstance(rank,float) or isinstance(rank,int), "rank is not of the right type: {0}".format(type(rank))
        premises = self.fetch_premises()
        ranks =  self.fetch_ranks

        if not is_cnf(sentence):
            sentence = to_cnf(sentence)

        if sentence in premises:
            self.update_rank_of_existing_premise(sentence,rank,premises,ranks)
        else:
            self.premises.append((sentence,rank))


    def check_dominance(self,automatically_fix_weights = False):
        """
        Check to see whether premises fulfils the third epistemic postulate (Dominance):
        if p |= q, then p <= q.
        If p entails q, then q has larger or equal epistemic entrenchment
        """
        for idx_1,premise1,rank1 in enumerate(self.premises):
            for idx_2,premise2,rank2 in enumerate(self.premises):
                if premise1 != premise2:
                    entails = PL_resolution(premise1,premise2)
                    if entails:
                        if not rank1 < rank2:
                            if not automatically_fix_weights:
                                print("Dominance postulate is violated")
                                stop = self.adjust_weights_for_dominance(automatically_fix_weights,idx_1, idx_2, rank1, rank2)
                                if stop:
                                    return
                            else:
                                self.adjust_weights_for_dominance(True,idx_1,idx_2,rank1,rank2)

    def adjust_weights_for_dominance(self,automatically_fix_weights, idx_1,idx_2,rank1,rank2):
        if automatically_fix_weights == False:
            adjust = input("Do you want to automatically adjust weights to satisfy dominance postulate.\n Type 'y' for yes and 'n' for no")
            while adjust not in ['y', 'n']:
                adjust = input("Your input is not valid. Type 'y' for yes and 'n' for no")
            if adjust == 'y':
                self.premises[idx_2][1] += abs(rank1-rank2)
                self.check_dominance(automatically_fix_weights = True)
            return False
        else:
            self.check_dominance(automatically_fix_weights=True)


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

    def rank_function

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
        [print(belief) for belief in new_beliefs]
        # print(f'{set(new_beliefs)}')
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
    print(KB)
    KB.add_premise(exp,"2")
    print(KB)
    KB.add_premise(exp,4)
    print(KB)

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

def main2():
    print('CONTRACTION')
    p, q, r = symbols('p q r')
    KB = Knowledge_base()
    print(KB)
    KB.contract(p)
    print(KB)


if __name__ == "__main__":
    main1()
    #main2()
