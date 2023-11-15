from abc import ABC, abstractmethod

class Player(ABC):
    def __init__(self, name, password):
        self.name = name
        self.password = password
        self.banked_money = 0
        self.unbanked_money = 0

    def reset_unbanked_money(self):
        self.unbanked_money = 0

    def bank_money(self):
        self.banked_money += self.unbanked_money
        self.reset_unbanked_money()

    def my_rank(self, game_state):
        # Extract the points_aggregate dictionary
        points_aggregate = game_state['points_aggregate']
        # Sort the dictionary by its values in descending order
        sorted_players = sorted(points_aggregate, key=points_aggregate.get, reverse=True)
        try:
            rank = sorted_players.index(self.name) + 1
            return rank
        except ValueError:
            return 0

    @abstractmethod
    def make_decision(self, game_state):
        pass