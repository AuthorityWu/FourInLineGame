
# content: 简单玩家类的设计与实现。使用多线程进行后台人机下棋模拟

import abc
from mcts.search import *
from mcts.node import TwoPlayerGameMonteCarloTreeSearchNode
from four_in_row.FourInRow import *
from threading import Thread
import time

class Player(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def choose_next_move(self, node: TwoPlayerGameMonteCarloTreeSearchNode, game_window: GameWindow):
        """ 选择下一步

        :param
            node: 当前棋局走势的节点（蒙特卡洛模拟树的一个节点）
        :return: 下一个棋局走势的节点
        """
        raise NotImplemented()

    @abc.abstractmethod
    def __repr__(self):
        raise NotImplemented()


class ComputerPlayer(Player):

    def choose_next_move(self, node, game_window):
        """ 选择人机的下一步，并在窗口显示

        :param node: 当前蒙特卡洛树的节点
        :param game_window: GameWindow 游戏窗口
        :return: TwoPlayerGameMonteCarloTreeSearchNode 最新的蒙特卡洛节点
        """
        print("人机下棋：")
        start = time.time()
        search = AlphaBetaAndSimulator(node)
        simulator_number = 6000
        # 开启线程进行人机下棋模拟
        simulations_thread = Thread(target=search.best_action, args=(simulator_number,))
        simulations_thread.start()
        simulations_thread.join()

        new_node = search.root.best_child
        game_window.move_and_update(new_node.state.pre_action)
        end = time.time()
        print("用时：", end-start)
        return new_node

    def __repr__(self):
        return "Computer"


class HumanPlayer(Player):

    def choose_next_move(self, node, game_window):
        """ 选择人的下一步，并在窗口显示

        :param node: 当前蒙特卡洛树的节点
        :param game_window: GameWindow 游戏窗口
        :return: TwoPlayerGameMonteCarloTreeSearchNode 最新的蒙特卡洛节点
        """
        print("人下棋：")
        action = game_window.getHumanMove()
        new_state = node.state.place(action)
        new_node = TwoPlayerGameMonteCarloTreeSearchNode(new_state, node)
        return new_node

    def __repr__(self):
        return "Human"
