from player_base import Player

class Testing_Player(Player):
    def make_decision(self, game_state):
        import random
        threshold = 1
        #bank if I have won
        if game_state['unbanked_money'][self.name] + game_state['banked_money'][self.name] >= 100:
            return 'bank'
        #continue if I am close to winning
        if game_state['unbanked_money'][self.name] + game_state['banked_money'][self.name] >= 96:
            return 'continue'
        if self.my_rank(game_state) > 5 and game_state['points_aggregate'][self.name] > 80:
            return 'continue'
        if game_state['unbanked_money'][self.name] >= threshold:
            if random.randint(0,10) >1:
                return 'bank' 

        #if I am ranked last then continue
        return 'continue'