import random
import os
import time
from player_base import Player
import importlib.util
from rich.console import Console
from rich.table import Table
import json

class Dice:
    def roll(self):
        return random.randint(1, 6)

class Game:
    def __init__(self, player_classes):
        # Create player instances from the provided classes
        self.players = [PlayerClass(f"{filename[:-3]}", "abc123") for PlayerClass, filename in player_classes]
        self.active_players = list(self.players)
        self.dice = Dice()
        self.players_banked_this_round = []
        self.round_no = 0
        self.roll_no = 0

    def get_game_state(self):
        return {
            "round_no": self.round_no,
            "roll_no": self.roll_no,
            "players_banked_this_round": self.players_banked_this_round,
            "banked_money": {player.name: player.banked_money for player in self.players},
            "unbanked_money": {player.name: player.unbanked_money for player in self.players},
        }
    
    def play_round(self, verbose=False):
        self.players_banked_this_round = []
        self.round_no += 1
        self.roll_no = 0
        for player in self.active_players:
            player.reset_turn()  # Resetting the banking status at the start of each turn

        while True:
            self.roll_no += 1
            roll = self.dice.roll()
            if verbose:
                print('  ROLL #' + str(self.roll_no) + ':', 'Dice says', roll)
            # If roll is 1, all players lose unbanked money and the round ends
            if roll == 1:
                for player in self.active_players:
                    player.reset_unbanked_money()
                break

            # Process each player's turn
            for player in self.active_players:
                if not player.has_banked_this_turn:
                    player.unbanked_money += roll
                    decision = player.make_decision(self.get_game_state())
                    if decision == 'bank':
                        if verbose:
                            print('    *', player.name, 'banked $' + str(player.unbanked_money))
                        player.bank_money()
                        player.has_banked_this_turn = True
                        self.players_banked_this_round.append(player.name)
                        # Check if the player has won after banking
                        if player.banked_money >= 100:
                            return  # End the round if a player has won

            # Check if all players have banked, then end the round
            if all(player.has_banked_this_turn for player in self.active_players):
                break

    def play_game(self, verbose= False):
        #randomise the order of the players
        random.shuffle(self.players)
        while max(player.banked_money for player in self.players) < 100:
            self.active_players = list(self.players)  # reset active players for the round
            if verbose:
                print('\nSTART ROUND #' + str(self.round_no))
            self.play_round(verbose)
            if verbose:
                print('\n  END OF ROUND')
                for player in self.players:
                    print('  ' + player.name + ': $' + str(player.banked_money))
                time.sleep(2)

        game_state = self.get_game_state()
        return game_state


def run_simulation_with_animation(number, verbose=False, folder_name="classes"):
    all_players = get_all_player_classes_from_folder(folder_name)
    if not all_players:
        raise ValueError("No player classes provided.")
    with open('colors.json', 'r') as file:
        data = json.load(file)
        team_colors = {team["name"]: team["color"] for team in data["teams"]}

    # Dictionary to store the total points for each player
    total_points = {filename[:-3]: 0 for _, filename in all_players}
    games_won = {filename[:-3]: 0 for _, filename in all_players}
    top_5_finishes = {filename[:-3]: 0 for _, filename in all_players}
    games_played = {filename[:-3]: 0 for _, filename in all_players}
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")

    # Add columns to the table
    table.add_column("Player", justify="right", style="bold")
    table.add_column("Total Points", justify="right")
    table.add_column("Games Won", justify="right")
    table.add_column("Top 5", justify="right")
    table.add_column("Games Played", justify="right")
    current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"logfiles/game_simulation_{number}_runs_{current_time}.txt"
    start_time = time.time()
    for i in range(number):
        game = Game(all_players)
        game_result = game.play_game(verbose)
        points_this_game = assign_points(game_result)

        for player, points in points_this_game.items():
            total_points[player] += points
            games_played[player] += 1
            # Assuming you have a way to determine if a game is won or lost
            if game_result['banked_money'][player] > 100:
                games_won[player] += 1

        top_5_players = sorted(points_this_game, key=points_this_game.get, reverse=True)[:5]
        for player in top_5_players:
            top_5_finishes[player] += 1            

        if (i + 1) % 200 == 0 or i == number - 1:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Player", justify="right", style="bold")
            table.add_column("Total Points", justify="right")
            table.add_column("Games Won", justify="right")
            table.add_column("Top 5", justify="right")
            table.add_column("Games Played", justify="right")
            
            for player_name in sorted(total_points, key=total_points.get, reverse=True):
                player_color = team_colors.get(player_name, "white")
                table.add_row(player_name, 
                            str(total_points[player_name]), 
                            str(games_won[player_name]),
                            str(top_5_finishes[player_name]),
                            str(games_played[player_name]),
                            style=player_color)
                

            console.clear()
            console.print(table)
            time.sleep(1)  # Pause for a short time before next update

    # Final results
    results = [f"{number} games were played in {round(time.time() - start_time, 2)} seconds"]
    for player_name in sorted(total_points, key=total_points.get, reverse=True):
        results.append(f"{player_name} earned a total of {total_points[player_name]} points")

    

    if folder_name == "classes":
        with open(filename, 'w') as file:
            g_res = {"banked_money":total_points}
            scores = assign_points(g_res, max_score=21)
            for player_name in sorted(scores, key=scores.get, reverse=True):
                file.write(f"{player_name} earned a total of {scores[player_name]*20} points\n")
            file.write("\n")
            file.write("----------------------------")
            file.write("\n".join(results))
        return "\n".join(results)
    else:
        return total_points


def assign_points(game_result, max_score=6):
    banked_money = game_result['banked_money']
    
    sorted_scores = sorted(banked_money.items(), key=lambda x: x[1], reverse=True)
    points_distribution = {}
    last_score = None
    last_rank = 0

    for rank, (player, score) in enumerate(sorted_scores, start=1):
        if score != last_score:  # New score, update rank
            last_rank = rank
        last_score = score

        # Assign points based on rank
        points = max(max_score - last_rank, 0)
        points_distribution[player] = points
  
    return points_distribution


def get_all_player_classes_from_folder(folder_name="classes"):
    # Get a list of all .py files in the given folder
    #check if a folder called classes exists otherwise use the present working directory
    if not os.path.exists(folder_name):
        folder_name = os.getcwd()

    files = [f for f in os.listdir(folder_name) if os.path.isfile(os.path.join(folder_name, f)) and f.endswith('.py')]

    player_classes = []

    for file in files:
        module_name = file[:-3]  # remove the ".py" extension
        spec = importlib.util.spec_from_file_location(module_name, os.path.join(folder_name, file))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check each item in the module to see if it's a subclass of Player
        for name, obj in vars(module).items():
            if isinstance(obj, type) and issubclass(obj, Player) and obj is not Player:
                player_classes.append((obj, file))
    return player_classes



if __name__ == "__main__":
    print(run_simulation_with_animation(10000, verbose=False))