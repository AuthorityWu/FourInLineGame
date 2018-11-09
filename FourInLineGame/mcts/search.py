# original: https://github.com/int8/monte-carlo-tree-search.git
# notice: class MCTS 是我 参照了上面项目的设计 编写的
# content：模拟、搜索获取人机的下棋动作，涉及 蒙特卡洛算法 和 决策树alpha-beta裁剪，还有多进程进程提高运算速度。

from mcts.node import TwoPlayerGameMonteCarloTreeSearchNode
from abts.alpha_beta_tree import AlphaBetaCutSearch
from game.boardstate import *
from threading import Thread
import copy
from multiprocessing import Pool, Process


class MCTS(object):

    def __init__(self, node: TwoPlayerGameMonteCarloTreeSearchNode):
        self.root = node

    def best_action(self, simulations_number):
        """ 进行蒙特卡洛模拟法进行模拟
        :param simulations_number: int 模拟次数，模拟次数越高，结果越精确
        :return: TwoPlayerGameMonteCarloTreeSearchNode 最好的儿子（最好的下一步）
        """
        self.simulation(simulations_number)
        return self.root.choose_best_child()

    def tree_policy(self):
        current_node = self.root
        while not current_node.is_terminal_node():
            if not current_node.is_full_expand():
                return current_node.expand()
            else:
                current_node = current_node.choose_best_child()
        return current_node

    def simulation(self, simulations_number):
        for _ in range(0, int(simulations_number)):
            v = self.tree_policy()
            reward = v.rollout()
            v.backpropagate(reward)
        return self


class AlphaBetaAndSimulator(MCTS):
    """ 结合 博弈树alpha-beta裁剪 和 蒙特卡洛搜索树算法的 下棋模拟类
    """

    def __init__(self, node: TwoPlayerGameMonteCarloTreeSearchNode):
        super(AlphaBetaAndSimulator, self).__init__(node)

    def best_action(self, simulations_number):
        """ 选择最好的移动
            先进行蒙特卡洛模拟法进行模拟,再通过alpha-beta裁剪的博弈树
            进行后4步的模拟，最后得出最优的移动

        :param
            simulations_number: 模拟次数，模拟次数越高，结果越精确
        :return: 最好的儿子（下一步）
        """
        # 若是开局第一或第二步，则选特殊函数进行模拟
        if self.root.parent == None or self.root.parent.parent == None:
            return self.first_and_second_choose()

        self.pool_simulation(simulations_number)
        return self.alpha_beta_cut_simulations()

    def alpha_beta_cut_simulations(self):
        """ 利用alpha-beta裁剪的博弈树进行后4步的模拟，获取最优的移动

        :return: TwoPlayerGameMonteCarloTreeSearchNode 最优的儿子
        """
        # print("开始裁剪")
        alpha_beta_cut_search = AlphaBetaCutSearch()
        i = 0
        simulations_result = self.root.get_children_result(c_param=0)
        count = len(simulations_result)
        deep = 3 if len(simulations_result) > 3 else len(simulations_result)    # 模拟的步数

        best_result = -1        # 棋盘的结果
        best_result_index = 0   # 最优儿子的下标
        while best_result != 1 and i < count:           # 决策树模拟所有下棋动作，直到结束或获得必胜的结果
            state = copy.deepcopy(self.root.children[i].state)
            response = alpha_beta_cut_search.find_human_move(
                state, alpha=-1, beta=1, deep=deep)

            if best_result <= response:
                if (best_result == response and
                        simulations_result[i] >= simulations_result[best_result_index]):
                    # 当两个下棋动作的决策树结果都是一样，选择蒙特卡洛模拟结果较大的一方
                    best_result = response
                    best_result_index = i
                    self.root.best_child = self.root.children[i]
                elif best_result < response:        # 选择决策树模拟的结果较大的下棋动作。
                    best_result = response
                    best_result_index = i
                    self.root.best_child = self.root.children[i]
            i += 1

        return self.root.best_child

    def first_and_second_choose(self):
        """ 获取第一步或第二步的下法（第一、第二步要达到较为精准，需要的模拟次数太大）

        :return: TwoPlayerGameMonteCarloTreeSearchNode 最好的儿子
        """

        if self.root.parent == None:    # 无父结点说明为第一步,选最中间下棋
            action = MoveAction(
                int(self.root.state.board_row/2),
                int(self.root.state.board_col/2), self.root.state.black_chess
            )
            new_state = self.root.state.place(action)
            new_node = TwoPlayerGameMonteCarloTreeSearchNode(
                new_state, self.root
            )
            self.root.best_child = new_node
            return new_node
        else:
            pre_action = self.root.state.pre_action     # 获取对手的第一步
            actions = []
            simulation_number = 3000    # 模拟次数

            # 根据对手的第一步，获取他周围可下的下棋动作，进行蒙特卡洛模拟
            if (pre_action.y != self.root.state.board_row - 1
                    and pre_action.x != self.root.state.board_col - 1):
                actions.append(MoveAction(
                    pre_action.y+1, pre_action.x+1, pre_action.chess_type*(-1))
                )
            if pre_action.y != 0 and pre_action.x != 0:
                actions.append(MoveAction(
                    pre_action.y - 1, pre_action.x - 1, pre_action.chess_type*(-1))
                )
            if (pre_action.x != self.root.state.board_col - 1 and
                    pre_action.y != 0):
                actions.append(MoveAction(
                    pre_action.y-1, pre_action.x+1, pre_action.chess_type * (-1))
                )
            if (pre_action.x != 0 and
                pre_action.y != self.root.state.board_row - 1):
                actions.append(MoveAction(
                    pre_action.y+1, pre_action.x-1, pre_action.chess_type * (-1))
                )

            self.root.untried_actions = actions
            self.simulation(simulation_number)
        return self.root.choose_best_child()

    def pool_simulation(self, simulations_number):
        """ 使用多进程进行同时对多棵蒙特卡洛模拟树进行模拟，提高模拟速度

        :param simulations_number:  int 模拟次数
        """

        process_num = 2                 # 额外开启的进程个数
        pool = Pool(process_num)        # 进程池
        pool_missions = []              # 进程的任务
        simulations_trees = []          # 模拟树

        for i in range(0, process_num):
            simulations_trees.append(self)

        for _ in range(0, process_num):
            pool_missions.append(pool.apply_async(
                func=simulations_trees[i].simulation, args=(int(simulations_number / process_num),))
            )
        pool.close()
        pool.join()

        for i in range(0, process_num):
            simulations_trees[i] = pool_missions[i].get()

        self.root = simulations_trees[process_num-1].root   # 将最后一棵树的结果当成root的模拟结果
        for i in range(len(self.root.children)):            # 将所有模拟树得到的模拟数据进行合并
            for j in range(process_num-1):
                self.root.children[i].results[1] += simulations_trees[j].root.children[i].results[1]
                self.root.children[i].results[-1] += simulations_trees[j].root.children[i].results[-1]
                self.root.children[i].results[0] += simulations_trees[j].root.children[i].results[0]
                self.root.children[i].number_of_visits += simulations_trees[j].root.children[i].n

        self.root.number_of_visits = simulations_number
