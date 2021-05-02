import json
import argparse
from itertools import product
from datetime import datetime

from main import run_game


TEST_SETTINGS = {
    'depth': [],
    'row_score': [],
    'action_score': [],
    # 'action_score_decrease_rate': [2],
    # 'attack_action_score': [0.0],
}


def unique_key(pl1, pl2):
    """Return a unique key for a given player1 and player2."""
    return '|'.join([pl1['name'], pl2['name']])


def draw_duels():
    duels = {}
    contenders = []
    for depth in TEST_SETTINGS['depth']:
        for row_score in TEST_SETTINGS.get('row_score', [0.0]):
            for action_score in TEST_SETTINGS.get('action_score', [0.0]):
                for action_score_decrease_rate in TEST_SETTINGS.get('action_score_decrease_rate', [2]):
                    for attack_action_score in TEST_SETTINGS.get('attack_action_score', [0.0]):
                        contenders.append({
                            'name': f'd{depth}-rs{row_score}+ac{action_score}@{action_score_decrease_rate}+at{attack_action_score}'.replace('0.', '.'),
                            'type': 'hminimax',
                            'parameters': {
                                'depth': depth,
                                'row_score': row_score,
                                'action_score': action_score,
                                'action_score_decrease_rate': action_score_decrease_rate,
                                'attack_action_score': attack_action_score,
                            },
                        })

    contenders = sorted(contenders, key=lambda k: k['name'])
    for pl1 in contenders:
        for pl2 in contenders:
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
        'runtimes': {
            'pl1': 0,
            'pl2': 0,
        },
        'players': (pl1, pl2),
        'test_settings': {
            'iterations': iterations,
            'winning_points': winning_points,
        },
        'total_turns': 0,
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
            if 'runtimes' in encounter:
                stats['runtimes']['pl1'] += encounter['runtimes'][0]
                stats['runtimes']['pl2'] += encounter['runtimes'][1]
            if 'total_turns' in encounter:
                stats['total_turns'] += encounter['total_turns']
    return stats


def display_results(results):
    rows, columns = set(), set()
    for key in results:
        column = key.split('|')[0] # player1
        row = key.split('|')[1] # player2
        rows.add(row)
        columns.add(column)
    rows = sorted(rows)
    columns = sorted(columns)
    print(f'\n                     ', end='\t')
    [print(f'{column:<21}', end='\t') for column in columns]
    print()
    print(f'                     ', end='\t')
    [print(f'---------------------', end='\t') for column in columns]
    print()
    print(f'                     ', end='\t')
    [print(f'point%   win% time_ms', end='\t') for column in columns]
    print()
    for row in rows:
        print(f'{row:<21}', end='\t')
        for column in columns:
            duel = results.get(f'{column}|{row}', {})
            if duel:
                try:
                    victory_ratio = 100 * duel["victories"]["pl1"] / ( duel["victories"]["pl1"] + duel["victories"]["pl2"])
                except ZeroDivisionError:
                    victory_ratio = float('NaN')
                try:
                    point_ratio = 100 * duel["points"]["pl1"] / ( duel["points"]["pl1"] + duel["points"]["pl2"])
                except ZeroDivisionError:
                    point_ratio = float('NaN')
                try:
                    time_per_turn = 1000 * duel["runtimes"]["pl1"] / duel["total_turns"] / 2
                except ZeroDivisionError:
                    time_per_turn = float('NaN')
                # print(f'{point_ratio:>6.1f}{victory_ratio:>7.1f}{time_per_turn:>8.2f}', end='\t')
            duel2 = results.get(f'{row}|{column}', {})
            if duel2:
                try:
                    victory_ratio += 100 - (100 * duel2["victories"]["pl1"] / ( duel2["victories"]["pl1"] + duel2["victories"]["pl2"]))
                except ZeroDivisionError:
                    victory_ratio = float('NaN')
                try:
                    point_ratio += 100 - (100 * duel2["points"]["pl1"] / ( duel2["points"]["pl1"] + duel2["points"]["pl2"]))
                except ZeroDivisionError:
                    point_ratio = float('NaN')
                # string = f'{duel2["points"]["pl1"]} / {duel2["points"]["pl2"]}'
            try:
                print(f'{point_ratio/2:>6.1f}{victory_ratio/2:>7.1f}{time_per_turn:>8.2f}', end='\t')
            except:
                print('--------        ', end="\t")
        print()


if __name__ == "__main__":
    results = {}
    count = 0

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--iterations', default=2, type=int)
    parser.add_argument('-w', '--winning-points', default=15, type=int)
    parser.add_argument('-d','--depths', type=int, nargs='+', help='<Required> List of depths (e.g. --d 4 5 6)', required=True)
    parser.add_argument('-r','--row-scores', type=float, nargs='+', help='List of row_scores (e.g. --a 0.0 0.2)', default=[0.2])
    parser.add_argument('-a','--action-scores', type=float, nargs='+', help='List of action_scores (e.g. --a 0.0 0.1)', default=[0.0, 0.1])
    args = parser.parse_args()

    TEST_SETTINGS['depth'] = args.depths
    TEST_SETTINGS['row_score'] = args.row_scores
    TEST_SETTINGS['action_score'] = args.action_scores

    duels = draw_duels()
    print(f"Suite settings {TEST_SETTINGS}")
    print(f"Running benchmark suite of {len(duels.keys())} tests:")
    for key in duels:
        print(key)
    for duel_key, players in duels.items():
        count += 1
        print(f'Test {count:>4}/{len(duels)}: ', end='')
        results[duel_key] = run_benchmark(players[0], players[1], args.iterations, args.winning_points)
    display_results(results)
    filename = f'results-{datetime.now().isoformat()}.json'
    with open(filename, 'w') as outfile:
        json.dump(results, outfile)
    print(f'Results saved in {filename}')
