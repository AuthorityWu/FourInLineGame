
# original: https://github.com/int8/monte-carlo-tree-search.git
# notice: 来源于上面项目的设计

class TwoPlayerGameState:
    def __init__(self, state, next_to_move):
        self.state = state
        self.next_to_move = next_to_move

    def game_result(self):
        raise NotImplemented()

    def is_game_over(self):
        raise NotImplemented()

    def place(self, action):
        raise NotImplemented()

    def get_legal_actions(self):
        raise NotImplemented()

class Action:
    pass