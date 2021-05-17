# Project Two: Belief Revision


## Running the belief revision engine

You can run this project either with Docker or installing dependencies and running python.

#### With docker

<details>
  <summary>Click to expand!</summary>

```bash
cd /this-repo/belief_revision
docker-compose run --rm beliefrevision
```
</details>


#### With your local python installation

<details>
  <summary>Click to expand!</summary>

First install pipenv to manage dependencies:

```bash
pip install --user pipenv
```

With pipenv installed you are ready to install dependencies and run the program:

```bash
cd /this-repo/belief_revision
pipenv install   # to install deps
pipenv shell     # to enter virtualenv
python cli.py    # to run the program
```

</details>



## User interface

The engine starts with a generic belief base, that the user can modify via `revise`, `contract` or `expand` commands.
Use `print` to show the current belief base.

The command-line interface shows the available commands and the way of formatting expressions:

```
-- Available commands: revise contract expand agm print reset quit (type "help <command>" for more information)
-- Format for expressions: ~p (NOT), p&q (AND), p|q (OR), p>>q (IMPLICATION)
```

Use help to learn more about a command: 

```
help revise
```

Example of `revise` command and its output:

```
> revise p&q
=============  KB  ===============
 (1.67) (r | ~p) & (s | ~p)
 (2.00) p | q
 (2.00) p | ~q
 (4.00) p & q
==================================
```

The `agm` command performs tests og AGM postulates:

```
> agm p - q
Closure: False
Success: True
Inclusion: True
Vacuity: True
Consistency: True
Extensionality: Can not be determined since (phi <-> psi) is not a tautologi
Superexpansion: False
Subexpansion: Can not be determined since psi negated in B*phi
```


## Development

You can specify loglevel via environment: `LOGLEVEL=DEBUG python cli.py`

