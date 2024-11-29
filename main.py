import random

class Player:
    def __init__(self, name):
        self.name = name
        self.losses = 0
        self.status = "active"  # "active" or "eliminated"

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Player(name={self.name}, losses={self.losses}, status={self.status})"

class Matchmaker:
    def __init__(self, players, loss_limit=3):
        self.players = players
        self.loss_limit = loss_limit
        self.eliminated_players = []
        self.round_number = 1

    def form_teams(self):
        active_players = [p for p in self.players if p.status == "active"]
        random.shuffle(active_players)
        teams = []
        while len(active_players) >= 4:
            team1 = [active_players.pop(), active_players.pop()]
            team2 = [active_players.pop(), active_players.pop()]
            teams.append((team1, team2))
        return teams

    def simulate_match(self, team1, team2):
        # Simulate a random outcome
        winner = random.choice([team1, team2])
        loser = team1 if winner == team2 else team2
        print(f"Match: {team1} vs {team2}")
        print(f"Winner: {winner}\n")
        for player in loser:
            player.losses += 1
            if player.losses >= self.loss_limit:
                player.status = "eliminated"
                self.eliminated_players.append(player)
                print(f"{player} has been eliminated!\n")
        return winner

    def run(self):
        print("Starting Matchmaking...\n")
        while len([p for p in self.players if p.status == "active"]) > 8:
            print(f"--- Round {self.round_number} ---\n")
            teams = self.form_teams()
            for team1, team2 in teams:
                self.simulate_match(team1, team2)
            self.round_number += 1
        self.revive_players_if_needed()

        print("Matchmaking Complete!")
        print("Remaining Players:")
        for player in self.players:
            if player.status == "active":
                print(player)

    def revive_players_if_needed(self):
        active_count = len([p for p in self.players if p.status == "active"])
        while active_count < 8 and self.eliminated_players:
            revived_player = self.eliminated_players.pop()
            revived_player.status = "active"
            revived_player.losses = self.loss_limit - 1
            print(f"{revived_player} has been revived!")
            active_count += 1

# Example Usage
players = [Player(f"Player {i+1}") for i in range(16)]
matchmaker = Matchmaker(players, loss_limit=3)
matchmaker.run()
