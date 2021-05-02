import numpy as np
from sympy import symbols, Symbol, init_printing
from sympy.logic.boolalg import And,Or, Not, Implies, Equivalent, distribute_and_over_or, distribute_or_over_and, is_cnf,to_cnf

def Biconditional(a,b):
    """
    rewrite biconditional as a new premise consisting of two implies according to formula in Peter Norvig & Stuart Russel Chapter 7
    replacing alpha <=> beta with (alpha => beta) and (beta => alpha)
    """
    return And(Implies(a,b),Implies(b,a))

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
    # def PL_resolution(self,KB,alpha):
    def to_clauses(self,premises=None):
        """
        OBS: DOES NOT WORK YET!

        turn premises into disjunctions of literals
        """
        clauses = []
        for prem in premises:
            if prem[0].func == And:
                for clause in prem[0].args:
                    clauses.append(clause)
        return clauses


if __name__ == "__main__":
    KB = Knowledge_base()

    #Use sympy to return boolean value
    x,y,r,s = symbols("x y r s")
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
    exp1 = Biconditional(b1, And(p1, p2))
    exp2 = Or(s, s)
    ranks = np.arange(2)
    premises = [to_cnf(exp) for exp in [exp1, exp2]]
    init_exp = list(zip(premises, ranks))
    clauses = KB.to_clauses(init_exp)
    print(clauses)