class Player:
    def __init__(self, name, app):
        self.name = name
        self.losses = 0
        self.wins = 0
        self.times_sat_out = 0
        self.internal_times_sat_out = 0
        self.app = app

    def add_loss(self):
        self.losses += 1
        if self.losses >= self.app.max_losses:
            self.eliminate()

    def add_win(self):
        self.wins += 1

    def sit_out(self):
        self.times_sat_out += 1
        self.internal_times_sat_out -= 1

    def eliminate(self):
        print(f"{self.name} has been eliminated.")
        self.app.eliminated_players.append(self)
        self.app.players.remove(self)
        self.app.update_eliminated_table()
        self.app.update_player_table()
        self.app.check_tournament_end()
