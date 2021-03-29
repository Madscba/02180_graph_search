# Project One: Kulibrat Graph Search


## Running the game

You can run this project either with Docker or installing dependencies and running python.

#### With docker

```bash
docker-compose run --rm kulibrat
```

You can optionally change player and game settings when invoking the program:

```bash
docker-compose run --rm kulibrat   main.py --player1-type human --player2-type hminimax --player2-depth 4 --winning-points 2
```


#### With your local python installation

First install pipenv to manage dependencies:

```bash
pip install --user pipenv
```

With pipenv installed you are ready to install dependencies and run the program:

```bash
cd /to/this/repo
pipenv install   # to install deps
pipenv shell     # to enter virtualenv
python main.py   # to run the game
```


```bash
pipenv shell
python main.py --player1-type human --player2-type hminimax --player2-depth 4 --winning-points 2
```


## Running benchmarks

With docker:

```
docker-compose run --rm kulibrat benchmark.py
```

Alternatively with your local python:

```bash
pipenv install
pipenv shell          # to enter virtualenv
python benchmark.py   # to run the benchmarks
```
