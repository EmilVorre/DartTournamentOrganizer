from stats import Stats

class Player:
    def __init__(self, name, app):
        self.name = name
        self.losses = 0
        self.wins = 0
        self.times_sat_out = 0
        self.internal_times_sat_out = 0
        self.app = app
        self.stats = Stats()


    def add_loss(self):
        self.stats.add_loss()
        self.losses += 1
        if self.losses >= self.app.max_losses:
            self.eliminate()

    def add_win(self):
        self.stats.add_win()
        self.wins += 1

    def sit_out(self):
        self.stats.sit_out()
        self.times_sat_out += 1
        self.internal_times_sat_out -= 1

    def reset_stats(self):
        self.stats.reset()

    def eliminate(self):
        self.stats.eliminate_player()
        print(f"{self.name} has been eliminated.")
        self.app.eliminated_players.append(self)
        self.app.players.remove(self)
        self.app.update_eliminated_table()
        self.app.update_player_table()
        self.app.check_tournament_end()

