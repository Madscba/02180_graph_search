# Project One: Kulibrat Graph Search


## Starting the game

You can run this project either with Docker or installing dependencies and running python.

#### With docker

<details>
  <summary>Click to expand!</summary>

```bash
docker-compose run --rm kulibrat
```

You can optionally change player and game settings when invoking the program:

```bash
docker-compose run --rm kulibrat   main.py --player1-type human --player2-type hminimax --player2-depth 4 --winning-points 2
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
cd /to/this/repo
pipenv install   # to install deps
pipenv shell     # to enter virtualenv
python main.py   # to run the game
```


```bash
pipenv shell
python main.py --player1-type human --player2-type hminimax --player2-depth 4 --winning-points 2
```
</details>



## Playing the game

The UI presents the current board and a numbered list of possible moves:

```
Score: [0, 0]
[[ 0. -2. -3.]
 [ 0.  0. -1.]
 [ 0.  1.  0.]
 [ 2.  3.  0.]]
Value of last move:  0.178125
[1] Piece 2: Diag from 1 to 3
[2] Piece 3: Diag from 2 to 4
[3] Piece 4: Insert from None to 0
```

* The pieces are numbered: `-1, -2, -3, -4` and `1, 2, 3, 4` where negative pieces belong to player 1 and positives to player 2.
* Player 1 starts at the top of the board, Player 2 at the bottom.
* The board cells are numbered `0..11` starting at the top left corner, that is:
```
 (cell numbers)
  
[[ 0.  1.  2.]
 [ 3.  4.  5.]
 [ 6.  7.  8.]
 [ 9.  10.  11.]]
```



## Running benchmarks

With docker:

```
docker-compose run --rm kulibrat benchmark.py --depths 4 5 6
```

Alternatively with your local python:

```bash
pipenv install
pipenv shell # to enter virtualenv
python benchmark.py --depths 4 5 6
python benchmark.py --help # for more options
```
