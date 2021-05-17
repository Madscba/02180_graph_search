import logging
import os
from collections.abc import Iterable

import numpy as np
from sympy import symbols, Symbol
from sympy.logic.boolalg import And, Or, Not, Implies, is_cnf, to_cnf

logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "INFO"),
    format='%(levelname)s: %(message)s'
)


def Biconditional(a, b):
    """
    rewrite biconditional as a new premise consisting of two implies according to formula in Peter Norvig & Stuart Russel Chapter 7
    replacing alpha <=> beta with (alpha => beta) and (beta => alpha)
    """
    return And(Implies(a, b), Implies(b, a))

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
    #>>> associate(And, [(A&B),(B|C),(B&C)])
    (A & B & (B | C) & B & C)
    #>>> associate(Or, [A|(B|(C|(A&B)))])
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

def PL_resolution(premises, alpha):
    alpha = to_cnf(alpha)
    if isinstance(alpha,list):
        alpha = dissociate(And,alpha)
    else:
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
                return False
            new = new.union(set(resolvents))
        if new.issubset(set(clauses)):
            return True
        for c in new:
            if c not in clauses:
                clauses.append(c)

def PL_resolve(ci, cj):
    clauses = []
    ci = dissociate(Or, [ci]) #Disjuncts
    cj = dissociate(Or, [cj]) #Disjuncts
    for di in ci:
        for dj in cj:
            if di == ~dj:
                resolve = [associate(Or,list(set(remove_all(di, ci) + remove_all(dj, cj))))]
                clauses+= resolve
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
    if isinstance(is_satisfiable,dict) != resolution:
        logging.warning(f'PL_resolution({beliefs}, {Not(formula)})={resolution} HOWEVER satisfiable={is_satisfiable}')
    else:
        logging.debug(f'PL_resolution({beliefs}, {Not(formula)})={resolution} AGREES with satisfiable={is_satisfiable}')
    if resolution:
    # if is_satisfiable:
        logging.debug(f'Formula {Not(formula)} is satisfiable with {beliefs}')
        return set([frozenset(beliefs)]) # Using frozenset to be able to nest a set into a set
    logging.debug(f'Formula {Not(formula)} is not satisfiable with {beliefs}')
    all_remainders = set()
    for belief in beliefs:
        # Recursively test all possible subsets by removing one belief at a time
        remainders_excluding_belief = get_remainders(beliefs - set([belief]), formula)
        for remainder in remainders_excluding_belief:
            if remainder:
                all_remainders.add(remainder)
    maximal_remainders = set()
    for candidate_remainder in all_remainders:
        is_maximal = True
        for another_remainder in all_remainders:
            if another_remainder == candidate_remainder:
                continue
            if candidate_remainder.issubset(another_remainder):
                is_maximal = False
                logging.debug('Remainder {} is subset of {}'.format(
                    candidate_remainder,
                    another_remainder
                ))
                break
        if is_maximal:
            logging.debug('Remainder {} is maximal'.format(candidate_remainder))
            maximal_remainders.add(candidate_remainder)
    return maximal_remainders


