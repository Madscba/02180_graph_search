from kb import PL_resolution, Biconditional
import logging
import os
import cmd
import inspect
import pickle

from sympy import symbols
from sympy.core.sympify import sympify
from sympy.logic.boolalg import And, Or, Not, Implies, to_cnf

from kb import Knowledge_base, PL_resolution

logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "INFO"),
    format='%(levelname)s: %(message)s'
)


class Cli(cmd.Cmd):
    # intro = '\nBelief Revision engine\n\n'
    prompt = '\n\n> '

    def __init__(self, kb, **kwargs):
        super().__init__(**kwargs)
        self.kb = kb

    def do_expand(self, line):
        'Add a belief to the KB. Example: "expand p>>q"'
        if not line:
            self.do_help('expand')
            return
        try:
            belief = sympify(line)
        except ValueError as exc:
            print(exc)
            return
        if not PL_resolution([], belief):
            print(f'{belief} is a contradiction, skipping')
            return
        self.kb.add_premise(belief)
        self.do_print(line)

    def do_contract(self, line):
        'Remove a belief from the KB. Example: "contract p>>q"'
        if not line:
            self.do_help('contract')
            return
        try:
            belief = sympify(line)
        except ValueError as exc:
            print(exc)
            return
        self.kb.contract(belief)
        self.do_print(line)

    def do_revise(self, line):
        'Add a belief and delete other beliefs as necessary to keep consistency. Example: "revise p>>q"'
        if not line:
            self.do_help('revise')
            return
        try:
            belief = sympify(line)
        except ValueError as exc:
            print(exc)
            return
        if not PL_resolution([], belief):
            print(f'{belief} is a contradiction, skipping')
            return
        self.kb.revise(belief)
        self.do_print(line)

    def do_agm(self,line):
        'Test the KB on AGM postulates with a phi and a psi. Split with "-". Example: "agm p>>q - q | p"'
        if not line:
            self.do_help('agm')
            return
        #Save KB
        line = line.split("-")
        try:
            if len(line)==1:
                phi = to_cnf(sympify(line[0]))
                psi = False
            elif len(line)==2:
                phi = to_cnf(sympify(line[0]))
                psi = to_cnf(sympify(line[1]))
            else:
                print("More than two inputs")
        except ValueError as exc:
            print(exc)
            return
        pickle.dump(self.kb,open("temp.pickle","wb"))
        notphi = to_cnf(Not(phi))
        baseline = self.kb.fetch_premises()
        appended = baseline+[phi]
        self.kb.revise(phi)
        revised = self.kb.fetch_premises()

        
        
        #print(baseline)
        #print(appended)
        #print(revised)
        
        #Closure
        print("Closure: False")
        #Success
        print(f'Success: {phi in revised}')
        #Inclusion
        print(f'Inclusion: {set(revised).issubset(set(appended))}')
        #Vacuity
        if notphi in baseline:
            print('Vacuity: Can not be determined since phi negated in B')
        else:
            print(f'Vacuity: {set(revised)==set(appended)}')

        #Consistency
        if PL_resolution([],phi):
            print(f"Consistency: {PL_resolution([],revised)}")
        else:
            print("Consistency: Can not be determined since phi isn't consistent")
        if psi:
            self.kb = pickle.load(open("temp.pickle","rb"))
            self.kb.revise(psi)
            revised_psi = self.kb.fetch_premises()
            appended_psi = revised + [psi]
            self.kb = pickle.load(open("temp.pickle","rb"))
            self.kb.revise(And(phi,psi))
            revised_phi_psi = self.kb.fetch_premises()
            notpsi = to_cnf(Not(psi))

            #Extensionality
            if (not PL_resolution([],Not(Biconditional(phi,psi)))) or Biconditional(phi,psi)==True:
                
                print(f'Extensionality: {set(revised)==set(revised_psi)}')
            else:
                print("Extensionality: Can not be determined since (phi <-> psi) is not a tautologi")

        
            #Superexpansion
            print(f"Superexpansion: {set(revised_phi_psi).issubset(set(appended_psi))}")
            #Subexpansion
            if notpsi in revised:
                print(f"Subexpansion: {set(appended_psi).issubset(set(revised_phi_psi))}")
            else:
                print('Subexpansion: Can not be determined since psi negated in B*phi')
        else:
            print("No psi given for last 3 postulates")
        #Load the prior KB
        self.kb = pickle.load(open("temp.pickle","rb"))
        #Cleanup temp file
        os.remove("temp.pickle")
        
       

    def do_print(self, line):
        'Print the knowledge base'
        print(self.kb)

    def do_reset(self, line):
        'Empty the knowledge base'
        self.kb.reset()
        self.do_print(line)

    def do_quit(self, line):
        'Exit the program'
        return True

    def do_EOF(self, line):
        return True

    def do_help(self, line):
        if not line:
            # main_commands = sorted(
            #     [cmd[3:] for cmd in dir(self.__class__) if cmd.startswith('do_') and getattr(self, cmd).__doc__]
            # )
            main_commands = ['revise', 'contract', 'expand', 'agm', 'print', 'reset', 'quit']
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
        # if line and line[0] in []
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


if __name__ == "__main__":
    KB = Knowledge_base()
    Cli(KB).cmdloop()
