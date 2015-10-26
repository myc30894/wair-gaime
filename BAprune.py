from copy import deepcopy
import war_game_main

def ba_prune(orig_col, orig_en, cur_color, other_color, board, max_depth=3, cur_depth = 0, loc = None, alpha = [-100000, None], beta = [100000, None]):
    # types: string, string, string, string, class, int, int, array[2], array[2], array [2]
    # goal is to keep going until cur_depth is greater than max depth and then return location after pruning

    copied_board = deepcopy(board)
    nodes_searched = 1
    if cur_depth == 0:
        nodes_searched = 1
        # team to go first is blue so it will be the "max"
        if cur_color == orig_col:
            ret_val = max(ba_prune(orig_col, orig_en, cur_color, other_color, copied_board, max_depth, cur_depth+1, n_loc) for n_loc in copied_board.open)
            return ret_val
        else:
            ret_val = min(ba_prune(orig_col, orig_en, cur_color, other_color, copied_board, max_depth, cur_depth+1, n_loc) for n_loc in copied_board.open)
            return ret_val
    #attempt blitz
    copied_board._make_move(loc, 1, cur_color, orig_col)

    # returns the alpha/beta, and location when hitting the bottom
    if cur_depth >= max_depth or len(copied_board.open) == 0:
        return [copied_board.score[orig_col] - copied_board.score[orig_en], loc]
    else:
        if cur_color != orig_col:
            for next in copied_board.open:
                alpha = max(alpha,ba_prune(orig_col, orig_en, cur_color, other_color, copied_board, max_depth, cur_depth+1, next, alpha, beta))
                if beta <= alpha:
                    # prune
                    break
            alpha[1] = loc
            return alpha
        else:
            for next in copied_board.open:
                beta = min(beta,ba_prune(orig_col, orig_en, cur_color, other_color, copied_board, max_depth, cur_depth+1, next, alpha, beta))
                if beta <= alpha:
                    # prune
                    break
            beta[1] = loc
            return beta