class Knowledge_base():
    """ Knowledge base is a set of sentences, where sentence refer to an assertions that we believe to be true in the world
    proposition symbol true or false
    complex sentences consists of propositional symbols and logical connectives
    
    """
    def __init__(self):
        self.alpha = 1 #entailment weight (used in evaluation of premise)
        self.beta = 2 #literal length weight (used in evaluation of premise)
        self.premises = []

    def reset(self):
        self.premises = []

    def fetch_premises(self):
        return [premise[0] for premise in self.premises]

    def fetch_ranks(self):
        return [premise[1] for premise in self.premises]

    def update_ranks_of_existing_premises(self, premises):
        """
        Calculate ranks of premises, and return updated ranks
        """
        return [self.alpha * self.count_entailment(premises,premise) + self.beta / self.count_literals(premise) for premise in premises]

    def add_premise(self, sentence):
        """
        :param sentence: sentence to be added
        :param rank: rank corresponding to sentence.
        :return:
        """
        premises = self.fetch_premises()

        if not PL_resolution(premises, sentence):
            logging.error(f'{sentence} would introduce a contradiction in the KB, skipping. Consider using revision instead.')
            return

        premises.append(sentence)
        updated_ranks = self.update_ranks_of_existing_premises(premises)
        self.premises = [(belief,rank) for belief,rank in zip(premises,updated_ranks)] #zip updated ranks and premises and store in


    def count_entailment(self, original_KB, sentence):
        entailment_count = 0
        for belief in original_KB:
            if not PL_resolution([sentence],Not(belief)): #If the negated belief is not satisfiable, then it must follow from the sentence.
                entailment_count +=1
        return entailment_count

    def count_literals(self, belief):
        return len(belief.binary_symbols)

    def selection_function(self, original_KB, remainders):
        """
        Takes in one or several remainders. Evaluates each of the remainders by summing over the value each of its beliefs. A value for a belief depends on its complexity and entrenchment.
        From the two best remainders we will find the intersection, which corresponds to the partial meet contraction of the original belief set.
        (if only a single remainder is given as input argument, This single remainder will be returned.
        :param remainders:
        :return:
        """
        remainder_scores = []
        for remainder in remainders:
            temp_remainder_score = 0
            for belief in remainder:
                temp_remainder_score +=  self.alpha * self.count_entailment(original_KB,belief) + self.beta / self.count_literals(belief)
            remainder_scores.append(temp_remainder_score)
        logging.debug('Remainders: {}'.format(remainders))
        logging.debug('Remainder scores: {}'.format(remainder_scores))
        remainders_ranks = np.argsort(remainder_scores)
        first_remainder = [remainder for idx,remainder in enumerate(remainders) if idx == np.where(remainders_ranks==0)[0][0]]
        second_remainder = [remainder for idx,remainder in enumerate(remainders) if idx == np.where(remainders_ranks==1)[0][0]]
        logging.debug("Remainder ranks: {}".format(remainders_ranks))
        new_KB = self.partial_meet(first_remainder,second_remainder)
        ranks = [self.alpha * self.count_entailment(original_KB,belief) + self.beta / self.count_literals(belief) for belief in new_KB]
        return [(belief,rank) for belief,rank in zip(new_KB,ranks)]

    def partial_meet(self, set1, set2):
        """
        Return intersection of two best remainders.
        :param set1:
        :param set2:
        :return:
        """
        if isinstance(set1, list):
            set1 = set1[0]
        if isinstance(set2, list):
            set2 = set2[0]
        partial_meet = set1 & set2
        if len(partial_meet) == 0: #if intersection is empty, then return remainder with highest value
            return set1
        return set1 & set2

    def contract(self, formula):
        # remove from the KB formulas identical to the one being contracted
        self.premises[:] = [premise for premise in self.premises if premise[0] != formula]

        # get a set of belief sets that do not imply the formula being contracted
        all_remainders = get_remainders(
            {premise[0] for premise in self.premises},
            formula
        )
        logging.debug('Possible remainders')
        for remainder in all_remainders:
            if isinstance(remainder, Iterable):
                logging.debug(set(remainder))
            else: # just watching out for bugs
                raise TypeError(f'Received type {type(remainder)} instead of Iterable: {remainder}')

        if len(all_remainders) > 1:
            self.premises = self.selection_function(self.fetch_premises(), all_remainders)
        elif len(all_remainders) == 1:
            self.premises = self.selection_function(self.fetch_premises(), [remainder, remainder])
        else:
            self.reset() # empty the database if no possible remainders

    def revise(self, formula):
        self.contract(Not(formula))
        self.add_premise(formula)

    def __repr__(self):
        output = '=============  KB  ===============\n'
        for premise in sorted(self.premises, key=lambda x: float(x[1])):
            output += f' ({premise[1]:.2f}) {premise[0]}\n'
        return output + '=================================='
