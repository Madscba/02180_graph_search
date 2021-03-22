import numpy as np
class Board():
    def __init__(self,pl1,pl2,score):
        """
        :param pl1: Boolean value, True for human, False for machine
        :param pl2: Boolean value, True for human, False for machine
        :param score: Int, amount of points need to win the game
        """
        self.state = list(np.zeros((12))) #Three possible states [-1,0,1] 0 = vacant, -1 for pl1,1 for pl2
        self.pl_id = [-1, 1]
        self.pl = [Player(pl1,self.pl_id[0]),Player(pl2,self.pl_id[1])]
        self.pl_turn = 0 #[0 for player 1, 1 for player 2]
        self.wining_score = score
        self.pl_scores = [0,0]
        self.row_count = 4
        self.column_count = 3
        self.minimax_dict = {}
        self.action_evaluator = {"Attack": [0, 0], "Diag": [0, 0], "Jump": [0, 0], "Insert": [0, 0]}

    def display_board(self):
        display = np.zeros((12))
        for idx,ele in enumerate(self.state):
            if isinstance(ele, Piece):
                display[idx] = (1+ele.piece_id)*ele.pl_id
            else:
                display[idx] = 0
        print(display.reshape(4,3))

    def update_state(self,action,minimax_depth=-1):
        #(old pos, new pos, move type,score)
        # update piece and score
        if action is not None:
            if minimax_depth != -1:
                self.minimax_dict[minimax_depth]["action"] = action
                self.minimax_dict[minimax_depth]["player"] = self.pl_turn
            self.update_piece_and_player(action,minimax_depth)
            #update board
            self.update_pos(action)
            #update score
            self.update_score(action)
        #update turn
        self.pl_turn = (self.pl_turn + 1) % 2


    def update_pos(self,action):
        pl_idx = self.pl_turn
        if action[0] != None:
            self.state[action[0]] = 0
        if action[1] != None:
            self.state[action[1]] = self.pl[pl_idx].pieces[action[3]]

    def update_piece_and_player(self,action,minimax_depth=-1):
        pl_idx = self.pl_turn
        if action[2] =='Attack':
            self.state[action[1]].on_board = False
            self.state[action[1]].pos = None
            self.pl[int(not bool(pl_idx))].piece_count +=1
            if minimax_depth != -1:
                self.minimax_dict[minimax_depth]["defender"] = (self.state[action[1]].piece_id,int(not bool(pl_idx))) #Save piece_id of piece being attacked, and owner_id

        if action[0] == None:
            self.pl[pl_idx].pieces[action[3]].on_board = True
            self.pl[pl_idx].pieces[action[3]].pos = action[1]
            self.pl[pl_idx].piece_count -=1
        elif action[1] == None:
            self.pl[pl_idx].pieces[action[3]].on_board = False
            self.pl[pl_idx].pieces[action[3]].pos = None
            self.pl[pl_idx].piece_count += 1
        else:
            self.pl[pl_idx].pieces[action[3]].pos = action[1]

    def update_score(self,action):
        if action[-1]:
            self.pl_scores[self.pl_turn] +=1

    def r_update_state(self,n_depth=-1):
        #Reverse update
        #update score
        self.r_update_score(n_depth)
        #update board
        self.r_update_pos(n_depth)
        #update piece and score
        self.r_update_piece_and_player(n_depth)
        #update turn
        self.pl_turn = (self.pl_turn + 1) % 2


    def r_update_pos(self,n_depth=-1):
        action = self.minimax_dict[n_depth]['action']
        pl_idx = self.minimax_dict[n_depth]["player"]
        if action[0] != None:
            self.state[action[0]] = self.pl[pl_idx].pieces[action[3]]
        if action[1] != None:
             if action[2] == "Attack":
                 opponent_piece_id,opponent_pl_id = self.minimax_dict[n_depth]["defender"]
                 self.state[action[1]] = self.pl[opponent_pl_id].pieces[opponent_piece_id]
             else:
                self.state[action[1]] = 0



    def r_update_piece_and_player(self,n_depth=-1):  #YET TO BE IMPLEMENTED
        
        action = self.minimax_dict[n_depth]['action']
        pl_idx = self.minimax_dict[n_depth]["player"]

        if action[2] == "Attack":
            opponent_piece_id, opponent_pl_id = self.minimax_dict[n_depth]["defender"]
            removed_piece = self.pl[opponent_pl_id].pieces[opponent_piece_id]
            removed_piece.on_board = True
            removed_piece.pos = action[1]
            self.pl[opponent_pl_id].piece_count -= 1

        if action[0] == None:
            self.pl[pl_idx].pieces[action[3]].on_board = False
            self.pl[pl_idx].pieces[action[3]].pos = None
            self.pl[pl_idx].piece_count +=1
        elif action[1] == None:
            self.pl[pl_idx].pieces[action[3]].on_board = True
            self.pl[pl_idx].pieces[action[3]].pos = action[0]
            self.pl[pl_idx].piece_count -= 1
        else:
            self.pl[pl_idx].pieces[action[3]].pos = action[0]

    def r_update_score(self,n_depth=-1):
        action = self.minimax_dict[n_depth]['action']
        pl_idx = self.minimax_dict[n_depth]["player"]
        if action[4]:
            self.pl_scores[pl_idx] -=1


    def eval_state(self):
        """Return an estimate of the expected utility of the board state.

        Note that the value is a global evaluation for both players, negative 
        values indicate that MIN is winning, and positives indicate that MAX is winning.
        """
        score_balance = self.pl_scores[1] - self.pl_scores[0]
        rows_advanced_weight = 0.95 # disincentivise advancing rows (compared to scoring)
        rows_advanced = 0
        for _, piece in enumerate(self.state):
            if piece: # non-empty cell
                if piece.pl_id == 1:
                    rows_advanced += piece.distance_from_home()
                elif piece.pl_id == -1:
                    # substract points for the pieces of the other player
                    rows_advanced -= piece.distance_from_home()
                else:
                    raise ValueError('Unknown player "{}" in Piece, valid players: [0,1]'.format(piece.pl_id))
        return score_balance + rows_advanced_weight*(rows_advanced/(self.row_count+1))

    def terminal_test(self):
        gridlock_win = self.pl[0].get_actions(self) == [] and self.pl[1].get_actions(self) == [] #If the actions of both pl1 and pl2 is None at the current state
        score_win = self.wining_score in self.pl_scores
        return (gridlock_win, score_win)

    def max_alpha_beta(self, alpha, beta, n_depth):
        maxv = -100000 #VERY SMALL
        action = None

        terminal = self.terminal_test()
        if terminal[0]:
            #print("Max terminal:")
            #print(terminal)
            #self.display_board()
            return (-maxv, None) #If game is gridlocked, then Max won
        if terminal[1]:
            #print("Max terminal:")
            #print(terminal)
            #self.display_board()
            return (maxv, None) #If game is won by score, then Max lost
        if n_depth==0:
            return (self.eval_state(),None)
        
        actions = self.pl[self.pl_turn].get_actions(self)
        actions = self.moveOrdering([action for sublist in actions for action in sublist]) #Flatten the list of lists
        if actions == []:
            actions = [None]
        for act in actions: #For all available actions at this point
            self.minimax_dict[n_depth] = {}
            self.update_state(act,minimax_depth=n_depth) #Update the state.
            #print(n_depth)
            #self.display_board()
            m,min_action = self.min_alpha_beta(alpha,beta,n_depth=n_depth-1) 


            if m > maxv: #Best action so far
                maxv = m 
                action = act
            
            if act is None:
                self.pl_turn = (self.pl_turn + 1) % 2
            else:
                self.r_update_state(n_depth)


            if maxv >= beta:
                return (maxv, action)
            
            if maxv > alpha:
                alpha = maxv
        return (maxv, action)

    def min_alpha_beta(self, alpha, beta, n_depth):
        minv = 100000 #VERY LARGE
        action = None

        terminal = self.terminal_test()
        if terminal[0]:
            #print("Min terminal:")
            #print(terminal)
            #self.display_board()
            return (-minv, None) #If game is gridlocked, then Min won
        if terminal[1]:
            #print("Min terminal:")
            #print(terminal)
            #self.display_board()
            return (minv, None) #If game is won by score, then Min lost
        if n_depth==0:
            return (self.eval_state(),None)
        
        actions = self.pl[self.pl_turn].get_actions(self)
        actions = self.moveOrdering([action for sublist in actions for action in sublist]) #Flatten and order the list of lists
        if actions == []:
            actions = [None]
        for act in actions: #For all available actions at this point
            self.minimax_dict[n_depth] = {}
            self.update_state(act,minimax_depth=n_depth) #Update the state.
            #print(n_depth)
            #self.display_board()
            m,max_action = self.max_alpha_beta(alpha,beta,n_depth=n_depth-1) 

            if m < minv: #Best action so far
                minv = m 
                action = act
            
            if act is None:
                self.pl_turn = (self.pl_turn + 1) % 2
            else:
                self.r_update_state(n_depth)


            if minv <= alpha:
                return (minv, action)
            
            if minv < beta:
                beta = minv
        return (minv, action)

    def moveOrdering(self,actions):
        temp_action_list = sorted(list(zip([action[2] for action in actions],actions)))
        return [action[1] for action in temp_action_list]





