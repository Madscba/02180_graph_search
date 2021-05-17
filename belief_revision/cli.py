from kb import PL_resolution
import logging
import os
import cmd
import inspect
import pickle

from sympy import symbols
from sympy.core.sympify import sympify
from sympy.logic.boolalg import And, Or, Not, Implies, to_cnf

from kb import Knowledge_base

logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "INFO"),
    format='%(levelname)s: %(message)s'
)


class Cli(cmd.Cmd):
    # intro = '\nBelief Revision engine\n\n'
    prompt = '> '

    def __init__(self, kb, **kwargs):
        super().__init__(**kwargs)
        self.kb = kb

    def do_expand(self, line):
        'Add a belief to the KB. Example: "expand p>>q"'
        if not line:
            self.do_help('expand')
            return
        belief = sympify(line)
        self.kb.add_premise(belief)

    def do_contract(self, line):
        'Remove a belief from the KB. Example: "contract p>>q"'
        if not line:
            self.do_help('contract')
            return
        belief = sympify(line)
        self.kb.contract(belief)

    def do_revise(self, line):
        'Add a belief and delete other beliefs as necessary to keep consistency. Example: "revise p>>q"'
        if not line:
            self.do_help('revise')
            return
        belief = sympify(line)
        self.kb.revise(belief)

    def do_agm(self,line):
        'Test the KB on AGM postulates with a phi and a psi. Split with "-". Example: "agm p>>q - q | p"'
        if not line:
            self.do_help('agm')
            return
        #Save KB
        line = line.split("-")
        if len(line)==1:
            phi = to_cnf(sympify(line[0]))
            psi = False
        elif len(line)==2:
            phi = to_cnf(sympify(line[0]))
            psi = to_cnf(sympify(line[1]))
        else:
            print("More than two inputs")
        pickle.dump(self.kb,open("temp.pickle","wb"))
        notphi = to_cnf(Not(phi))
        baseline = self.kb.fetch_premises()
        appended = list(set(baseline+[phi]))
        self.kb.revise(phi,1)
        revised = self.kb.fetch_premises()
        #print(baseline)
        #print(appended)
        #print(revised)
        #Closure

        #Success
        print(f'Success: {phi in revised}')
        #Inclusion
        print(f'Inclusion: {set(revised).issubset(set(appended))}')
        #Vacuity
        if notphi in baseline:
            print('Vacuity: Can not be determined since phi negated in B')
        else:
            print(f'Vacuity: {revised==appended}')

        #Consistency
        if PL_resolution([],phi):
            print(f"Consistency: {PL_resolution([],revised)}")
        else:
            print("Consistency: Can not be determined since phi isn't consistent")
        if psi:
            True
            #Extensionality

            #Superexpansion

            #Subexpansion
        else:
            "No psi given for last 3 postulates"
        
        #Load the prior KB
        self.kb = pickle.load(open("temp.pickle","rb"))
        #Cleanup temp file
        os.remove("temp.pickle")

    def do_print(self, line):
        'Print the knowledge base'
        print()
        print(self.kb)
        print()

    def do_reset(self, line):
        'Empty the knowledge base'
        self.kb.reset()

    def do_quit(self, line):
        'Exit the program'
        return True

    def do_EOF(self, line):
        return True

    def do_help(self, line):
        if not line:
            main_commands = sorted(
                [cmd[3:] for cmd in dir(self.__class__) if cmd.startswith('do_') and getattr(self, cmd).__doc__]
            )
            print(f'\n-- Available commands: {" ".join(main_commands)} (type "help <command>" for more information)')
            print('-- Format for expressions: ~p (NOT), p&q (AND), p|q (OR), p>>q (IMPLICATION)')
            return
        if f'do_{line}' in dir(self):
            print(inspect.getdoc(getattr(self, f'do_{line}')))
        else:
            print(f'No help available for "{line}"')

    def emptyline(self):
        self.do_help('')

    def preloop(self):
        print('\nInitialising Knowledge Base...\n')
        for belief in generate_initial_beliefs():
            self.kb.revise(belief)
        print(self.kb)
        self.do_help('')

    def precmd(self, line):
        return line

    def postcmd(self, stop, line):
        return stop

    def postloop(self):
        print('\n\nFinal KB:')
        self.do_print('')


def generate_initial_beliefs():
    """Example premises is from exercises from lecture 9"""
    p, q, s, r = symbols("p q s r")
    return [
        Implies(Not(p), q),
        Implies(q, p),
        Implies(p, And(r, s))
    ]
    # beliefs = [to_cnf(belief) for belief in beliefs]
    # temp_ranks = np.arange(5)
    # temp_kb = list(zip(beliefs,temp_ranks))
    # ranks = [1.0 * self.count_entailment(temp_kb,belief) + self.beta / self.count_literals(belief) for belief in beliefs]
    # return list(zip(beliefs,ranks))


# def main1():
#     KB = Knowledge_base()

#     #Use sympy to return boolean value
#     x,y,r,s = symbols("x y r s")
#     ###Resolve test
#     alpha = KB.fetch_sample_thesis()
#     premises = []
#     for premis in KB.premises:
#         premises += [premis[0]]
#     print("Resolution: ",PL_resolution(premises,alpha))
    
#     exp = Implies(x,y)
#     print(exp.subs(x, False))

#     #Example add a premise to KB
#     [print(f"rank {prem[1]} {prem[0]}") for prem in KB.premises]
#     KB.add_premise(exp,5)
#     print(KB)
#     KB.add_premise(exp,"2")
#     print(KB)
#     KB.add_premise(exp,4)
#     print(KB)

#     print("#"*20)
#     [print(f"rank {prem[1]} {prem[0]}") for prem in KB.premises]
#     print("#" * 20)

#     #Try to make to_clause function to work with example from book:
#     """Example from book: Chapter 7.5.2 Proof by resolution (book version 4), subsection "Conjunctive normal form"
#     B1, 1 ⇔ (P1, 2 ∨ P2, 1) should be turned into 3 clauses:
#     (¬B1, 1 ∨ P1, 2 ∨ P2, 1) ∧ (¬P1, 2 ∨ B1, 1) ∧ (¬P2, 1 ∨ B1, 1)
#     """
#     b1, p1, p2 = symbols("b1 p1 p2")
#     s = symbols("s")
#     exp1 = Biconditional(b1, Or(p1, p2))
#     exp2 = Or(s, s)
#     ranks = np.arange(2)
#     premises = [to_cnf(exp) for exp in [exp1, exp2]]
#     init_exp = list(zip(premises, ranks))
#     clauses = KB.to_clauses(init_exp)
#     print(clauses)


if __name__ == "__main__":
    KB = Knowledge_base()
    Cli(KB).cmdloop()
