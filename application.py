from PyQt6.QtWidgets import (
    QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QWidget, QDialog, QGridLayout, QLineEdit, QSpinBox, QFormLayout, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt
import random

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
        # Move player to eliminated players list
        self.app.eliminated_players.append(self)
        self.app.players.remove(self)
        self.app.update_eliminated_table()
        self.app.update_player_table()
        self.app.check_tournament_end()

class PlayerItemWidget(QWidget):
    def __init__(self, player_name, remove_callback):
        super().__init__()
        self.player_name = player_name
        self.remove_callback = remove_callback
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        self.label = QLabel(self.player_name)
        self.remove_button = QPushButton("✖")
        self.remove_button.setFixedSize(20, 20)
        self.remove_button.clicked.connect(self.remove_player)
        layout.addWidget(self.label)
        layout.addWidget(self.remove_button)
        self.setLayout(layout)

    def remove_player(self):
        self.remove_callback(self.player_name)

class StartPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Start Page")
        layout = QVBoxLayout()

        # Form layout for player names and max losses
        form_layout = QFormLayout()
        self.player_name_input = QLineEdit()
        self.player_name_input.returnPressed.connect(self.add_player)  # Connect Enter key to add_player
        self.max_losses = QSpinBox()
        self.max_losses.setMinimum(1)
        self.max_losses.setValue(3)
        form_layout.addRow("Player Name:", self.player_name_input)
        form_layout.addRow("Max Losses Before Elimination:", self.max_losses)
        layout.addLayout(form_layout)

        # List widget to display player names
        self.player_list = QListWidget()
        layout.addWidget(self.player_list)

        # Button to add player name to the list
        add_player_button = QPushButton("Add Player")
        add_player_button.clicked.connect(self.add_player)
        layout.addWidget(add_player_button)

        # Button to start the tournament
        start_button = QPushButton("Start Tournament")
        start_button.clicked.connect(self.start_tournament)
        layout.addWidget(start_button)

        # Button to add 17 players for testing
        test_button = QPushButton("Add 17 Players for Testing")
        test_button.clicked.connect(self.add_test_players)
        layout.addWidget(test_button)

        self.setLayout(layout)

    def add_player(self):
        player_name = self.player_name_input.text().strip()
        if player_name:
            # Check if the player name is already in the list
            for i in range(self.player_list.count()):
                item = self.player_list.item(i)
                widget = self.player_list.itemWidget(item)
                if widget.player_name == player_name:
                    QMessageBox.warning(self, "Duplicate Player", f"The player '{player_name}' is already in the list.")
                    return
            item = QListWidgetItem()
            player_widget = PlayerItemWidget(player_name, self.remove_player)
            item.setSizeHint(player_widget.sizeHint())
            self.player_list.addItem(item)
            self.player_list.setItemWidget(item, player_widget)
            self.player_name_input.clear()

    def remove_player(self, player_name):
        for i in range(self.player_list.count()):
            item = self.player_list.item(i)
            widget = self.player_list.itemWidget(item)
            if widget.player_name == player_name:
                self.player_list.takeItem(i)
                break

    def start_tournament(self):
        player_names = [self.player_list.itemWidget(self.player_list.item(i)).player_name for i in range(self.player_list.count())]
        max_losses = self.max_losses.value()
        players = [Player(name, None) for name in player_names]
        self.switch_to_matchmaking(players, max_losses)

    def add_test_players(self):
        max_losses = self.max_losses.value()
        players = [Player(f"Player{i + 1}", None) for i in range(17)]
        self.switch_to_matchmaking(players, max_losses)

    def switch_to_matchmaking(self, players, max_losses):
        self.matchmaking_app = MatchmakingApp(players, max_losses)
        for player in self.matchmaking_app.players:
            player.app = self.matchmaking_app
        self.matchmaking_app.show()
        self.close()

class MatchmakingApp(QWidget):
    def __init__(self, players, max_losses):
        super().__init__()
        self.players = players
        self.max_losses = max_losses
        self.matches = []
        self.unused_players = []
        self.eliminated_players = []
        self.last_eliminated_players = []
        self.match_results = {}
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Matchmaking Frontend")
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        self.update_ui()

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clear_layout(child.layout())

    def update_ui(self):
        self.clear_layout(self.main_layout)
        if len(self.players) <= 8:
            self.show_final_bracket()
        else:
            self.show_matchmaking_ui()

    def show_matchmaking_ui(self):
        # Player Tables Layout
        player_tables_layout = QVBoxLayout()

        # Player Table
        self.player_table = QTableWidget(len(self.players), 4)
        self.player_table.setHorizontalHeaderLabels(["Player Name", "Losses", "Wins", "Times Sat Out"])
        self.player_table.setColumnWidth(0, 150)  # Adjust column width for Player Name
        self.player_table.setColumnWidth(1, 50)   # Adjust column width for Losses
        self.player_table.setColumnWidth(2, 50)   # Adjust column width for Wins
        self.player_table.setColumnWidth(3, 100)  # Adjust column width for Times Sat Out
        self.update_player_table()
        player_tables_layout.addWidget(self.player_table)

        # Eliminate Players Table
        self.eliminated_table = QTableWidget(0, 1)
        self.eliminated_table.setHorizontalHeaderLabels(["Eliminated Players"])
        self.eliminated_table.setColumnWidth(0, 150)  # Adjust column width for Eliminated Players
        player_tables_layout.addWidget(self.eliminated_table)

        self.main_layout.addLayout(player_tables_layout)

        # Matches and Players that Sit Out Layout
        matches_unused_layout = QVBoxLayout()

        # Matches Table
        self.match_table = QTableWidget(0, 2)
        self.match_table.setHorizontalHeaderLabels(["Team 1", "Team 2"])
        self.match_table.setColumnWidth(0, 200)  # Adjust column width for Team 1
        self.match_table.setColumnWidth(1, 200)  # Adjust column width for Team 2
        self.match_table.cellClicked.connect(self.handle_cell_click)
        matches_unused_layout.addWidget(self.match_table)

        # Players that Sit Out Table
        self.unused_table = QTableWidget(0, 1)
        self.unused_table.setHorizontalHeaderLabels(["Players that Sit Out"])
        self.unused_table.setColumnWidth(0, 150)  # Adjust column width for Players that Sit Out
        matches_unused_layout.addWidget(self.unused_table)

        self.main_layout.addLayout(matches_unused_layout)

        # Status Label
        self.status_label = QLabel("Status: Waiting for matches to be generated.")
        self.main_layout.addWidget(self.status_label)

        # Buttons Layout
        buttons_layout = QVBoxLayout()

        # Generate Matches Button
        self.generate_matches_button = QPushButton("Generate Matches")
        self.generate_matches_button.clicked.connect(self.generate_random_matches)
        buttons_layout.addWidget(self.generate_matches_button)

        # Submit Results Button
        self.submit_results_button = QPushButton("Submit Results")
        self.submit_results_button.setEnabled(False)
        self.submit_results_button.clicked.connect(self.handle_match_results)
        buttons_layout.addWidget(self.submit_results_button)

        self.main_layout.addLayout(buttons_layout)

    def show_final_bracket(self):
        final_layout = QVBoxLayout()

        # Remaining Players Table
        remaining_players_table = QTableWidget(len(self.players), 1)
        remaining_players_table.setHorizontalHeaderLabels(["Remaining Players"])
        remaining_players_table.setColumnWidth(0, 150)  # Adjust column width for Remaining Players
        for row, player in enumerate(self.players):
            remaining_players_table.setItem(row, 0, QTableWidgetItem(player.name))
        final_layout.addWidget(remaining_players_table)

        if len(self.players) < 8:
            # Last Eliminated Players Table
            last_eliminated_table = QTableWidget(len(self.last_eliminated_players), 1)
            last_eliminated_table.setHorizontalHeaderLabels(["Last Eliminated Players"])
            last_eliminated_table.setColumnWidth(0, 150)  # Adjust column width for Last Eliminated Players
            for row, player in enumerate(self.last_eliminated_players):
                last_eliminated_table.setItem(row, 0, QTableWidgetItem(player.name))
            final_layout.addWidget(last_eliminated_table)

            # Add a button to start the extra game
            start_extra_game_button = QPushButton("Start Extra Game")
            start_extra_game_button.clicked.connect(self.handle_extra_game)
            final_layout.addWidget(start_extra_game_button)

        self.main_layout.addLayout(final_layout)

    def update_player_table(self):
        self.player_table.setRowCount(len(self.players))
        for row, player in enumerate(self.players):
            self.player_table.setItem(row, 0, QTableWidgetItem(player.name))
            self.player_table.setItem(row, 1, QTableWidgetItem(str(player.losses)))
            self.player_table.setItem(row, 2, QTableWidgetItem(str(player.wins)))
            self.player_table.setItem(row, 3, QTableWidgetItem(str(player.times_sat_out)))

    def update_eliminated_table(self):
        self.eliminated_table.setRowCount(len(self.eliminated_players))
        for row, player in enumerate(self.eliminated_players):
            self.eliminated_table.setItem(row, 0, QTableWidgetItem(player.name))

    def generate_random_matches(self):
        """Generate random 2v2 matches."""
        # Clear previous match results and last eliminated players
        self.match_results.clear()
        self.last_eliminated_players.clear()

        available_players = [player for player in self.players if player not in self.eliminated_players]
        # Sort players by unused count (ascending) and then shuffle to randomize within the same unused count
        available_players.sort(key=lambda player: (player.unused_count, random.random()))
        self.matches = []
        self.unused_players = []

        # Split players into teams of 4, leaving the rest as unused
        for i in range(0, len(available_players), 4):
            group = available_players[i:i + 4]
            if len(group) == 4:
                self.matches.append((group[:2], group[2:]))
            else:
                self.unused_players.extend(group)

        # Increment unused count for players who are unused
        for player in self.unused_players:
            player.unused_count += 1
            player.sit_out()

        # Update the matches table
        self.match_table.setRowCount(len(self.matches))
        for row, (team_1, team_2) in enumerate(self.matches):
            team_1_names = ", ".join(player.name for player in team_1)
            team_2_names = ", ".join(player.name for player in team_2)
            self.match_table.setItem(row, 0, QTableWidgetItem(team_1_names))
            self.match_table.setItem(row, 1, QTableWidgetItem(team_2_names))

        # Update the players that sit out table
        self.unused_table.setRowCount(len(self.unused_players))
        for row, player in enumerate(self.unused_players):
            self.unused_table.setItem(row, 0, QTableWidgetItem(player.name))

        self.submit_results_button.setEnabled(True)
        self.status_label.setText("Status: Matches generated. Enter results.")

    def handle_cell_click(self, row, column):
        if column == 0:
            self.set_match_result(row, 1)
        elif column == 1:
            self.set_match_result(row, 2)

    def set_match_result(self, row, result):
        self.match_results[row] = result
        for col in range(2):
            item = self.match_table.item(row, col)
            if col == result - 1:
                item.setBackground(Qt.GlobalColor.green)
            else:
                item.setBackground(Qt.GlobalColor.red)

    def handle_match_results(self):
        """Handle submission of match results."""
        all_results_entered = True
        for row in range(self.match_table.rowCount()):
            if row not in self.match_results:
                all_results_entered = False
                break

        if not all_results_entered:
            self.status_label.setText("Status: Enter all results before submitting!")
            return

        # Track the players eliminated in this round
        self.last_eliminated_players = []

        # Process results
        for row, (team_1, team_2) in enumerate(self.matches):
            result = self.match_results.get(row)
            if result == 1:
                for player in team_2:
                    player.add_loss()
                    if player.losses >= self.max_losses:
                        self.last_eliminated_players.append(player)
                for player in team_1:
                    player.add_win()
            elif result == 2:
                for player in team_1:
                    player.add_loss()
                    if player.losses >= self.max_losses:
                        self.last_eliminated_players.append(player)
                for player in team_2:
                    player.add_win()

        # Update tables and reset match table
        self.update_player_table()
        self.update_eliminated_table()
        self.match_table.setRowCount(0)
        self.unused_table.setRowCount(0)
        self.submit_results_button.setEnabled(False)
        self.status_label.setText("Status: Results submitted successfully!")

        # Check if the tournament should end
        self.check_tournament_end()

    def check_tournament_end(self):
        """Check if the tournament should end and handle the extra game if needed."""
        if len(self.players) <= 8:
            self.update_ui()

    def handle_extra_game(self):
        """Handle the extra game to fill the remaining spots."""
        extra_game_dialog = ExtraGameDialog(self.last_eliminated_players, self)
        extra_game_dialog.exec()
        self.update_ui()

    def end_tournament(self):
        """End the tournament and display the final players."""
        final_dialog = FinalDialog(self.players)
        final_dialog.exec()

class ExtraGameDialog(QDialog):
    def __init__(self, players, parent=None):
        super().__init__(parent)
        self.players = players
        self.remaining_spots = 8 - len(parent.players)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Extra Game")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.next_match()

    def next_match(self):
        if len(self.players) <= self.remaining_spots:
            self.parent().players.extend(self.players)
            self.parent().update_player_table()
            self.accept()
            return

        if len(self.players) < 2:
            self.accept()
            return

        player1 = self.players.pop()
        player2 = self.players.pop()
        match_label = QLabel(f"{player1.name} vs {player2.name}")
        self.layout.addWidget(match_label)

        button1 = QPushButton(f"{player1.name} Wins")
        button1.clicked.connect(lambda: self.match_result(player1, player2))
        self.layout.addWidget(button1)

        button2 = QPushButton(f"{player2.name} Wins")
        button2.clicked.connect(lambda: self.match_result(player2, player1))
        self.layout.addWidget(button2)

    def match_result(self, winner, loser):
        self.players.append(winner)
        self.next_match()

class FinalDialog(QDialog):
    def __init__(self, players, parent=None):
        super().__init__(parent)
        self.players = players
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Final Players")
        layout = QVBoxLayout()

        # Display the final players
        player_table = QTableWidget(len(self.players), 1)
        player_table.setHorizontalHeaderLabels(["Player Name"])
        player_table.setColumnWidth(0, 150)  # Adjust column width for Player Name
        for row, player in enumerate(self.players):
            player_table.setItem(row, 0, QTableWidgetItem(player.name))
        layout.addWidget(player_table)

        self.setLayout(layout)

# Sample Players
players = [Player(f"Player{i + 1}", None) for i in range(17)]  # 17 players for demonstration

# Start Application
app = QApplication([])
start_page = StartPage()
start_page.show()
app.exec()