class Player():
    def __init__(self,human_player,pl_id):
        self.human = human_player
        self.pl_id= pl_id
        self.piece_count = 4
        self.pieces = self.initialize_pieces(pl_id)

    def get_actions(self,board):
        possible_actions = []
        for piece_idx,piece in enumerate(self.pieces):
            actions = piece.get_actions(board)
            if actions != []:
                possible_actions.append(piece.get_actions(board))
        return possible_actions

    def initialize_pieces(self,pl_id):
        return [Piece(pl_id,i) for i in range(4)]
    




class Piece():
    def __init__(self,pl_id,piece_id):
        self.pl_id = pl_id
        self.piece_id = piece_id
        self.on_board = False
        self.pos = None

    def update_pos(self,pos):
        self.pos = pos

    def distance_from_home(self, row_count=4, column_count=3):
        """Return the distance (in rows) from the cell to the player's home."""
        row = self.pos//column_count
        if self.pl_id == -1: # XXX IDs could be the other way around, needs testing
            return row + 1
        elif self.pl_id == 1:
            return row_count - row

    def get_actions(self, board):
        # Every move is a tuple containing (current pos, new pos, type of move, piece_id,score) #None means piece is not on board
        all_actions = []
        if self.pl_id ==-1:
            bool = 0 #bool will be used to determine whether we look forward or backward in our list, an expression like this will be used: (1-bool)*(#_1) + (bool*(#_2))
        else:
            bool= 1
        if self.on_board:
            actions = self.action_diag(board,bool)
            if actions != []:
                all_actions+= actions
            if not ( (self.pl_id == -1 and self.pos in [9, 10, 11]) or (self.pl_id == 1 and self.pos in [0, 1, 2]) ): #Piece is not at the opponents starting row
                fw_idx = 3*(-self.pl_id)
                if isinstance(board.state[self.pos+fw_idx], Piece):
                    if board.state[self.pos+fw_idx].pl_id != self.pl_id:
                        actions = self.action_attack(board, fw_idx)
                        if actions != []:
                            all_actions += actions
                        actions = self.action_jump(board, fw_idx)
                        if actions != []:
                            all_actions += actions
        else:
            actions = self.action_insert(board, bool)
            if actions != []:
                all_actions+= actions

        return all_actions

    def action_diag(self, board, bool):
        if (self.pl_id == -1 and self.pos in [9, 10, 11]) or (self.pl_id == 1 and self.pos in [0, 1, 2]):  # end row of opponent
            return [(self.pos,None,"Diag",self.piece_id,True)] #Score
        actions =[]

        if self.pos % 3 == 0:  # right column for p1 point of view, left column for p2
            list_change = ((1 - bool) * 4 + bool * 2) * (-self.pl_id)
            if board.state[self.pos + list_change] == 0:
                actions.append(( self.pos, self.pos + list_change, "Diag",self.piece_id,False))

        elif self.pos % 3 == 1:  # middle column
            list_change0 = ((1 - bool) * 2 + 4 * bool) * (-self.pl_id)
            if board.state[self.pos + list_change0] == 0:
                actions.append( (self.pos, self.pos + list_change0, "Diag",self.piece_id,False) )

            list_change1 =((1 - bool) * 4 + 2 * bool)* (-self.pl_id)
            if board.state[self.pos + list_change1 ] == 0:
                actions.append( (self.pos, self.pos + list_change1, "Diag",self.piece_id,False) )
        else:  # left column for p1 point of view, right column for p2
            list_change = ((1 - bool) * 2 + 4 * bool)* (-self.pl_id)
            if board.state[self.pos + list_change] == 0:
                actions.append( (self.pos, self.pos + list_change, "Diag",self.piece_id,False) )
        return actions



    def action_jump(self, board, fw_idx):
        if self.pos + fw_idx in [0,1,2,9,10,11]:
            return [(self.pos,None,"Jump",self.piece_id,True)] #Score

        fw_idx_2 = self.pos + fw_idx*2

        while (fw_idx_2 < 12 and self.pl_id ==-1) or (fw_idx_2>-1 and self.pl_id==1):
            if isinstance(board.state[fw_idx_2], Piece) and board.state[fw_idx_2].pl_id != self.pl_id:
                fw_idx_2 += fw_idx
                if (fw_idx_2 > 11 and self.pl_id ==-1) or (fw_idx_2<0 and self.pl_id==1):
                    return [(self.pos, None, "Jump",self.piece_id,False)] #Score
            elif isinstance(board.state[fw_idx_2], Piece) and board.state[fw_idx_2].pl_id == self.pl_id:
                    return []
            elif board.state[fw_idx_2] == 0:
                return [(self.pos,fw_idx_2,"Jump",self.piece_id,False)]






    def action_attack(self, board, fw_idx):
        return [(self.pos,self.pos+fw_idx,'Attack',self.piece_id,False)]

    def action_insert(self, board, bool):
        if bool ==0:
            return [(None,i,"Insert",self.piece_id,False) for i in range(3) if board.state[i] == 0]
        else:
            return [(None,i,"Insert",self.piece_id,False) for i in range(9,12) if board.state[i] == 0]
