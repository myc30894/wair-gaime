import argparse
import logging

from collections import Counter


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WarGame:

    def __init__(self, fname, runmode):
        self.board = []
        self.score = {'green': 0, 'blue': 0}
        self.open = 0
        try:
            with open(fname) as f:
                for idx, line in enumerate(f):
                    self.board.append([])
                    for col, char in enumerate(line.split('\t')):
                        self.board[idx].append({'value': int(char), 'team': None})
                        self.open += 1

        except OSError:
            logger.error('Could not open board.')



def main():
    parser = argparse.ArgumentParser(description='''War Game Simulator for CS 440 by
                                                    Shibo Yao, Mike Chen,
                                                    and Jeff Zhu''')
    parser.add_argument('fname', help='Input Board')
    parser.add_argument('runmode', help='''Choose a mode: MvM, ABvAB, MvAB, ABvM''')
    args = parser.parse_args()

    wg = WarGame(args.fname, args.runmode)


if __name__ == '__main__':
    main()