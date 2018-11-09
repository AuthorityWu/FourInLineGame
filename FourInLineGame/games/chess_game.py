
# content: 简单的游戏启动类

from game.player import *
import numpy as np
from game.boardstate import *
import tkinter.messagebox


class ChessGame(object):
    def __init__(self):
        self.player1 = HumanPlayer()
        self.player2 = ComputerPlayer()
        self.init_state = None
        self.mcst_node = None
        self.game_window = GameWindow()

    @property
    def get_sente(self):
        """ 获取先后手
            :return 人先手 -1 人机先手1
        """
        if np.random.randint(2):
            print(self.player2, end=' ')
            return 1
        else:
            print(self.player1, end=' ')
            return -1

    def start_one_game(self):
        sente = self.get_sente
        print("先手")
        self.init_state = GameState(
            np.zeros((self.game_window.BOARDHEIGHT, self.game_window.BOARDWIDTH)),
            sente, None)  # 获取初始棋盘
        self.mcst_node = TwoPlayerGameMonteCarloTreeSearchNode(self.init_state, None)   # 蒙特卡洛root节点
        result = None
        count = 0 if sente == -1 else 1

        while result == None:
            if count%2 == 0:
                self.mcst_node = self.player1.choose_next_move(self.mcst_node, self.game_window)
            else:
                self.mcst_node = self.player2.choose_next_move(self.mcst_node, self.game_window)
            count += 1
            result = self.mcst_node.state.game_result()
            print(self.mcst_node.state.board)

        return result

    def game_start(self):

        result = self.start_one_game()
        if result == 1:
            print(self.player2, " Win!")
            tkinter.messagebox.showinfo("Winner", "人机获胜!")
        elif result == -1:
            print(self.player1, " Win!")
            tkinter.messagebox.showinfo("Winner", "人获胜!")
        else:
            print("Deuce!")
            tkinter.messagebox.showinfo("Deuce", "平局")


def main():
    chessgame = ChessGame()
    chessgame.game_start()

if __name__ == '__main__':
    main()




