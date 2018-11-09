
# original: https://github.com/int8/monte-carlo-tree-search.git
# notice: 这段代码是我 参照了上面项目的设计 编写的
# content：蒙特卡洛搜索树的节点类，及其子类的两人博弈类的设计实现

import numpy as np
from collections import defaultdict
from game.boardstate import GameState

class MonteCarloTreeSearchNode:

    def __init__(self, state: GameState, parent=None):
        self.state = state
        self.parent = parent
        self.children = []

    @property
    def untried_actions(self):
        raise NotImplemented()

    @property
    def q(self):
        raise NotImplemented()

    @property
    def n(self):
        raise NotImplemented()

    @property
    def expand(self):
        raise NotImplemented()

    def is_terminal_node(self):
        raise NotImplemented()

    def rollout(self):
        raise NotImplemented()

    def backpropagate(self, reward):
        raise NotImplemented()

    def is_full_expand(self):
        return len(self.untried_actions) == 0

    def choose_best_child(self, c_param=1.4):
            choices_weight = [
                (c.q / (c.n)) + c_param * np.sqrt((2 * np.log(self.n) / (c.n)))
                for c in self.children
            ]

            return self.children[np.argmax(choices_weight)]

    def rollout_policy(self, possible_moves):
        """ 随机选择下棋动作的移动策略
        :param possible_moves: list 所有的下棋动作列表
        :return: MoveAction 一个下棋动作
        """
        return possible_moves[np.random.randint(len(possible_moves))]


class TwoPlayerGameMonteCarloTreeSearchNode(MonteCarloTreeSearchNode):

    def __init__(self, state: GameState, parent=None):
        super(TwoPlayerGameMonteCarloTreeSearchNode, self).__init__(state, parent)
        self.number_of_visits = 0
        self.results = defaultdict(int)
        self.best_child = None

    @property
    def untried_actions(self):
        if not hasattr(self, '_untried_actions'):
            self._untried_actions = self.state.get_legal_actions()
        return self._untried_actions

    @untried_actions.setter
    def untried_actions(self, actions):
        self._untried_actions = actions

    @property
    def q(self):
        wins = self.results[self.parent.state.next_to_move]
        loses = self.results[-1 * self.parent.state.next_to_move]
        return wins - loses

    @property
    def n(self):
        return self.number_of_visits

    def expand(self):
        action = self._untried_actions.pop()
        next_state = self.state.place(action)
        child_node = TwoPlayerGameMonteCarloTreeSearchNode(next_state, parent=self)
        self.children.append(child_node)
        return child_node

    def is_terminal_node(self):
        return self.state.is_game_over()

    def rollout(self):
        current_rollout_state = self.state
        while not current_rollout_state.is_game_over():
            possible_moves = current_rollout_state.get_legal_actions()
            action = self.rollout_policy(possible_moves)
            current_rollout_state = current_rollout_state.place(action)

        return current_rollout_state.game_result()

    def backpropagate(self, result):
        self.number_of_visits += 1
        self.results[result] += 1

        if self.parent:
            self.parent.backpropagate(result)

    def choose_best_child(self, c_param=1.4):
        self.best_child = super().choose_best_child(c_param=c_param)
        return self.best_child

    def get_children_result(self, c_param=1.4):
        """ 获取每个儿子节点的模拟结果
        :return:  list 儿子模拟结果的列表
        """
        choices_weight = [
            (c.q / c.n) + c_param * np.sqrt((2 * np.log(self.n) / (c.n)))
            for c in self.children
        ]
        return choices_weight



