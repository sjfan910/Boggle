import json
import sqlite3
from PyQt5.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QFrame, QMessageBox)
from PyQt5.QtCore import Qt
from modules.gameDetailWindow import format_timestamp
from css.gameHistoryWindowcss import *

"""
GameHistoryWindow displays a scrollable list of all previously played games.
Each game is shown as a clickable block with summary information.

Key Features:
- Loads summary game data from data/game_history.db (SQLite)
- Displays games in reverse chronological order (most recent first)
- Each game block shows: completion %, timestamp, game settings
- Click any block to view detailed breakdown (word lists loaded from JSON)
- Delete button on each block to remove individual games
- Back button returns to main menu

Note: SQLite stores summary columns only (score, grid_size, time_played, ai_helper_uses, difficulty, timer, timestamp). Full word list data for GameDetailWindow is still read from data/game_history.json.
"""


class GameBlock(QFrame):
    def __init__(self, game_data, row_id, parent_window):
        """
        Parameters:
            game_data - dict with keys: score, grid_size, time_played,
                        ai_helper_uses, difficulty, timer, timestamp
            row_id    - SQLite rowid for this record (used for deletion)
        """
        super().__init__()
        self.game_data = game_data
        self.row_id = row_id
        self.parent_window = parent_window
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(2)
        self.setCursor(Qt.PointingHandCursor)
        self.__initUI()

    def __initUI(self):
        self.setFixedHeight(100)
        self.setStyleSheet(gameBlockStyle)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setAlignment(Qt.AlignVCenter)

        score = self.game_data['score']
        completion_badge = QLabel(f"Score\n{score}")
        completion_badge.setFixedSize(80, 60)
        completion_badge.setAlignment(Qt.AlignCenter)
        completion_badge.setStyleSheet(completionBadgeStyle)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)

        formatted_time = format_timestamp(self.game_data['timestamp'])
        timestamp_label = QLabel(formatted_time)
        timestamp_label.setStyleSheet(timestampLabelStyle)

        grid_size = self.game_data['grid_size']
        difficulty = self.game_data['difficulty']
        timer = self.game_data['timer']

        if not timer:
            time_played = self.game_data['time_played']
            minutes = time_played // 60
            seconds = time_played % 60
            timer = f"{minutes}:{seconds:02d} played"
        else:
            timer = int(timer)
            minutes = timer // 60
            seconds = timer % 60
            timer = f"{minutes}:{seconds:02d}"

        settings_text = f"{grid_size}x{grid_size} Grid, {difficulty} mode, {timer}"
        settings_label = QLabel(settings_text)
        settings_label.setStyleSheet(settingsLabelStyle)

        info_layout.addStretch()
        info_layout.addWidget(timestamp_label)
        info_layout.addWidget(settings_label)
        info_layout.addStretch()

        delete_btn = QPushButton('Delete\nGame')
        delete_btn.setFixedSize(80, 60)
        delete_btn.setStyleSheet(deleteButtonStyle)
        delete_btn.clicked.connect(self.delete_game)

        main_layout.addWidget(completion_badge, 0, Qt.AlignVCenter)
        main_layout.addLayout(info_layout, 1)
        main_layout.addWidget(delete_btn, 0, Qt.AlignVCenter)

        self.setLayout(main_layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent_window.open_game_detail(self.row_id)

    def delete_game(self):
        self.parent_window.delete_game_at_row_id(self.row_id)


class GameHistoryWindow(QWidget):
    def __init__(self, main_menu=None):
        super().__init__()
        self.main_menu = main_menu
        self.game_history = []  # list of dicts from SQL
        self.__load_history()
        self.__initUI()

    def __load_history(self):
        """Load summary rows from SQLite in reverse chronological order."""
        try:
            con = sqlite3.connect('data/game_history.db')
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS gameHistory(
                    score, grid_size, time_played, ai_helper_uses,
                    difficulty, timer, timestamp
                )
            """)
            rows = cur.execute(
                "SELECT rowid, * FROM gameHistory ORDER BY rowid DESC"
            ).fetchall()
            con.close()
            self.game_history = [dict(row) for row in rows]
        except Exception as e:
            self.game_history = []

    def __initUI(self):
        self.setWindowTitle('Game History')
        self.setFixedSize(900, 700)
        self.setStyleSheet("background-color: #f0f0f0;")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 20, 30, 20)
        header_layout = QHBoxLayout()

        title = QLabel('Game History')
        title.setStyleSheet(titleStyle)

        back_btn = QPushButton('Back')
        back_btn.setFixedSize(120, 40)
        back_btn.setStyleSheet(backButtonStyle)
        back_btn.clicked.connect(self.back_to_menu)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(back_btn)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(scrollAreaStyle)

        scroll_content = QWidget()
        self.games_layout = QVBoxLayout()
        self.games_layout.setSpacing(15)

        self.__populate_games_layout()

        self.games_layout.addStretch()
        scroll_content.setLayout(self.games_layout)
        scroll.setWidget(scroll_content)
        main_layout.addLayout(header_layout)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def __populate_games_layout(self):
        if not self.game_history:
            empty_label = QLabel('No games played yet.\nStart playing to build your history')
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet(emptyLabelStyle)
            self.games_layout.addWidget(empty_label)
        else:
            for game_data in self.game_history:
                game_block = GameBlock(game_data, game_data['rowid'], self)
                self.games_layout.addWidget(game_block)

    def delete_game_at_row_id(self, row_id):
        try:
            con = sqlite3.connect('data/game_history.db')
            cur = con.cursor()
            cur.execute("DELETE FROM gameHistory WHERE rowid = ?", (row_id,))
            con.commit()
            con.close()
            self.__load_history()
            self.__refresh_display()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to delete game: {e}")

    def __refresh_display(self):
        while self.games_layout.count():
            child = self.games_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.__populate_games_layout()
        self.games_layout.addStretch()

    def open_game_detail(self, row_id):
        """
        Word lists (found_words, all_possible_words) are not stored in SQL.
        We match by rowID position into the JSON file to retrieve full data.
        """
        from modules.gameDetailWindow import GameDetailWindow
        try:
            with open('data/game_history.json', 'r') as f:
                all_games = json.load(f)
            sql_row = None
            for game in self.game_history:
                if game['rowid'] == row_id:
                    sql_row = game
                    break
            game_data = None
            for game in all_games:
                if game.get('timestamp') == sql_row['timestamp']:
                    game_data = game
                    break

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load game detail: {e}")
            return
        
        self.hide()
        self.detail_window = GameDetailWindow(game_data, self)
        self.detail_window.show()

    def back_to_menu(self):
        if self.main_menu:
            self.hide()
            self.main_menu.show()
        else:
            self.close()