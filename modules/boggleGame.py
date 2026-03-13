import sys
from math import floor
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QMessageBox, QDialog
from PyQt5.QtCore import Qt, QTimer
from modules.boardGen import BoardGenerator
from modules.validation import WordValidator
from modules.wordFinder import WordFinder
from modules.analyticsWindow import AnalyticsWindow
from modules.aiHelper import AIHelper


class TileButton(QPushButton):
    def __init__(self, letter, row, col):
        super().__init__(letter)
        self.row = row
        self.col = col
        self.is_selected = False
        self.is_ai_highlighted = False
        self.setFixedSize(70, 70)
        self.update_style()

    def update_style(self):
        if self.is_ai_highlighted:
            # AI Helper highlighting (purple/blue)
            self.setStyleSheet("""
                QPushButton {
                    background-color: #9C27B0;
                    color: white;
                    font-size: 36px;
                    font-weight: bold;
                    border: 3px solid #7B1FA2;
                    border-radius: 10px;
                }
            """)
        elif self.is_selected:
            # User selection (green)
            self.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    font-size: 36px;
                    font-weight: bold;
                    border: 3px solid #2E7D32;
                    border-radius: 10px;
                }
            """)
        else:
            # Default state
            self.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: #333;
                    font-size: 36px;
                    font-weight: bold;
                    border: 2px solid #666;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #E8F5E9;
                    border: 3px solid #4CAF50;
                }
            """)

    def set_selected(self, selected):
        self.is_selected = selected
        self.update_style()

    def set_ai_highlighted(self, highlighted):
        self.is_ai_highlighted = highlighted
        self.update_style()

    def flash_color(self, color, border_color):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-size: 36px;
                font-weight: bold;
                border: 3px solid {border_color};
                border-radius: 10px;
            }}
        """)


class EndGameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("End Game?")
        self.setModal(True)
        self.setFixedSize(400, 200)
        layout = QVBoxLayout()
        question = QLabel("End the current game?")
        question.setAlignment(Qt.AlignCenter)
        question.setStyleSheet("font-size: 16px; color: #666; padding: 20px;")
        button_layout = QHBoxLayout()

        no_btn = QPushButton("No, Return")
        no_btn.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 10px;
                border: 2px solid #333;
            }
            QPushButton:hover {
                background-color: #455A64;
            }
        """)
        no_btn.clicked.connect(self.reject)

        yes_btn = QPushButton("Yes, End and Exit")
        yes_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 10px;
                border: 2px solid #333;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        yes_btn.clicked.connect(self.accept)

        button_layout.addWidget(no_btn)
        button_layout.addWidget(yes_btn)
        layout.addWidget(question)
        layout.addLayout(button_layout)
        self.setLayout(layout)


