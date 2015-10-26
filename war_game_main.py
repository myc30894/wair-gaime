from copy import deepcopy
import argparse
import logging
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

        loc_team = self.board[loc[0]][loc[1]]['team']
        if loc_team and loc_team!= team:
            self.score[loc_team] -= self.board[loc[0]][loc[1]]['value']

        self.score[team] += self.board[loc[0]][loc[1]]['value']
        self.board[loc[0]][loc[1]]['team'] = team

        return

    def __conquer_neighbors(self, loc, team, opponent, max_player):
        neighbors = [(loc[0]+1, loc[1]), (loc[0]-1, loc[1]), (loc[0], loc[1]+1), (loc[0], loc[1]-1)]

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
    minimax_board = deepcopy(board)

    if depth == 3:
        if max_player:
            return max(minimax(minimax_board, team, opponent, max_player, depth-1, unoccupied) for unoccupied in minimax_board.open)
        else:
            return min(minimax(minimax_board, team, opponent, max_player, depth-1, unoccupied) for unoccupied in minimax_board.open)
   
    # Attempt Blitz
    minimax.nodes += 1

    minimax_board._make_move(loc, 1, team, max_player)

    if (len(minimax_board.open) == 0) or (depth <= 0):
        return [(minimax_board.score[team] if max_player else minimax_board.score[opponent]), loc]

    if max_player:
        retval = min(minimax(minimax_board, opponent, team, not max_player, depth-1, unoccupied) for unoccupied in minimax_board.open)
        retval[1] = loc
        return retval
    else:
        retval = max(minimax(minimax_board, opponent, team, not max_player, depth-1, unoccupied) for unoccupied in minimax_board.open)
        retval[1] = loc
        return retval

def simulate(game, runmode):
    if(runmode == 'MvM'):
        expanded_nodes = {'blue': [], 'green':[]}
        current_team = 'blue'
        opponent_team = 'green'
        max_player = True
        total_nodes = 0
        while(game.open):
            minimax.nodes = 0
            result = minimax(game, current_team, opponent_team, max_player, 3)
            game._make_move(result[1], 1, current_team, max_player)
            print(minimax.nodes, current_team)
            total_nodes += minimax.nodes
            expanded_nodes[current_team].append(minimax.nodes) 
            current_team, opponent_team = opponent_team, current_team
        print("green:", expanded_nodes['green'])
        print("blue:", expanded_nodes['blue'])
        print(game.score)
        print(game.board)
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