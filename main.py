import random
import sys
from timeit import default_timer as timer

from classes import Board


def initialize_game(pl1, pl2, winning_points):
    pl1_human = pl1['type'] == 'human'
    pl2_human = pl2['type'] == 'human'
    board = Board(
        pl1_human,
        pl2_human,
        winning_points,
        pl1_params=pl1.get('parameters'),
        pl2_params=pl2.get('parameters')
    )
    return board


def run_game(pl1, pl2, winning_points, interactive=True):
    pl1_depth = pl1.get('parameters', {}).get('depth', 6)
    pl2_depth = pl2.get('parameters', {}).get('depth', 6)

    iteration_count = 0
    max_iterations = winning_points * 30
    value=0
    pl1_time = 0
    pl2_time = 0
    board = initialize_game(pl1, pl2, winning_points)

    while True:
        iteration_count += 1
        gridlock_winner, score_winner = board.terminal_test()
        if any((gridlock_winner, score_winner)):
            break
        if iteration_count > max_iterations:
            print(f'  pl1 actions={board.pl[0].get_actions(board)}')
            print(f'  pl2 actions={board.pl[1].get_actions(board)}')
            print("  Score: {}".format(board.pl_scores))
            print("  Value of last move: ", value)
            print(f'  gridlock_winner={gridlock_winner}, score_winner={score_winner}')
            board.display_board()
            raise RecursionError(f'MAX_ITERATIONS ({max_iterations}) reached')
        if interactive:
            board.display_board()
            print("Value of last move: ",value)
        # input("Press enter to progress")

        cur_pl = board.pl[board.pl_turn]
        actions = cur_pl.get_actions(board)
        if len(actions) != 0:
            if not cur_pl.human:
                if cur_pl.pl_id == -1: 
                    start = timer()
                    if pl1['type'] == 'random':
                        value, chosen_action = None, random.choice(random.choice(actions))
                    else:
                        value, chosen_action = board.min_alpha_beta(-1000, 1000, pl1_depth, invoking_player=0)
                    end = timer()
                    pl1_time += end - start
                else:
                    start = timer()
                    if pl2['type'] == 'random':
                        value, chosen_action = None, random.choice(random.choice(actions))
                    else:
                        value, chosen_action = board.max_alpha_beta(-1000, 1000, pl2_depth, invoking_player=1)
                    end = timer()
                    pl2_time += end - start
            else:
                action_choices = [action for piece_actions in actions for action in piece_actions]
                [print("[{}] Piece {}: {} from {} to {}".format(
                        idx+1, action[3]+1, action[2], action[0],action[1]
                    )) for idx, action in enumerate(action_choices)]
                while True:
                    try:
                        human_input = input("Choose action number from the list: ")
                        chosen_action_id = int(human_input)-1
                        if chosen_action_id >= 0:
                            chosen_action = action_choices[chosen_action_id]
                            break
                    except KeyboardInterrupt:
                        sys.exit("Keyboard interrupt")
                    except:
                        pass
        else:
            chosen_action = None
            value = "NA"
        board.update_state(chosen_action)

        if interactive:
            print("Score: {}".format(board.pl_scores))
    if score_winner:
        winner = score_winner
    elif gridlock_winner:
        winner = gridlock_winner
    else:
        raise RuntimeError('Cannot determine winner after game has finished')
    return {
        'winner': winner,
        'scores': (board.pl_scores[0], board.pl_scores[1]),
        'runtimes': (pl1_time, pl2_time),
        'total_turns': iteration_count,
    }


if __name__ == "__main__":
    # pl1 = {
    #     'name': 'hminimax-depth4',
    #     'type': 'hminimax',
    #     'parameters': {
    #         'depth': 4,
    #         'row_score': 0.2,
    #         'action_score': 0.1,
    #         'action_score_decrease_rate': 2,
    #         'attack_action_score': 0.0,
    #     }
    # }
    pl1 = {
        'name': 'human',
        'type': 'human',
    }
    pl2 = {
        'name': 'hminimax-depth5', # any string
        'type': 'hminimax',        # human | hminimax | random
        'parameters': {            # algorithm parameters
            'depth': 5, # hminimax depth
            'row_score': 0.2, # enable=0.20 / disable=0.0
            'action_score': 0.1, # enable=0.1 / disable=0.0
            'action_score_decrease_rate': 2, # recommended=2
            'attack_action_score': 0.0, # recommended=0
        }
    }
    winning_points = 10
    result = run_game(pl1, pl2, winning_points)
    print(f'Winner: {result["winner"]}, Scores: {result.get("scores")}')
