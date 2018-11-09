
# content: 决策树模拟和alpha-beta裁剪算法

from game.boardstate import GameState
import copy

class AlphaBetaCutSearch(object):

    def find_comp_move(self, state: GameState, alpha, beta, deep):
        """模拟人机的移动
            寻找对于自己当前局势最有利的移动
        :param
            state: GameState 当前棋盘的局势状态
            alpha: int alpha裁剪的判断条件
            beta: int beta裁剪的判断条件
            deep: int 用于限制决策的深度，还能再深入几层
        :return: 决策树选择的棋局结果
        """

        if state.is_game_over() or deep == 0:
            value = state.game_result()
            if value == None:       # 若当前没有结果则当成平局来算
                value = 0
        else:
            value = alpha
            actions_list = state.get_legal_actions()
            i = 0
            while i < len(actions_list) and value < beta:
                state_copy = state.place(actions_list[i])
                if state.is_game_over():
                    response = state.game_result()
                else:
                    response = self.find_human_move(state_copy, value, beta, deep-1)
                if response > value:
                    value = response
                i += 1
        return value

    def find_human_move(self, state: GameState, alpha, beta, deep):
        """ 模拟人类的移动，寻找对与敌人当前局势最不利的移动
        :param
            state: GameState 当前棋盘的局势状态
            alpha: int alpha裁剪的判断条件
            beta: int beta裁剪的判断条件
            deep: int 用于限制决策的深度，还能再深入几层
        :return: 决策树选择的棋局结果
        """

        if state.is_game_over() or deep == 0:
            value = state.game_result()
            if value == None:       # 若当前没有结果则当成平局来算
                value = 0
        else:
            value = beta
            actions_list = state.get_legal_actions()
            i = 0

            while i < len(actions_list) and value > alpha:
                state_copy = state.place(actions_list[i])
                if state.is_game_over():
                    response = state.game_result()
                else:
                    response = self.find_comp_move(state_copy, alpha, value, deep-1)
                if response < value:
                    value = response
                i += 1
        return value





