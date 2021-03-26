import numpy as np
import random
import sys
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

def evaluate_actions(actions,board): ###DUMMY EVAL FUNC
    return random.choice(random.choice(actions))

def run_game(pl1, pl2, winning_points, interactive=True):
    pl1_depth = pl1.get('parameters', {}).get('depth', 6)
    pl2_depth = pl2.get('parameters', {}).get('depth', 6)

    iteration_count = 0
    value=0
    board = initialize_game(pl1, pl2, winning_points)

    while True:
        iteration_count += 1
        gridlock_winner, score_winner = board.terminal_test()
        if any((gridlock_winner, score_winner)):
            break
        if iteration_count > winning_points**3:
            raise RecursionError(f'MAX_ITERATIONS ({winning_points**3}) reached')
        if interactive:
            board.display_board()
            print("Value of last move: ",value)
#        input("Press enter to progress")

        cur_pl = board.pl[board.pl_turn]
        actions = cur_pl.get_actions(board)
        if len(actions) != 0:
            current_player_cannot_move = False
            if cur_pl.human == False:
                if cur_pl.pl_id == -1: 
                    if pl1['type'] == 'random':
                        value, chosen_action = None, evaluate_actions(actions, board)
                    else:
                        value, chosen_action = board.min_alpha_beta(-1000,1000,pl1_depth, me=0)
                else:
                    if pl2['type'] == 'random':
                        value, chosen_action = None, evaluate_actions(actions, board)
                    else:
                        value, chosen_action = board.max_alpha_beta(-1000,1000,pl2_depth, me=1)
            else:
                [print("{} piece: {} from {}  to {}".format(action[2],action[3]+1,action[0],action[1])) for piece_actions in actions for action in piece_actions ]
                while True:
                    try:
                        human_input = input("Choose piece, and option (format: 'piece,action'))").split(",")
                        chosen_action = actions[int(human_input[0])-1][int(human_input[1])-1]
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
    }


if __name__ == "__main__":
    pl2 = {
        'name': 'human',
        'type': 'human',
    }
    # pl1 = {
    #     'name': 'hminimax-depth3-e1',
    #     'type': 'hminimax',
    #     'parameters': {
    #         'depth': 3,
    #         'eval_type': 'default',
    #     }
    # }
    pl1 = {
        'name': 'hminimax-depth3-e2',
        'type': 'hminimax',
        'parameters': {
            'depth': 4,
            'eval_type': 'default',
        }
    }
    winning_points = 10
    result = run_game(pl1, pl2, winning_points)
    print(f'Winner: {result["winner"]}, Scores: {result.get("scores")}')
