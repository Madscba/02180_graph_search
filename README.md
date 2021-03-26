# Project One: Kulibrat Graph Search


## Running the game

You can run this project either with Docker or installing dependencies and running python.

### With docker

```
docker-compose run --rm kulibrat
```

### Python 3.8

First install pipenv to manage dependencies:

```
pip install --user pipenv
```

With pipenv installed you are ready to use this repo:

```bash
cd /to/this/repo
pipenv install   # to install deps
pipenv shell     # to enter virtualenv
python main.py   # to run the game
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