class BoggleGame(QWidget):
    def __init__(self, config, main_window=None):
        super().__init__()
        self.config = config
        self.config_window = None
        self.main_window = main_window

        self.grid_size = int(config['grid_size'][0])
        self.timer_seconds = self.parse_timer(config['timer'])
        self.difficulty = config['difficulty']
        self.ai_helper_enabled = config['ai_helper'] == 'On'

        self.board_letters = []
        self.tiles = []
        self.selected_path = []
        self.current_word = ""
        self.found_words = []
        self.all_possible_words = []
        self.score = 0
        self.is_dragging = False
        self.ai_helper_uses = 0

        self.ai_cooldown_time = 20  # 20 seconds
        self.ai_cooldown_remaining = 0
        self.ai_cooldown_timer = None
        self.ai_highlighted_path = []

        self.board_gen = BoardGenerator(self.grid_size, self.difficulty)
        self.validator = WordValidator()
        self.word_finder = WordFinder()
        self.ai_helper = AIHelper() if self.ai_helper_enabled else None

        self.initUI()
        self.generate_board()
        if self.timer_seconds > 0:
            self.start_timer()

    def parse_timer(self, timer_str):
        if timer_str == "Off":
            return 0
        minutes, seconds = timer_str.split(':')
        return int(minutes) * 60 + int(seconds)

    def initUI(self):
        self.setWindowTitle('Boggle Game')
        self.setGeometry(200, 100, 900, 750)
        self.setStyleSheet("background-color: #f5f5f5;")
        main_layout = QVBoxLayout()
        top_bar = QHBoxLayout()

        self.timer_label = QLabel('Time: --:--')
        self.timer_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #333;
            padding: 10px;
            background-color: white;
            border-radius: 10px;
        """)

        end_game_btn = QPushButton('End Game')
        end_game_btn.setFixedSize(120, 40)
        end_game_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 10px;
                border: 2px solid #333;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        end_game_btn.clicked.connect(self.confirm_end_game)

        top_bar.addWidget(self.timer_label)
        top_bar.addStretch()
        top_bar.addWidget(end_game_btn)

        self.score_label = QLabel('Score: 0')
        self.score_label.setAlignment(Qt.AlignCenter)
        self.score_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #333;
            padding: 10px;
        """)

        self.word_display = QLabel('')
        self.word_display.setAlignment(Qt.AlignCenter)
        self.word_display.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            color: #4CAF50;
            padding: 15px;
            background-color: white;
            border: 3px solid #4CAF50;
            border-radius: 10px;
            min-height: 60px;
        """)

        board_container = QWidget()
        self.board_layout = QGridLayout()
        self.board_layout.setSpacing(25)
        board_container.setLayout(self.board_layout)
        board_container.setMaximumSize(500, 500)

        self.words_label = QLabel('Found Words:')
        self.words_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        self.words_display = QLabel('')
        self.words_display.setStyleSheet("""
            background-color: white;
            border: 2px solid #ddd;
            border-radius: 10px;
            padding: 10px;
            font-size: 14px;
            color: #333;
        """)
        self.words_display.setWordWrap(True)
        self.words_display.setMaximumHeight(100)

        if self.ai_helper_enabled:
            ai_helper_container = QVBoxLayout()
            ai_helper_container.setAlignment(Qt.AlignCenter)

            self.ai_helper_btn = QPushButton('AI Helper')
            self.ai_helper_btn.setFixedSize(180, 50)
            self.ai_helper_btn.setStyleSheet("""
                QPushButton {
                    background-color: #9C27B0;
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                    border-radius: 10px;
                    border: 2px solid #7B1FA2;
                }
                QPushButton:hover {
                    background-color: #7B1FA2;
                }
                QPushButton:disabled {
                    background-color: #BDBDBD;
                    color: #757575;
                    border: 2px solid #9E9E9E;
                }
            """)
            self.ai_helper_btn.clicked.connect(self.use_ai_helper)

            self.ai_cooldown_label = QLabel('')
            self.ai_cooldown_label.setAlignment(Qt.AlignCenter)
            self.ai_cooldown_label.setStyleSheet("""
                font-size: 12px;
                color: #666;
                padding: 5px;
            """)

            ai_helper_container.addWidget(self.ai_helper_btn)
            ai_helper_container.addWidget(self.ai_cooldown_label)

        main_layout.addLayout(top_bar)
        main_layout.addWidget(self.score_label)
        main_layout.addWidget(self.word_display)
        main_layout.addWidget(board_container, alignment=Qt.AlignCenter)
        main_layout.addWidget(self.words_label)
        main_layout.addWidget(self.words_display)

        if self.ai_helper_enabled:
            main_layout.addLayout(ai_helper_container)

        main_layout.addStretch()
        self.setLayout(main_layout)
        self.setMouseTracking(True)

    def generate_board(self):
        self.board_letters = self.board_gen.generate()
        self.all_possible_words = self.word_finder.find_all_words(self.board_letters)

        # Clear existing tiles
        for i in reversed(range(self.board_layout.count())):
            self.board_layout.itemAt(i).widget().setParent(None)

        self.tiles = []
        for row in range(self.grid_size):
            tile_row = []
            for col in range(self.grid_size):
                letter = self.board_letters[row][col]
                tile = TileButton(letter, row, col)
                tile.pressed.connect(lambda r=row, c=col: self.start_selection(r, c))
                tile.clicked.connect(self.clear_ai_highlight)
                self.board_layout.addWidget(tile, row, col)
                tile_row.append(tile)
            self.tiles.append(tile_row)

    def use_ai_helper(self):
        if self.ai_cooldown_remaining > 0:
            return

        self.ai_helper_btn.setEnabled(False)
        self.ai_helper_btn.setText('Searching...')
        QApplication.processEvents()
        word, path = self.ai_helper.suggest_word(
            self.board_letters,
            set(w.upper() for w in self.found_words)
        )
        self.handle_ai_suggestion(word, path)

    def handle_ai_suggestion(self, word, path):
        if word is None:
            QMessageBox.information(self, "No Suggestions", "No valid suggestions found on the board.")
            self.ai_helper_btn.setText('AI Helper')
            self.ai_helper_btn.setEnabled(True)
            return
        self.word_display.setText(f"AI suggests: {word}")
        self.word_display.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #9C27B0;
            padding: 15px;
            background-color: white;
            border: 3px solid #9C27B0;
            border-radius: 10px;
            min-height: 60px;
        """)
        self.animate_ai_path(path)
        self.start_ai_cooldown()

    def animate_ai_path(self, path):
        self.ai_highlighted_path = path
        def highlight_tile(index):
            if index < len(path):
                row, col = path[index]
                self.tiles[row][col].set_ai_highlighted(True)
                QTimer.singleShot(300, lambda: highlight_tile(index + 1))
        highlight_tile(0)

    def clear_ai_highlight(self):
        for row, col in self.ai_highlighted_path:
            if row < len(self.tiles) and col < len(self.tiles[0]):
                self.tiles[row][col].set_ai_highlighted(False)
                self.tiles[row][col].update_style()
        self.ai_highlighted_path = []
        if "AI suggests:" in self.word_display.text():
            self.word_display.setText("")
            self.word_display.setStyleSheet("""
                font-size: 36px;
                font-weight: bold;
                color: #4CAF50;
                padding: 15px;
                background-color: white;
                border: 3px solid #4CAF50;
                border-radius: 10px;
                min-height: 60px;
            """)

    def start_ai_cooldown(self):
        self.ai_cooldown_remaining = self.ai_cooldown_time
        self.ai_helper_btn.setText('AI Helper')
        self.ai_helper_btn.setEnabled(False)
        self.ai_cooldown_timer = QTimer()
        self.ai_cooldown_timer.timeout.connect(self.update_ai_cooldown)
        self.ai_cooldown_timer.start(1000)
        self.update_ai_cooldown()

    def update_ai_cooldown(self):
        if self.ai_cooldown_remaining > 0:
            self.ai_cooldown_label.setText(f"Cooldown: {self.ai_cooldown_remaining}s")
            self.ai_cooldown_remaining -= 1
        else:
            self.ai_cooldown_label.setText("")
            self.ai_helper_btn.setEnabled(True)
            if self.ai_cooldown_timer:
                self.ai_cooldown_timer.stop()
                self.ai_cooldown_timer = None

    def confirm_end_game(self):
        if hasattr(self, 'timer'):
            self.timer.stop()
        if self.ai_cooldown_timer:
            self.ai_cooldown_timer.stop()
        dialog = EndGameDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.end_game()
        else:
            if hasattr(self, 'timer') and self.timer_seconds > 0:
                self.timer.start()
            if self.ai_cooldown_timer and self.ai_cooldown_remaining > 0:
                self.ai_cooldown_timer.start()

    def submit_word(self):
        if len(self.current_word) < 3:
            self.clear_selection()
            return

        if self.current_word.upper() in self.found_words:
            self.setEnabled(False)
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    self.tiles[row][col].flash_color('orange', 'darkorange')
            self.word_display.setText("<b>Word Already Found</b>")
            self.word_display.setStyleSheet("""
                font-size: 36px;
                font-weight: bold;
                color: orange;
                padding: 15px;
                background-color: white;
                border: 3px solid orange;
                border-radius: 10px;
                min-height: 60px;
            """)
            QTimer.singleShot(1000, lambda: (self.reset_all_tiles(), self.clear_selection(), self.setEnabled(True)))
            return

        elif self.validator.is_valid_word(self.current_word):
            self.found_words.append(self.current_word.upper())
            points = floor((len(self.current_word) - 2) * 1.5)
            self.score += points
            self.score_label.setText(f'Score: {self.score}')
            self.words_display.setText(', '.join(self.found_words))
            self.setEnabled(False)
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    self.tiles[row][col].flash_color('green', 'darkgreen')
            self.word_display.setText(f"<b>+{points}</b>")
            self.word_display.setStyleSheet("""
                            font-size: 36px;
                            font-weight: bold;
                            color: green;
                            padding: 15px;
                            background-color: white;
                            border: 3px solid green;
                            border-radius: 10px;
                            min-height: 60px;
                        """)
            QTimer.singleShot(1000, lambda: (self.reset_all_tiles(), self.clear_selection(), self.setEnabled(True)))

        else:
            self.setEnabled(False)
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    self.tiles[row][col].flash_color('red', 'darkred')
            self.word_display.setText(f"<b>{self.current_word} is not valid</b>")
            self.word_display.setStyleSheet("""
                font-size: 36px;
                font-weight: bold;
                color: red;
                padding: 15px;
                background-color: white;
                border: 3px solid red;
                border-radius: 10px;
                min-height: 60px;
            """)
            QTimer.singleShot(1000, lambda: (self.reset_all_tiles(), self.clear_selection(), self.setEnabled(True)))

    def start_selection(self, row, col):
        self.clear_selection()
        self.clear_ai_highlight()
        self.is_dragging = True
        self.add_to_selection(row, col)

    def add_to_selection(self, row, col):
        if (row, col) in self.selected_path:
            return
        if self.selected_path and not self.is_adjacent(row, col):
            return
        self.selected_path.append((row, col))
        self.tiles[row][col].set_selected(True)
        self.current_word += self.board_letters[row][col]
        self.word_display.setText(self.current_word)

    def is_adjacent(self, row, col):
        if not self.selected_path:
            return True
        last_row, last_col = self.selected_path[-1]
        return abs(row - last_row) <= 1 and abs(col - last_col) <= 1

    def mouseMoveEvent(self, event):
        if not self.is_dragging:
            return
        pos = event.pos()
        widget = self.childAt(pos)
        if isinstance(widget, TileButton):
            self.add_to_selection(widget.row, widget.col)

    def mouseReleaseEvent(self, event):
        if self.is_dragging:
            self.is_dragging = False
            self.submit_word()

    def clear_selection(self):
        for row, col in self.selected_path:
            self.tiles[row][col].set_selected(False)
        self.selected_path = []
        self.current_word = ""
        if "AI suggests:" not in self.word_display.text():
            self.word_display.setText("")
            self.word_display.setStyleSheet("""
                font-size: 36px;
                font-weight: bold;
                color: #4CAF50;
                padding: 15px;
                background-color: white;
                border: 3px solid #4CAF50;
                border-radius: 10px;
                min-height: 60px;
            """)

    def reset_tile_colors(self):
        for row, col in self.selected_path:
            tile = self.tiles[row][col]
            tile.is_selected = False
            tile.is_ai_highlighted = False
            tile.update_style()

    def reset_all_tiles(self):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                tile = self.tiles[row][col]
                tile.is_selected = False
                tile.is_ai_highlighted = False
                tile.update_style()

    def start_timer(self):
        self.time_left = self.timer_seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)
        self.update_timer()

    def update_timer(self):
        if self.time_left <= 0:
            self.timer.stop()
            self.end_game()
            return
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        self.timer_label.setText(f'Time: {minutes:02d}:{seconds:02d}')
        self.time_left -= 1

    def end_game(self):
        if hasattr(self, 'timer'):
            self.timer.stop()
        if self.ai_cooldown_timer:
            self.ai_cooldown_timer.stop()
        game_data = {
            'score': self.score,
            'found_words': self.found_words,
            'all_possible_words': self.all_possible_words,
            'board': self.board_letters,
            'grid_size': self.grid_size,
            'time_played': self.timer_seconds - (self.time_left if hasattr(self, 'time_left') else 0),
            'ai_helper_uses': self.ai_helper_uses,
            'difficulty': self.difficulty,
            'timer': self.timer_seconds
        }
        self.hide()
        self.analytics = AnalyticsWindow(game_data, self.main_window)
        self.analytics.show()