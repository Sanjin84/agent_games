from player_base import Player

class New2_Player(Player):
    def make_decision(self, game_state):
        if game_state['unbanked_money'][self.name] >= 22:
            return 'bank'
        return 'continue'