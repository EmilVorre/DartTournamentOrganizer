from PyQt6.QtWidgets import (
    QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
    QPushButton, QDialogButtonBox, QLabel, QWidget, QDialog, QGridLayout, QLineEdit, QSpinBox, QFormLayout, QListWidget, QListWidgetItem, QMessageBox, QCheckBox
)
from PyQt6.QtGui import QPainter, QPixmap
from PyQt6.QtCore import (Qt, QTimer)
import random
from player import Player  # Import the Player class
from stats import Stats  # Import the Match class
from stylesheet import stylesheet  # Import the stylesheet

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

    # sorto players alfabetically
    def __lt__(self, other):
        return self.player_name < other.player_name

class StartPage(QWidget):
    def __init__(self, player_names=None):
        super().__init__()
        self.player_names = player_names if player_names else []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Start Page")
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        #  Form layout for player names and max losses
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

        # Button to add player namem to the list
        add_player_button = QPushButton("Add Player")
        add_player_button.clicked.connect(self.add_player)
        layout.addWidget(add_player_button)

        # Button to start the tournament
        start_button = QPushButton("Start Tournament")
        start_button.clicked.connect(self.start_tournament)
        layout.addWidget(start_button)

        # Button to add 35 players for testing
        test_button = QPushButton("Add 35 Players for Testing")
        test_button.clicked.connect(self.add_test_players)
        layout.addWidget(test_button)

        self.setLayout(layout)

        # Pre-enter player names if provided
        for name in self.player_names:
            self.add_player(name)

    def add_player(self, player_name=None):
        if player_name is None:
            player_namea = self.player_name_input.text().strip()
        if player_name:
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
        players = [Player(f"Player{i + 1}", None) for i in range(47)]
        self.switch_to_matchmaking(players, max_losses)

    def switch_to_matchmaking(self, players, max_losses):
        self.matchmaking_app = Application(players, max_losses)
        for player in self.matchmaking_app.players:
            player.app = self.matchmaking_app
        self.matchmaking_app.show()
        self.close()

