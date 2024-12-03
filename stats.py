class Stats:
    def __init__(self):
        self.losses = 0
        self.wins = 0
        self.times_sat_out = 0
        eliminated_status = False

    def add_loss(self):
        self.losses += 1

    def add_win(self):
        self.wins += 1
    
    def sit_out(self):
        self.times_sat_out += 1

    def eliminate_player(self):
        self.eliminated_status = True
    
    def reset(self):
        self.losses = 0
        self.wins = 0
        self.times_sat_out = 0
