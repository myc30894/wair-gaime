from copy import deepcopy
import argparse
import logging
import BAprune
import sys
from collections import Counter


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WarGame:

    def __init__(self, fname, runmode):
        self.board = []
        self.score = {'green': 0, 'blue': 0}
        self.open = []
        try:
            with open(fname) as f:
                for idx, line in enumerate(f):
                    self.board.append([])
                    for col, char in enumerate(line.split('\t')):
                        self.board[idx].append({'value': int(char), 'team': None})
                        self.open.append((idx,col))

        except OSError:
            logger.error('Could not open board.')

        self.height = len(self.board)
        self.width = len(self.board[0])

    def __capture(self, loc, team):
        try:
            self.open.remove(loc)
        except:
            pass

        # Check conquer and change scores respectively
        loc_team = self.board[loc[0]][loc[1]]['team']
        if loc_team and loc_team!= team:
            self.score[loc_team] -= self.board[loc[0]][loc[1]]['value']

        self.score[team] += self.board[loc[0]][loc[1]]['value']
        self.board[loc[0]][loc[1]]['team'] = team

        return

    def __conquer_neighbors(self, loc, team, opponent, max_player):
        neighbors = [(loc[0]+1, loc[1]), (loc[0]-1, loc[1]), (loc[0], loc[1]+1), (loc[0], loc[1]-1)]

        # Conquer and capture all valid enemy neighbors and spots
        for neighbor in neighbors:
            row = neighbor[0]
            col = neighbor[1]
            if (0 <= row < self.height) and (0 <= col < self.width) and (self.board[row][col]['team'] == team):
                for opp in neighbors:
                    opp_row = opp[0]
                    opp_col = opp[1]
                    if (0 <= opp_row < self.height) and (0 <= opp_col < self.width):
                        if self.board[opp_row][opp_col]['team'] == opponent:
                            self.__capture(opp, team)
                return

    def __death_blitz(self, loc, team, max_player):
        if team == 'blue':
            opponent = 'green'
        else:
            opponent = 'blue'

        # Capture spot (basically paradrop) then attempt to blitz
        self.__capture(loc, team)
        self.__conquer_neighbors(loc, team, opponent, max_player)      

        return

    def _make_move(self, loc, mode, team, max_player):
        if mode == 0: 
            self.__capture(loc, team)
        elif mode == 1:
            self.__death_blitz(loc, team, max_player)
        return

def minimax(board, team, opponent, max_player, depth, loc = None):
    # Depth reached/No more spots
    if depth == 0 or (len(board.open) == 0):
        return (board.score[team] if max_player else board.score[opponent], loc)

    max_value = -sys.maxint - 1
    min_value = sys.maxint
    best_loc = (-1,-1)

    # Test every open spot
    for unoccupied in board.open:

        # Make deepcopy to prevent different paths changing game board
        copied_board = deepcopy(board)
        minimax.nodes += 1

        # Attempt blitz
        copied_board._make_move(unoccupied, 1, team, max_player)

        # Recurse to get best move
        move_score = minimax(copied_board, opponent, team, not max_player, depth-1, unoccupied)

        if max_player:
            if move_score[0] > max_value:
                max_value = move_score[0]
                best_loc = unoccupied
        else:
            if move_score[0] < min_value:
                min_value = move_score[0]
                best_loc = unoccupied

    return (max_value if max_player else min_value, best_loc)

def simulate(game, runmode):
    expanded_nodes = {'blue': [], 'green':[]}
    current_team = 'blue'
    opponent_team = 'green'
    if(runmode == 'MvM'):
        max_player = True
        total_nodes = 0

        # Run until all spots are captured
        while(game.open):
            minimax.nodes = 0

            # Get minimax decision and capture spot (blitz if possible, drop otherwise)
            result = minimax(game, current_team, opponent_team, max_player, 3)
            game._make_move(result[1], 1, current_team, max_player)
            print (result[1])
            # Expanded nodes
            print(minimax.nodes, current_team)
            total_nodes += minimax.nodes
            expanded_nodes[current_team].append(minimax.nodes) 

            # Next turn
            current_team, opponent_team = opponent_team, current_team
            
    if (runmode == 'ABvAB'):
        total_nodes = 0
        while(game.open):
            abnodes = 0

            # Get minimax decision and capture spot (blitz if possible, drop otherwise)
            result = BAprune.ba_prune(current_team,opponent_team,current_team,opponent_team,game)
            game._make_move(result[1], 1, current_team, opponent_team)
            abnodes = result[2]
            # Expanded nodes
            print(abnodes, current_team, result[1])
            total_nodes += abnodes
            expanded_nodes[current_team].append(abnodes) 

            # Next turn
            current_team, opponent_team = opponent_team, current_team


    print('green:', expanded_nodes['green'])
    print('blue:', expanded_nodes['blue'])
    print(game.score)
    for row in game.board: print(row)
    print(total_nodes)


    return

def main():
    parser = argparse.ArgumentParser(description='''War Game Simulator for CS 440 by
                                                    Shibo Yao, Mike Chen,
                                                    and Jeff Zhu''')
    parser.add_argument('fname', help='Input Board')
    parser.add_argument('runmode', help='''Choose a mode: MvM, ABvAB, MvAB, ABvM''')
    args = parser.parse_args()

    wg = WarGame(args.fname, args.runmode)
    print('Running War Game with matchup:', args.runmode)
    simulate(wg, args.runmode)


if __name__ == '__main__':
    main()