class Application(QWidget):
    def __init__(self, players, max_losses):
        super().__init__()
        self.players = players
        self.max_losses = max_losses
        self.matches = []
        self.unused_players = []
        self.eliminated_players = []
        self.last_eliminated_players = []
        self.match_results = {}
        self.final_match_results = {}
        
        # Initialize scrolling variables
        self.scroll_timer = QTimer(self)
        self.scroll_timer.timeout.connect(self.scroll_player_table)
        self.scroll_position = 0
        self.scroll_delay_counter = 0

        self.init_ui()
        self.start_scrolling()

    def init_ui(self):
        self.setWindowTitle("Dart Tournament")
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        self.status_label = QLabel("Status: Waiting for matches to be generated.")
        self.main_layout.addWidget(self.status_label)
        self.update_ui()

    def start_scrolling(self):
        """Start the scrolling timer for the player table."""
        self.scroll_timer.start(100)  # Decrease the interval (in ms) for smoother scrolling

    def scroll_player_table(self):
        """Automatically scroll the player table with infinite looping."""
        if hasattr(self, 'player_table'):  # Ensure the table exists
            # Increment scroll position by a smaller step for smoother scrolling
            self.scroll_position += 0.1  # Use a fractional step for smoother scrolling

            # Check if we've reached the end
            if self.scroll_position > self.player_table.verticalScrollBar().maximum():
                self.scroll_delay_counter += 1
                if self.scroll_delay_counter > 50:  # Adjust this value for the delay
                    self.scroll_position = 0  # Reset to the top for infinite scrolling
                    self.scroll_delay_counter = 0

            # Set the new scroll position
            self.player_table.verticalScrollBar().setValue(int(self.scroll_position))

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
            self.show_final_players()
        else:
            self.show_matchmaking_ui()

    def show_matchmaking_ui(self):
        # Player Tables Layout (Left Side)
        player_tables_layout = QVBoxLayout()
        player_tables_layout.setContentsMargins(0, 0, 0, 0)
        player_tables_layout.setSpacing(0)

        # Player Table
        self.player_table = QTableWidget(len(self.players), 4)
        self.player_table.setHorizontalHeaderLabels(["Player Name", "Losses", "Wins", "Times Sat Out"])
        self.player_table.setColumnWidth(0, 200)  # Adjust column width for Player Name
        self.player_table.setColumnWidth(1, 80)   # Adjust column width for Losses
        self.player_table.setColumnWidth(2, 80)   # Adjust column width for Wins
        self.player_table.setColumnWidth(3, 140)  # Adjust column width for Times Sat Out
        self.update_player_table()
        player_tables_layout.addWidget(self.player_table)

        self.main_layout.addLayout(player_tables_layout, stretch=1)

        # Matches and Other Tables Layout (Right Side)
        right_side_layout = QVBoxLayout()
        right_side_layout.setContentsMargins(0, 0, 0, 0)
        right_side_layout.setSpacing(0)

        # Matches Table
        self.match_table = QTableWidget(0, 2)
        self.match_table.setHorizontalHeaderLabels(["Team 1", "Team 2"])
        self.match_table.setColumnWidth(0, 300)  # Adjust column width for Team 1
        self.match_table.setColumnWidth(1, 300)  # Adjust column width for Team 2
        self.match_table.cellClicked.connect(self.handle_cell_click)
        right_side_layout.addWidget(self.match_table, stretch=2)

        # Players that Sit Out Table
        self.unused_table = QTableWidget(0, 1)
        self.unused_table.setHorizontalHeaderLabels(["Players that Sit Out"])
        self.unused_table.setColumnWidth(0, 200)  # Adjust column width for Players that Sit Out
        right_side_layout.addWidget(self.unused_table, stretch=1)

        # Eliminated Players Table
        self.eliminated_table = QTableWidget(0, 1)
        self.eliminated_table.setHorizontalHeaderLabels(["Eliminated Players"])
        self.eliminated_table.setColumnWidth(0, 200)  # Adjust column width for Eliminated Players
        right_side_layout.addWidget(self.eliminated_table, stretch=3)

        self.main_layout.addLayout(right_side_layout, stretch=2)

        # Buttons Layout
        buttons_layout = QVBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(0)

        # Generate Matches Button
        self.generate_matches_button = QPushButton("Generate Matches")
        self.generate_matches_button.clicked.connect(self.generate_random_matches)
        buttons_layout.addWidget(self.generate_matches_button)

        # Submit Results Button
        self.submit_results_button = QPushButton("Submit Results")
        self.submit_results_button.setEnabled(False)
        self.submit_results_button.clicked.connect(self.handle_match_results)
        buttons_layout.addWidget(self.submit_results_button)

        # Edit Losses Button
        edit_losses_button = QPushButton("Edit Losses")
        edit_losses_button.clicked.connect(self.edit_losses_for_players)
        buttons_layout.addWidget(edit_losses_button)

        # Eliminate Player Button
        eliminate_player_button = QPushButton("Eliminate Player")
        eliminate_player_button.clicked.connect(self.eliminate_a_selected_player)
        buttons_layout.addWidget(eliminate_player_button)

        # Restart Tournament Button
        reset_tournament_button = QPushButton("Restart Tournament")
        reset_tournament_button.clicked.connect(self.restart_tournament)
        buttons_layout.addWidget(reset_tournament_button)

        # End Tournament Button
        end_tournament_button = QPushButton("End Tournament")
        end_tournament_button.clicked.connect(self.reset_tournament)
        buttons_layout.addWidget(end_tournament_button)

        self.main_layout.addLayout(buttons_layout)

    def show_final_players(self):
        final_layout = QVBoxLayout()
        final_layout.setContentsMargins(0, 0, 0, 0)
        final_layout.setSpacing(0)
        # Add widgets to final_layout as needed
        
        # Remaining Players Table
        remaining_players_table = QTableWidget(len(self.players), 1)
        remaining_players_table.setHorizontalHeaderLabels(["Remaining Players"])
        remaining_players_table.setColumnWidth(0, 200)  # Adjust column width for Remaining Players
        for row, player in enumerate(self.players):
            remaining_players_table.setItem(row, 0, QTableWidgetItem(player.name))
        final_layout.addWidget(remaining_players_table)

        if len(self.players) < 8:
            # Last Eliminated Players Table
            last_eliminated_table = QTableWidget(len(self.last_eliminated_players), 1)
            last_eliminated_table.setHorizontalHeaderLabels(["Last Eliminated Players"])
            last_eliminated_table.setColumnWidth(0, 220)  # Adjust column width for Last Eliminated Players
            for row, player in enumerate(self.last_eliminated_players):
                last_eliminated_table.setItem(row, 0, QTableWidgetItem(player.name))
            final_layout.addWidget(last_eliminated_table)

            # Add a button to start the extra game
            start_extra_game_button = QPushButton("Start Extra Game")
            start_extra_game_button.clicked.connect(self.handle_missing_players)
            final_layout.addWidget(start_extra_game_button)

        if len(self.players) == 8:
            # Add a button to proceed to the final matches
            proceed_button = QPushButton("Proceed to Final Matches")
            proceed_button.clicked.connect(self.seed_last_8_players)
            final_layout.addWidget(proceed_button)

        self.main_layout.addLayout(final_layout)

    def paintEvent(self, event):
        super().paintEvent(event)

        # Create a painter to draw the dartboard
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Load and draw the dartboard image
        dartboard = QPixmap("dartboard.png")  # Path to your dartboard image
        if not dartboard.isNull():
            painter.setOpacity(1.0)  # Make it semi-transparent
            target_rect = self.rect()  # Fill the entire widget
            painter.drawPixmap(target_rect, dartboard)

    def update_player_table(self):
        self.player_table.setRowCount(len(self.players))
        for row, player in enumerate(self.players):
            self.player_table.setItem(row, 0, QTableWidgetItem(player.name))
            self.player_table.setItem(row, 1, QTableWidgetItem(str(player.stats.losses)))
            self.player_table.setItem(row, 2, QTableWidgetItem(str(player.stats.wins)))
            self.player_table.setItem(row, 3, QTableWidgetItem(str(player.stats.times_sat_out)))

    def update_eliminated_table(self):
        self.eliminated_table.setRowCount(len(self.eliminated_players))
        for row, player in enumerate(self.eliminated_players):
            self.eliminated_table.setItem(row, 0, QTableWidgetItem(player.name))

    def set_table_items_transparent(self, table):
        pass  # Remove the transparency setting logic

    def generate_random_matches(self):
        """Generate random 2v2 matches."""
        # Clear previous match results and last eliminated players
        self.match_results.clear()
        self.last_eliminated_players.clear()

        available_players = [player for player in self.players if player not in self.eliminated_players]
        # Sort players by unused count (ascending) and then shuffle to randomize within the same unused count
        available_players.sort(key=lambda player: (player.internal_times_sat_out, random.random()))
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

        self.generate_matches_button.setEnabled(False)
        self.submit_results_button.setEnabled(True)

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
            QMessageBox.warning(self, "Incomplete Results", "Please select a winner for all matches.")
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
        self.generate_matches_button.setEnabled(True)

        # Check if the tournament should end
        self.check_tournament_end()

    def check_tournament_end(self):
        """Check if the tournament should end and handle the extra game if needed."""
        if len(self.players) <= 8:
            self.update_ui()

    def handle_missing_players(self):
        """Handle the extra game to fill the remaining spots."""
        self.clear_layout(self.main_layout)
    
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(QLabel(f"Select {8 - len(self.players)} players from the last eliminated players to fill the spots:"))
    
        self.checkboxes = []
        for player in self.last_eliminated_players:
            checkbox = QCheckBox(player.name)
            self.checkboxes.append((checkbox, player))
            layout.addWidget(checkbox)

        submit_button = QPushButton("Submit Selection")
        # connect the button to the function that added the selected players back to the tournament
        submit_button.clicked.connect(self.add_selected_players)

        layout.addWidget(submit_button)

        self.main_layout.addLayout(layout)

    def add_selected_players(self):
        """Add the selected players back to the tournament."""
        selected_players = [player for checkbox, player in self.checkboxes if checkbox.isChecked()]
        for player in selected_players:
            self.players.append(player)
            self.eliminated_players.remove(player)

        self.update_ui()

    def seed_last_8_players(self):
        """Prepare the final 8 players for the last rounds."""
        # seed the last 8 players randomly
        self.players = random.sample(self.players, 8)
        self.clear_layout(self.main_layout)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(QLabel("The final 8 players have been seeded."))
        seed_button = QPushButton("Proceed to Final Matches")
        seed_button.clicked.connect(self.show_final_matches)
        layout.addWidget(seed_button)
        self.main_layout.addLayout(layout)

    def show_final_matches(self, match_stage=1):
        """Display the final matches for the given stage."""
        # Determine the number of matches based on the number of players
        if len(self.players) == 8:
            num_matches = 2
            stage_name = "Semi-Finals"
        elif len(self.players) == 4:
            num_matches = 1
            stage_name = "Finals"
        elif len(self.players) == 2:
            num_matches = 1
            stage_name = "Grand Finals"
        else:
            num_matches = 0
            stage_name = "Unknown Stage"

        # Clear the layout and display the final matches
        self.clear_layout(self.main_layout)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        label = QLabel(f"Knockout Stage - {stage_name}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # Matches table
        self.final_match_table = QTableWidget(num_matches, 2)
        self.final_match_table.setHorizontalHeaderLabels(["Team 1", "Team 2"])
        self.final_match_table.setColumnWidth(0, 300)
        self.final_match_table.setColumnWidth(1, 300)
        self.final_match_table.cellClicked.connect(self.handle_final_cell_click)

        if len(self.players) == 8:
            for i in range(0, 8, 4):
                team_1 = self.players[i:i+2]
                team_2 = self.players[i+2:i+4]
                self.final_match_table.setItem(i // 4, 0, QTableWidgetItem(", ".join(player.name for player in team_1)))
                self.final_match_table.setItem(i // 4, 1, QTableWidgetItem(", ".join(player.name for player in team_2)))
        elif len(self.players) == 4:
            team_1 = self.players[:2]
            team_2 = self.players[2:]
            self.final_match_table.setItem(0, 0, QTableWidgetItem(", ".join(player.name for player in team_1)))
            self.final_match_table.setItem(0, 1, QTableWidgetItem(", ".join(player.name for player in team_2)))
        elif len(self.players) == 2:
            team_1 = self.players[0]
            team_2 = self.players[1]
            self.final_match_table.setItem(0, 0, QTableWidgetItem(team_1.name))
            self.final_match_table.setItem(0, 1, QTableWidgetItem(team_2.name))

        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)
        table_layout.addWidget(self.final_match_table)
        table_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        layout.addLayout(table_layout)

        # Buttons
        submit_results_button = QPushButton("Submit Final Results")
        submit_results_button.clicked.connect(lambda: self.handle_final_results(match_stage))
        layout.addWidget(submit_results_button)

        self.main_layout.addLayout(layout)

    def handle_final_results(self, match_stage):
        """Handle the results of the final matches."""
        # Check if all matches have a selected winner
        if len(self.final_match_results) != self.final_match_table.rowCount():
            QMessageBox.warning(self, "Incomplete Results", "Please select a winner for all matches.")
            return

        winners = []
        eliminated = []

        for row in range(self.final_match_table.rowCount()):
            result = self.final_match_results.get(row)
            if result == 1:
                team_1 = self.final_match_table.item(row, 0).text().split(", ")
                winners.extend([player for player in self.players if player.name in team_1])
                for player in self.players:
                    if player.name in team_1:
                        player.add_win_stats()
                team_2 = self.final_match_table.item(row, 1).text().split(", ")
                eliminated.extend([player for player in self.players if player.name in team_2])
                for player in self.players:
                    if player.name in team_2:
                        player.add_loss_stats()
            elif result == 2:
                team_2 = self.final_match_table.item(row, 1).text().split(", ")
                winners.extend([player for player in self.players if player.name in team_2])
                for player in self.players:
                    if player.name in team_2:
                        player.add_win_stats()
                team_1 = self.final_match_table.item(row, 0).text().split(", ")
                eliminated.extend([player for player in self.players if player.name in team_1])
                for player in self.players:
                    if player.name in team_1:
                        player.add_loss_stats()

        # Update players and eliminated lists
        self.players = winners
        self.eliminated_players.extend(eliminated)

        if len(self.players) == 2:
            self.end_tournament()
        else:
            self.final_match_results.clear()  # Clear the results for the next stage
            self.show_final_matches(match_stage + 1)

    def set_final_match_result(self, row, result):
        """Set the result of the final match."""
        for col in range(2):
            item = self.final_match_table.item(row, col)
            if col == result - 1:
                item.setBackground(Qt.GlobalColor.green)
            else:
                item.setBackground(Qt.GlobalColor.red)
        self.final_match_results[row] = result

    def handle_final_cell_click(self, row, column):
        """Handle cell click to select the winner of the match."""
        if column == 0:
            self.set_final_match_result(row, 1)
        elif column == 1:
            self.set_final_match_result(row, 2)

    def edit_losses_for_players(self):
        """Edit the losses for selected players."""
        headline = QLabel("Select the players to remove 1 loss from:")
        layout = QVBoxLayout()
        layout.addWidget(headline)

        dialog = PlayerSelectionDialog(self.players)
        dialog.exec()
        selected_players = dialog.get_selected_players()
        for player in self.players:
            if player.name in selected_players:
                player.stats.losses -= 1
                player.losses -= 1
        
        # Update the player table after editing losses
        self.update_player_table()

    def eliminate_a_selected_player(self):
        """Eliminate a selected player from the tournament."""
        headline = QLabel("Select the player to eliminate:")
        layout = QVBoxLayout()
        layout.addWidget(headline)

        dialog = PlayerSelectionDialog(self.players)
        dialog.exec()
        selected_players = dialog.get_selected_players()
        for player in self.players:
            if player.name in selected_players:
                player.eliminate()

        # Update the player table after eliminating a player
        self.update_player_table

    def restart_tournament(self):
        """Restart the tournament with the same players."""
        reply = QMessageBox.question(self, 'End The Tournament', 'Are you sure you want to restart the tournament?', 
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.No:
            return

        player_names = [player.name for player in self.players] + [player.name for player in self.eliminated_players]

        # Clear all player data
        self.players.clear()
        self.eliminated_players.clear()
        self.last_eliminated_players.clear()
        self.matches.clear()
        self.unused_players.clear()
        self.match_results.clear()
        self.final_match_results.clear()

        # Close the current window and show the start page with pre-entered player names
        self.close()
        self.start_page = StartPage(player_names)
        self.start_page.show()

    def reset_tournament(self):
        """Reset the tournament from scratch and delete all player data."""
        reply = QMessageBox.question(self, 'End The Tournament', 'Are you sure you want to end the tournament?', 
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.No:
            return

        # Clear all player data
        self.players.clear()
        self.eliminated_players.clear()
        self.last_eliminated_players.clear()
        self.matches.clear()
        self.unused_players.clear()
        self.match_results.clear()
        self.final_match_results.clear()

        # Close the current window and show the start page
        self.close()
        self.start_page = StartPage()
        self.start_page.show()

    def end_tournament(self):
        """End the tournament and display the winner."""
        self.clear_layout(self.main_layout)
        layout = QVBoxLayout()

        if len(self.players) == 2:
            winner_1 = self.players[0] 
            winner_2 = self.players[1] 
            layout.addWidget(QLabel(f"The tournament winner is: {winner_1.name} And {winner_2.name}"))
        else:
            layout.addWidget(QLabel("The tournament ended with no winner."))

        # Add elimnted players back to the players list
        self.players.extend(self.eliminated_players)

        # Delete array of eliminated players
        self.eliminated_players.clear()

        # Table with the player stats
        player_table = QTableWidget(len(self.players), 4)
        player_table.setHorizontalHeaderLabels(["Player Name", "Losses", "Wins", "Times Sat Out"])
        player_table.setColumnWidth(0, 200)
        player_table.setColumnWidth(1, 80)
        player_table.setColumnWidth(2, 80)
        player_table.setColumnWidth(3, 140)
        for row, player in enumerate(self.players):
            player_table.setItem(row, 0, QTableWidgetItem(player.name))
            player_table.setItem(row, 1, QTableWidgetItem(str(player.stats.losses)))
            player_table.setItem(row, 2, QTableWidgetItem(str(player.stats.wins)))
            player_table.setItem(row, 3, QTableWidgetItem(str(player.stats.times_sat_out)))
        
        layout.addWidget(player_table)


        # Got to many errors with the restart button so I commented it out (Players already in the table)
        restart_button = QPushButton("Restart Tournament")
        restart_button.clicked.connect(self.restart_tournament)
        layout.addWidget(restart_button)

        reset_button = QPushButton("Go Back to Start Page")
        reset_button.clicked.connect(self.reset_tournament)
        layout.addWidget(reset_button)

        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(self.exit_tournament)
        layout.addWidget(exit_button)

        self.main_layout.addLayout(layout)

    def exit_tournament(self):
        """Exit the tournament."""
        QApplication.quit()

class PlayerSelectionDialog(QDialog):
    def __init__(self, players, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Players to Return")
        self.players = players
        self.selected_players = []

        layout = QVBoxLayout()

        self.checkboxes = []
        for player in players:
            checkbox = QCheckBox(player.name)
            self.checkboxes.append(checkbox)
            layout.addWidget(checkbox)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_selected_players(self):
        """Return the selected players from the checkboxes."""
        return [checkbox.text() for checkbox in self.checkboxes if checkbox.isChecked()]


# Start the application
app = QApplication([])
app.setStyleSheet(stylesheet)
start_page = StartPage()
start_page.show()
app.exec()