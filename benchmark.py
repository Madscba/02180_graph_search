from itertools import product

from main import run_game


CONTENDERS = sorted([
        {
            'name': 'hminimax-depth2',
            'type': 'hminimax',
            'parameters': {
                'depth': 2,
            },
        },
        {
            'name': 'hminimax-depth3',
            'type': 'hminimax',
            'parameters': {
                'depth': 3,
            },
        },
        {
            'name': 'hminimax-depth4',
            'type': 'hminimax',
            'parameters': {
                'depth': 4,
            },
        },
        {
            'name': 'hminimax-depth5',
            'type': 'hminimax',
            'parameters': {
                'depth': 5,
            },
        },
        {
            'name': 'hminimax-depth6',
            'type': 'hminimax',
            'parameters': {
                'depth': 6,
            },
        },
        {
            'name': 'random',
            'type': 'random',
            'parameters': {},
        },
    ],
    key=lambda k: k['name']
)

RESULTS = {}



def unique_key(pl1, pl2):
    """Return a unique key for a given player1 and player2."""
    return '|'.join([pl1['name'], pl2['name']])


def draw_duels():
    duels = {}
    for pl1 in CONTENDERS:
        for pl2 in CONTENDERS:
            duel_key = unique_key(pl1, pl2)
            # Uncomment to prevent testing of both permutations of the same players
            # reverse_key = unique_key(pl2, pl1)
            # if duel_key not in duels and reverse_key not in duels:
            if duel_key not in duels:
                duels[duel_key] = (pl1, pl2)
    return duels


def run_benchmark(pl1, pl2, iterations, winning_points):
    print(f'run_benchmark({pl1["name"]}, {pl2["name"]}, {iterations}, {winning_points})')
    stats = {
        'victories': {
            'pl1': 0,
            'pl2': 0,
        },
        'points': {
            'pl1': 0,
            'pl2': 0,
        },
        # 'times': {},
        'players': (pl1, pl2),
        'test_settings': {
            'iterations': iterations,
            'winning_points': winning_points,
        },
    }
    for _ in range(iterations):
        try:
            encounter = run_game(pl1, pl2, winning_points, interactive=False)
        except RecursionError as exc:
            print(f'Game run failed to complete, ignoring results: {exc}')
        else:
            if encounter['winner'] == -1:
                stats['victories']['pl1'] += 1
            elif encounter['winner'] == 1:
                stats['victories']['pl2'] += 1
            else:
                raise ValueError(f'Unknown player id: {encounter["winner"]}')
            if 'scores' in encounter:
                stats['points']['pl1'] += encounter['scores'][0]
                stats['points']['pl2'] += encounter['scores'][1]
    return stats


def display_results():
    rows, columns = set(), set()
    for key in RESULTS:
        row, column = key.split('|')
        rows.add(row)
        columns.add(column)
    rows = sorted(rows)
    columns = sorted(columns)
    print(f'\nVICTORIES       ', end='\t')
    [print(f'{column:<16}', end='\t') for column in columns]
    print()
    for row in rows:
        print(f'{row:<16}', end='\t')
        for column in columns:
            duel = RESULTS.get(f'{row}|{column}', {})
            if duel:
                string = f'{duel["victories"]["pl1"]} / {duel["victories"]["pl2"]}'
                print(f'{string:<16}', end='\t')
            else:
                print('--------        ', end="\t")
        print()
    print(f'\nPOINTS          ', end='\t')
    [print(f'{column:<16}', end='\t') for column in columns]
    print()
    for row in rows:
        print(f'{row:<16}', end='\t')
        for column in columns:
            duel = RESULTS.get(f'{row}|{column}', {})
            if duel:
                string = f'{duel["points"]["pl1"]} / {duel["points"]["pl2"]}'
                print(f'{string:<16}', end='\t')
            else:
                print('--------        ', end="\t")
        print()


if __name__ == "__main__":
    iterations = 10
    winning_points = 10
    duels = draw_duels()
    print(f"Running benchmark suite of {len(duels.keys())} tests: {list(duels.keys())}\n")
    for duel_key, players in duels.items():
        RESULTS[duel_key] = run_benchmark(players[0], players[1], iterations, winning_points)
    display_results()
