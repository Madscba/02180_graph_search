import numpy as np
import random
from classes import Board

def initialize_game(human_pl1,human_pl2,winning_points):
    board = Board(human_pl1,human_pl2,winning_points)
    return board

def evaluate_actions(actions,board): ###DUMMY EVAL FUNC
    return random.choice(random.choice(actions))
if __name__ == "__main__":
    pl1_human,pl2_human = False,True
    winning_points = 10

    board = initialize_game(pl1_human,pl2_human,winning_points)

    old_player_cannot_move,avaiable_moves = False,True
    while not board.terminal_test() and avaiable_moves:
        board.display_board()

        cur_pl = board.pl[board.pl_turn]
        actions = cur_pl.get_actions(board)
        if len(actions) != 0:
            current_player_cannot_move = False
            if cur_pl.human == False:
                chosen_action = evaluate_actions(actions,board)
            else:
                [print("{} piece: {} from {}  to {}".format(action[2],action[3]+1,action[0],action[1])) for piece_actions in actions for action in piece_actions ]
                while True:
                    try:
                        human_input = input("Choose piece, and option (format: 'piece,action'))").split(",")
                        chosen_action = actions[int(human_input[0])][int(human_input[1])]
                        break
                    except:
                        pass

            board.update_state(chosen_action)
        else:
            current_player_cannot_move = True
        #[print(i,": ",type(ele)) for i,ele in enumerate(board.state)]
        print("Score: {}".format(board.pl_scores))
        board.pl_turn = (board.pl_turn + 1) % 2
        if old_player_cannot_move and current_player_cannot_move:
            avaiable_moves = False
            print("No available moves, player {} looses!".format(board.pl_turn))
        else:
            old_player_cannot_move = current_player_cannot_move




