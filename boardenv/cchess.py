import copy
import itertools
import sys

import numpy as np

from .env import BoardGameEnv

letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
dict_letters = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, }
# numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
numbers = ['9', '8', '7', '6', '5', '4', '3', '2', '1', '0']
dict_numbers = {'0': 9, '1': 8, '2': 7, '3': 6, '4': 5,
                '5': 4, '6': 3, '7': 2, '8': 1, '9': 0}


# dict_numbers = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
#                 '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}


def mv_to_str(x1, y1, x2, y2):
    return letters[x1] + numbers[y1] + letters[x2] + numbers[y2]


def str_to_mv(s):
    return dict_letters[s[0]], dict_numbers[s[1]], \
           dict_letters[s[2]], dict_numbers[s[3]]


dict_mv = {}


# 创建所有合法走子UCI，size 2086
def create_uci_labels():
    labels_array = []
    shi_labels = ['d7e8', 'e8d7', 'e8f9', 'f9e8', 'd0e1', 'e1d0', 'e1f2', 'f2e1',
                  'd2e1', 'e1d2', 'e1f0', 'f0e1', 'd9e8', 'e8d9', 'e8f7', 'f7e8']
    xiang_labels = ['a2c4', 'c4a2', 'c0e2', 'e2c0', 'e2g4', 'g4e2', 'g0i2', 'i2g0',
                    'a7c9', 'c9a7', 'c5e7', 'e7c5', 'e7g9', 'g9e7', 'g5i7', 'i7g5',
                    'a2c0', 'c0a2', 'c4e2', 'e2c4', 'e2g0', 'g0e2', 'g4i2', 'i2g4',
                    'a7c5', 'c5a7', 'c9e7', 'e7c9', 'e7g5', 'g5e7', 'g9i7', 'i7g9']
    for x1 in range(9):
        for y1 in range(10):
            dests = [(x2, y1) for x2 in range(9)] + \
                    [(x1, y2) for y2 in range(10)] + \
                    [(x1 + a, y1 + b) for (a, b) in
                     [(-2, -1), (-1, -2), (-2, 1), (1, -2),
                      (2, -1), (-1, 2), (2, 1), (1, 2)]]  # 马走日
            for (x2, y2) in dests:
                if (x1, y1) != (x2, y2) and x2 in range(9) and y2 in range(10):
                    mv_str = mv_to_str(x1, y1, x2, y2)
                    dict_mv[mv_str] = len(labels_array)
                    labels_array.append(mv_str)

    for p in shi_labels:
        dict_mv[p] = len(labels_array)
        labels_array.append(p)

    for p in xiang_labels:
        dict_mv[p] = len(labels_array)
        labels_array.append(p)

    return labels_array


labels_mv = create_uci_labels()

# print('len_labels_mv: ', len(labels_mv))
EMPTY = 0
BLACK = 1  # 红
WHITE = -1  # 黑

PIECE_JIANG = 0
PIECE_SHI = 1
PIECE_XIANG = 2
PIECE_MA = 3
PIECE_JU = 4
PIECE_PAO = 5
PIECE_BING = 6


def strfboard(board):
    # s = ''
    # for j in range(10):
    #     for i in range(9):
    #         p = board[j][i]
    return ''.join([str(p) for row in board for p in row])
    # return s


init_board = np.array(
    [[20, 19, 18, 17, 16, 17, 18, 19, 20],
     [0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 21, 0, 0, 0, 0, 0, 21, 0],
     [22, 0, 22, 0, 22, 0, 22, 0, 22],
     [0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0],
     [14, 0, 14, 0, 14, 0, 14, 0, 14],
     [0, 13, 0, 0, 0, 0, 0, 13, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0],
     [12, 11, 10, 9, 8, 9, 10, 11, 12]])

arr_injiugong = np.array([
    [0, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0, 0]])

# (x, y)
jiang_delta = ((1, 0), (0, 1), (-1, 0), (0, -1))
shi_delta = ((1, 1), (-1, 1), (-1, -1), (1, -1))
xiang_delta = ((2, 2), (-2, 2), (-2, -2), (2, -2))
# 马的步长，以帅(将)的步长作为马腿（固定起点）
ma_delta = (((2, -1), (2, 1)), ((1, 2), (-1, 2)),
            ((-2, 1), (-2, -1)), ((-1, -2), (1, -2)))
