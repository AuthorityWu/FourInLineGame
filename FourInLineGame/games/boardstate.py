
# original: https://github.com/int8/monte-carlo-tree-search.git
# notice: 这段代码是我 参照了上面项目的设计 编写的
# content：下棋动作类和四字棋游戏状态类的设计、实现

from game.common import TwoPlayerGameState
from game.common import Action
import numpy as np

class MoveAction(object):
    def __init__(self, y, x, chess_type):
        self.chess_type = chess_type
        self.x = x
        self.y = y

    def __repr__(self):
        return "x:" + str(self.x) + " y:" + str(self.y) + " v:" + str(self.chess_type)


class GameState(object):

    red_chess = -1
    black_chess = 1

    def __init__(self, board, next_to_move, pre_action: MoveAction=None):
        self.board = board
        self.next_to_move = next_to_move
        self.board_row = len(board)
        self.board_col = len(board[0])
        self.pre_action = pre_action

    def is_actions_legal(self, action):
        """ 判断当前的下棋动作是否合法

        :param action: MoveAction 下棋动作
        :return: bool 合法 True 非法 False
        """
        # 判断棋子类型是否正确
        if action.chess_type != self.next_to_move:
            return False
        # 判断该移动是否再棋盘范围
        if action.x >= self.board_col or action.x < 0:
            return False
        if action.y >= self.board_row or action.y < 0:
            return False
        # 判断该位置是否已被占用
        return self.board[action.y, action.x] == 0

    def get_legal_actions(self):
        """ 获取当前棋盘状态上，所有的合法下棋的位置

        :return: list[] 返回一个下棋动作列表
        """
        legal_actions = np.where(self.board == 0)
        return [
            MoveAction(coords[0], coords[1], self.next_to_move)
            for coords in list(zip(legal_actions[0], legal_actions[1]))
        ]

    def place(self, action):
        """ 放置棋子
        为了保存每一步的状态，选择创建并返回一个放置棋子后的最新的棋盘状态。
        （没有选择共用一个棋盘）

        :param action: MoveAction 下棋动作
        :return: 最新的棋盘状态
        """

        if not self.is_actions_legal(action):
            raise ValueError("move " + action + " on board " + self.board + " is not legal")
        new_board = np.copy(self.board)
        new_board[action.y, action.x] = action.chess_type
        next_to_move = (GameState.black_chess if self.next_to_move == GameState.red_chess
                        else GameState.red_chess)

        return GameState(new_board, next_to_move, action)

    def is_board_full(self):
        """ 判断棋盘是否已满
        :return: bool
        """
        return len(np.where(self.board == 0)[0]) == 0

    def is_game_over(self):
        """ 判断游戏是否结束
        :return: bool
        """
        return self.game_result() != None

    def game_result(self):
        """ 获取当前棋盘状态的结果
            利用最新一步棋的位置来进行判断（非遍历棋盘），获取结果

        :return: 棋盘的结果（玩家赢-1，人机赢1，平局0，无结果None）
        """

        if self.pre_action == None:
            return None

        chess_type = self.pre_action.chess_type

        # 判断是否四子连成一线
        # 判断 斜向右下 是否有四子
        x = self.pre_action.x
        y = self.pre_action.y
        count = 1       # 记录连续的相同的棋子的个数
        while (y - 1 >= 0 and x - 1 >= 0
               and self.board[y - 1, x - 1] == chess_type):
            # 从当前的位置（y,x）向左上移动直到越界或棋子类型不同
            x -= 1
            y -= 1
        while (y + 1 < self.board_row and x + 1 < self.board_col
               and self.board[y + 1, x + 1] == chess_type):
            # 从刚刚找到的位置（y,x）开始向右下移动,直到越界或棋子类型不同
            count += 1
            y += 1
            x += 1
        if count >= 4:      # 若连续的相同的棋子是否 >= 4，则有游戏结果
            return chess_type

        # 判断 斜向左下 是否有四子
        x = self.pre_action.x
        y = self.pre_action.y
        count = 1
        while (y - 1 >= 0 and x + 1 < self.board_col
               and self.board[y - 1, x + 1] == chess_type):
            x += 1
            y -= 1
        while (y + 1 < self.board_row and x - 1 >= 0
               and self.board[y + 1, x - 1] == chess_type):
            count += 1
            y += 1
            x -= 1
        if count >= 4:
            return chess_type

        # 判断 竖直 是否有四子
        x = self.pre_action.x
        y = self.pre_action.y
        count = 1
        while y - 1 >= 0 and self.board[y - 1, x] == chess_type:
            y -= 1
        while y + 1 < self.board_row and self.board[y + 1, x] == chess_type:
            count += 1
            y += 1
        if count >= 4:
            return chess_type

        # 判断 水平 是否有四子
        x = self.pre_action.x
        y = self.pre_action.y
        count = 1
        while x - 1 >= 0 and self.board[y, x - 1] == chess_type:
            x -= 1
        while x + 1 < self.board_col and self.board[y, x + 1] == chess_type:
            count += 1
            x += 1
        if count >= 4:
            return chess_type

        if self.is_board_full():    # 若当前棋盘已满却没有赢，则平局
            return 0
        else:                       # 若不赢不平，则无结果
            return None


