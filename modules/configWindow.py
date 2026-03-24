import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
from css.configWindowcss import *

"""
This file creates the configuration screen where the user customize Boggle game settings.
It acts as the bridge between the main menu and the actual game, managing all game parameters.
"""
class ConfigWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.gridsize_index = 0
        self.timer_index = 0
        self.difficulty_index = 0
        self.helper_index = 0

        self.gridsize_options = ["4x4", "5x5"]
        self.timer_options = ["3:00", "3:30", "4:00", "Off"]
        self.difficulty_options = ["Medium", "Hard", "Easy"]
        self.helper_options = ["On", "Off"]

        self.__initUI()

    def __initUI(self):
        self.setWindowTitle('Boggle Configuration')
        self.setFixedSize(900, 700)
        self.setStyleSheet("background-color: white;")
        main_layout = QVBoxLayout()
        title = QLabel('Game Configuration')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(titleStyle)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(30)

        gridsize_label = QLabel('Grid Size')
        gridsize_label.setAlignment(Qt.AlignCenter)
        gridsize_label.setStyleSheet(gridStyle)
        self.gridsize_btn = self.__create_toggle_button(self.gridsize_options[0])
        self.gridsize_btn.clicked.connect(self.__toggle_gridsize)

        timer_label = QLabel('Timer')
        timer_label.setAlignment(Qt.AlignCenter)
        timer_label.setStyleSheet(gridStyle)
        self.timer_btn = self.__create_toggle_button(self.timer_options[0])
        self.timer_btn.clicked.connect(self.__toggle_timer)

        difficulty_label = QLabel('Difficulty')
        difficulty_label.setAlignment(Qt.AlignCenter)
        difficulty_label.setStyleSheet(gridStyle)
        self.difficulty_btn = self.__create_toggle_button(self.difficulty_options[0])
        self.difficulty_btn.clicked.connect(self.__toggle_difficulty)

        helper_label = QLabel('AI Helper')
        helper_label.setAlignment(Qt.AlignCenter)
        helper_label.setStyleSheet(gridStyle)
        self.helper_btn = self.__create_toggle_button(self.helper_options[0])
        self.helper_btn.clicked.connect(self.__toggle_helper)

        grid_layout.addWidget(gridsize_label, 0, 0)
        grid_layout.addWidget(self.gridsize_btn, 1, 0)
        grid_layout.addWidget(timer_label, 0, 1)
        grid_layout.addWidget(self.timer_btn, 1, 1)
        grid_layout.addWidget(difficulty_label, 2, 0)
        grid_layout.addWidget(self.difficulty_btn, 3, 0)
        grid_layout.addWidget(helper_label, 2, 1)
        grid_layout.addWidget(self.helper_btn, 3, 1)

        start_btn = QPushButton('Start Game')
        start_btn.setFixedSize(200, 50)
        start_btn.setStyleSheet(startButtonStyle)
        start_btn.clicked.connect(self.start_game)

        back_btn = QPushButton('Back to Menu')
        back_btn.setFixedSize(200, 40)
        back_btn.setStyleSheet(backButtonStyle)
        back_btn.clicked.connect(self.back_to_menu)

        button_container = QVBoxLayout()
        button_container.setAlignment(Qt.AlignCenter)
        button_container.addWidget(start_btn)
        button_container.addSpacing(10)
        button_container.addWidget(back_btn)

        main_layout.addWidget(title)
        main_layout.addLayout(grid_layout)
        main_layout.addStretch()
        main_layout.setContentsMargins(50, 30, 50, 30)
        main_layout.addLayout(button_container)

        self.setLayout(main_layout)

    def __create_toggle_button(self, text):
        button = QPushButton(text)
        button.setFixedSize(150, 80)
        button.setStyleSheet(toggleButtonStyle)
        return button

    def __toggle_gridsize(self):
        self.gridsize_index = (self.gridsize_index + 1) % len(self.gridsize_options)
        self.gridsize_btn.setText(self.gridsize_options[self.gridsize_index])

    def __toggle_timer(self):
        self.timer_index = (self.timer_index + 1) % len(self.timer_options)
        self.timer_btn.setText(self.timer_options[self.timer_index])

    def __toggle_difficulty(self):
        self.difficulty_index = (self.difficulty_index + 1) % len(self.difficulty_options)
        self.difficulty_btn.setText(self.difficulty_options[self.difficulty_index])

    def __toggle_helper(self):
        self.helper_index = (self.helper_index + 1) % len(self.helper_options)
        self.helper_btn.setText(self.helper_options[self.helper_index])

    def start_game(self):
        config = {
            'grid_size': self.gridsize_options[self.gridsize_index],
            'timer': self.timer_options[self.timer_index],
            'difficulty': self.difficulty_options[self.difficulty_index],
            'ai_helper': self.helper_options[self.helper_index]
        }
        from modules.boggleGame import BoggleGame
        self.hide()
        print(self.main_menu.__dict__)
        self.game_window = BoggleGame(config, self.main_menu)
        self.game_window.config_window = self
        self.game_window.show()

    def back_to_menu(self):
        if self.main_menu:
            self.hide()
            self.main_menu.show()
        else:
            self.close()