ma_delta2 = ((2, -1), (2, 1), (1, 2), (-1, 2),
             (-2, 1), (-2, -1), (-1, -2), (1, -2))
# 马将军的步长，以仕(士)的步长作为马腿（固定终点）
ma_check_delta = (((2, 1), (1, 2)), ((-1, 2), (-2, 1)),
                  ((-2, -1), (-1, -2)), ((1, -2), (2, -1)))

ma_pin_dict = {-2: -1, -1: 0, 1: 0, 2: 1}


def is_jiang_legalmove(x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    return (dx, dy) in jiang_delta


def is_shi_legalmove(x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    return (dx, dy) in shi_delta


def is_xiang_legalmove(x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    return (dx, dy) in xiang_delta


def ma_pin(x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    if not (dx, dy) in ma_delta2:
        return x1, y1
    return x1 + ma_pin_dict[dx], y1 + ma_pin_dict[dy]


def is_inboard(x, y):
    return 0 <= x <= 8 and 0 <= y <= 9


def is_injiugong(x, y):
    return is_inboard(x, y) and arr_injiugong[y][x] == 1


def flip_x(x):
    return 8 - x


def flip_y(y):
    return 9 - y


def flip_xy(x, y):
    return 8 - x, 9 - y


def sq_forward(y, player):
    return y - 1 if player == BLACK else y + 1


def xiang_pin(x1, y1, x2, y2):
    return (x1 + x2) // 2, (y1 + y2) // 2


# def ma_pin(x1, y1, x2, y2):
#     pass


def is_self_half(y, player):
    return y >= 5 if player == BLACK else y <= 4


def is_away_half(y, player):
    return y <= 4 if player == BLACK else y >= 5


def is_same_half(y1, y2):
    return (y1 <= 4 and y2 <= 4) or (y1 >= 5 and y2 >= 5)


def side_tag(player):
    return 8 if player == BLACK else 16


def opp_side_tag(player):
    return 16 if player == BLACK else 8


def is_self_piece(pc, player):
    return (side_tag(player) & pc) != 0


def is_self_piece_by_tag(pc, tag):
    return (tag & pc) != 0


def is_opp_piece(pc, player):
    return (opp_side_tag(player) & pc) != 0


def is_opp_piece_by_tag(pc, tag):
    return (tag & pc) != 0


def gen_moves(board, player):
    # print(sys._getframe().f_code.co_name)
    mvs = []
    self_tag, opp_tag = side_tag(player), opp_side_tag(player)
    for x in range(9):
        for y in range(10):
            pc = board[y][x]
            if pc & self_tag == 0:
                continue
            piece = pc - self_tag
            if piece == PIECE_JIANG:
                for i in range(4):
                    dst_x, dst_y = x + jiang_delta[i][0], y + jiang_delta[i][1]
                    if not is_injiugong(dst_x, dst_y):
                        continue
                    pc_dst = board[dst_y][dst_x]
                    if pc_dst & self_tag == 0:
                        mvs.append((x, y, dst_x, dst_y))
            elif piece == PIECE_SHI:
                for i in range(4):
                    dst_x, dst_y = x + shi_delta[i][0], y + shi_delta[i][1]
                    if not is_injiugong(dst_x, dst_y):
                        continue
                    pc_dst = board[dst_y][dst_x]
                    if pc_dst & self_tag == 0:
                        mvs.append((x, y, dst_x, dst_y))
            elif piece == PIECE_XIANG:
                for i in range(4):
                    # 是象眼的位置
                    dst_x, dst_y = x + shi_delta[i][0], y + shi_delta[i][1]
                    if not (is_inboard(dst_x, dst_y) and
                            is_self_half(dst_y, player)
                            and board[dst_y][dst_x] == 0):
                        continue
                    dst_x += shi_delta[i][0]
                    dst_y += shi_delta[i][1]
                    pc_dst = board[dst_y][dst_x]
                    if pc_dst & self_tag == 0:
                        mvs.append((x, y, dst_x, dst_y))
            elif piece == PIECE_MA:
                for i in range(4):
                    pin_x, pin_y = x + jiang_delta[i][0], y + jiang_delta[i][1]
                    if not is_inboard(pin_x, pin_y) or board[pin_y][pin_x] != 0:
                        continue
                    for j in range(2):
                        dst_x, dst_y = x + ma_delta[i][j][0], y + ma_delta[i][j][1]
                        if not is_inboard(dst_x, dst_y):
                            continue
                        pc_dst = board[dst_y][dst_x]
                        if pc_dst & self_tag == 0:
                            mvs.append((x, y, dst_x, dst_y))
            elif piece == PIECE_JU:
                for i in range(4):
                    dst_x, dst_y = x + jiang_delta[i][0], y + jiang_delta[i][1]
                    while is_inboard(dst_x, dst_y):
                        pc_dst = board[dst_y][dst_x]
                        if pc_dst == 0:
                            mvs.append((x, y, dst_x, dst_y))
                        else:
                            if (pc_dst & opp_tag) != 0:
                                mvs.append((x, y, dst_x, dst_y))
                            break
                        dst_x += jiang_delta[i][0]
                        dst_y += jiang_delta[i][1]
            elif piece == PIECE_PAO:
                for i in range(4):
                    dst_x, dst_y = x + jiang_delta[i][0], y + jiang_delta[i][1]
                    while is_inboard(dst_x, dst_y):
                        pc_dst = board[dst_y][dst_x]
                        if pc_dst == 0:
                            mvs.append((x, y, dst_x, dst_y))
                        else:
                            break
                        dst_x += jiang_delta[i][0]
                        dst_y += jiang_delta[i][1]
                    dst_x += jiang_delta[i][0]
                    dst_y += jiang_delta[i][1]
                    while is_inboard(dst_x, dst_y):
                        pc_dst = board[dst_y][dst_x]
                        if pc_dst != 0:
                            if (pc_dst & opp_tag) != 0:
                                mvs.append((x, y, dst_x, dst_y))
                            break
                        dst_x += jiang_delta[i][0]
                        dst_y += jiang_delta[i][1]
            elif PIECE_BING:
                dst_x, dst_y = x, sq_forward(y, player)
                if is_inboard(dst_x, dst_y):
                    pc_dst = board[dst_y][dst_x]
                    if pc_dst & self_tag == 0:
                        mvs.append((x, y, dst_x, dst_y))
                if is_away_half(y, player):
                    for i in (-1, 1):
                        dst_x, dst_y = x + i, y
                        if is_inboard(dst_x, dst_y):
                            pc_dst = board[dst_y][dst_x]
                            if pc_dst & self_tag == 0:
                                mvs.append((x, y, dst_x, dst_y))
    return np.array(mvs)


def is_legalmove(board, x1, y1, x2, y2, player):
    # print(sys._getframe().f_code.co_name)
    # 1.
    if not is_inboard(x1, y1) or not is_inboard(x2, y2):
        return False
    self_tag = side_tag(player)
    pc_src = board[y1][x1]
    if (pc_src & self_tag) == 0:
        return False
    # 2.
    pc_dst = board[y2][x2]
    if pc_dst & self_tag != 0:
        return False
    # 3.
    piece = pc_src - self_tag
    if piece == PIECE_JIANG:
        return is_injiugong(x2, y2) and is_jiang_legalmove(x1, y1, x2, y2)
    elif piece == PIECE_SHI:
        return is_injiugong(x2, y2) and is_shi_legalmove(x1, y1, x2, y2)
    elif piece == PIECE_XIANG:
        pin_x, pin_y = xiang_pin(x1, y1, x2, y2)
        return is_same_half(y1, y2) and is_xiang_legalmove(x1, y1, x2, y2) \
               and board[pin_y][pin_x] == 0
    elif piece == PIECE_MA:
        pin_x, pin_y = ma_pin(x1, y1, x2, y2)
        return (pin_x != x1 or pin_y != y1) and board[pin_y][pin_x] == 0
    elif piece == PIECE_JU or piece == PIECE_PAO:
        # if piece == PIECE_JU:
        #     print('JU!')
        dx, dy = 0, 0
        if y1 == y2:
            dx = -1 if x2 < x1 else 1
        elif x1 == x2:
            dy = -1 if y2 < y1 else 1
        else:
            return False
        pin_x, pin_y = x1 + dx, y1 + dy
        while (pin_x != x2 or pin_y != y2) and board[pin_y][pin_x] == 0:
            pin_x += dx
            pin_y += dy
        if pin_x == x2 and pin_y == y2:
            return pc_dst == 0 or (pc_src - self_tag == PIECE_JU)
        elif (pc_dst != 0) and (pc_src - self_tag == PIECE_PAO):
            pin_x += dx
            pin_y += dy
            while (pin_x != x2 or pin_y != y2) and board[pin_y][pin_x] == 0:
                pin_x += dx
                pin_y += dy
            return pin_x == x2 and pin_y == y2
        else:
            return False
    elif piece == PIECE_BING:
        if is_away_half(y2, player) and y1 == y2 \
                and (x2 == x1 - 1 or x2 == x1 + 1):
            return True
        return sq_forward(y1, player) == y2 and x1 == x2
    return False


def is_checked(board, player):
    # print(sys._getframe().f_code.co_name)
    self_tag = side_tag(player)
    opp_tag = opp_side_tag(player)
    src_x, src_y = 0, 0
    ok = False
    for src_x in range(9):
        for src_y in range(10):
            if board[src_y][src_x] == self_tag + PIECE_JIANG:
                ok = True
                break
        if ok:
            break
    if not ok:
        return False
    # 1.Bing
    x, y = src_x, sq_forward(src_y, player)
    if is_inboard(x, y) and board[y][x] == opp_tag + PIECE_BING:
        return True
    for dx in (-1, 1):
        x, y = src_x + dx, src_y
        if is_inboard(x, y) and board[y][x] == opp_tag + PIECE_BING:
            return True
    # 2.Ma
    for i in range(4):
        x, y = src_x + shi_delta[i][0], src_y + shi_delta[i][1]
        if (not is_inboard(x, y)) or \
                (is_inboard(x, y) and board[y][x] != 0):
            continue
        for j in range(2):
            x = src_x + ma_check_delta[i][j][0]
            y = src_y + ma_check_delta[i][j][1]
            if is_inboard(x, y) and board[y][x] == opp_tag + PIECE_MA:
                return True
    # 3.Ju Pao Jiang
    for i in range(4):
        dx, dy = jiang_delta[i][0], jiang_delta[i][1]
        dst_x, dst_y = src_x + dx, src_y + dy
        while is_inboard(dst_x, dst_y):
            pc_dst = board[dst_y][dst_x]
            if pc_dst != 0:
                if pc_dst == opp_tag + PIECE_JIANG or \
                        pc_dst == opp_tag + PIECE_JU:
                    return True
                break
            dst_x += dx
            dst_y += dy
        dst_x += dx
        dst_y += dy
        while is_inboard(dst_x, dst_y):
            pc_dst = board[dst_y][dst_x]
            if pc_dst != 0:
                if pc_dst == opp_tag + PIECE_PAO:
                    return True
                break
            dst_x += dx
            dst_y += dy
    return False


def add_piece(board, x, y, pc):
    board[y][x] = pc


def del_piece(board, x, y):
    board[y][x] = 0


def move_piece(board, x1, y1, x2, y2):
    pc_killed = board[y2][x2]
    if pc_killed != 0:
        del_piece(board, x2, y2)
    pc_src = board[y1][x1]
    del_piece(board, x1, y1)
    add_piece(board, x2, y2, pc_src)
    return pc_killed


def undo_move_piece(board, x1, y1, x2, y2, pc_killed):
    pc = board[y2][x2]
    del_piece(board, x2, y2)
    add_piece(board, x1, y1, pc)
    if pc_killed != 0:
        add_piece(board, x2, y2, pc_killed)


def is_mate(board, player):
    mvs = gen_moves(board, player)
    for mv in mvs:
        pc_killed = move_piece(board, mv[0], mv[1], mv[2], mv[3])
        if not is_checked(board, player):
            undo_move_piece(board, mv[0], mv[1], mv[2], mv[3], pc_killed)
            return False
        else:
            undo_move_piece(board, mv[0], mv[1], mv[2], mv[3], pc_killed)
    return True


def is_jiang_exist(board, player):
    self_tag = side_tag(player)
    for x in range(9):
        for y in range(10):
            if board[y][x] == self_tag + PIECE_JIANG:
                return True
    return False


def board_to_net_input(board, player):
    input_arr = np.zeros(shape=(10, 9, 15))
    for j in range(10):
        for i in range(9):
            if board[j][i] != 0:
                n = board[j][i] - 16 + 7 \
                    if board[j][i] >= 16 else board[j][i] - 8
                input_arr[j][i][n] = 1
    # 红方的[:][:][14]=0，黑方=1
    if player == WHITE:
        for j in range(10):
            for i in range(9):
                input_arr[j][i][14] = 1
    return input_arr


class CChessEnv(BoardGameEnv):
    MAX_DEPTH = 500
    BOARD_SHAPE = (10, 9)

    def __init__(self, board_shape=(10, 9), render_characters='+ox'):
        super().__init__(board_shape=board_shape,
                         illegal_action_mode='pass', render_characters=render_characters,
                         allow_pass=False)
        self.reset()

    def reset(self):
        self.board = init_board
        self.player = BLACK
        self.depth = 0
        return self.board, self.player, self.depth

    # action是一个(1~2086)的列表
    def is_valid(self, state, action):
        board, player, _ = state
        x1, y1, x2, y2 = str_to_mv(labels_mv[action[0]])
        legal = is_legalmove(board, x1, y1, x2, y2, player)
        # if not legal:
        #     print(f'player: {player}, action: {labels_mv[action[0]]}')
        return legal

    def get_valid(self, state):
        board, player, _ = state
        mvs = gen_moves(board, player)
        A = np.zeros((2086,), dtype=float)
        for mv in mvs:
            s = mv_to_str(mv[0], mv[1], mv[2], mv[3])
            A[dict_mv[s]] = 1
        return A

    def has_valid(self, state):
        return True

    def step(self, action):
        state = (self.board, self.player, self.depth)
        next_state, reward, done, info = self.next_step(state, action)
        self.board, self.player, self.depth = next_state
        return next_state, reward, done, info

    def get_winner(self, state):
        # print(sys._getframe().f_code.co_name)
        board, player, depth = state
        if is_mate(board, player):
            return -player
        if not is_jiang_exist(board, player):
            return -player
        if not is_jiang_exist(board, -player):
            return player
        if depth >= self.MAX_DEPTH:
            return 0
        return None

    def get_next_state(self, state, action):
        # print(sys._getframe().f_code.co_name)
        board, player, depth = state
        board = copy.deepcopy(board)
        x1, y1, x2, y2 = str_to_mv(labels_mv[action[0]])
        move_piece(board, x1, y1, x2, y2)
        return board, -player, depth + 1

    def render(self, mode='human'):
        s = ''
        redf = '\033[1;31m%s\033[0m　'
        blackf = '\033[1;37m%s\033[0m　'
        piecestr_list = ['将', '士', '象', '马', '车', '炮', '兵']
        xlist = "\033[1m　　ａ　ｂ　ｃ　ｄ　ｅ　ｆ　ｇ　ｈ　ｉ\033[0m"
        ylist = "９８７６５４３２１０"
        s += f'{xlist}\n'
        for j in range(10):
            s += f'{ylist[j]}　'
            for i in range(9):
                p = self.board[j][i]
                if p == 0:
                    s += '\033[1m０\033[0m　'
                else:
                    f = blackf if p >= 16 else redf
                    s += f % (piecestr_list[p - 16] if p >= 16
                              else piecestr_list[p - 8])
            s += ylist[j]
            s += '\n'
            if j == 4:
                s += '　——————————————————————————————————\n'
        s += f'{xlist}\n'
        print(s)
