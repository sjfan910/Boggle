import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
                             QHBoxLayout)
from PyQt5.QtCore import Qt
from css.homepagecss import style

'''
This file serves as the application's main menu and navigation hub.
It provides the first interface users see and handles transitions to other components.

Key Attributes:
 - self.config_window - Reference to ConfigWindow for navigation management

Key Methods:
 - __init__(self):
        - Constructor that initializes the main menu window
        - Calls parent QWidget constructor and triggers UI setup
 - initUI(self):
        - Builds the complete user interface layout and styling
        - Window setup: Sets title "Boggle" and geometry (300,300,800,600)
        - Styling system: Applies CSS-like styling:
            - Light gray background (#f0f0f0)
            - Large bold title (72px, dark gray)
            - Styled buttons with rounded corners, padding, and hover effects
            - Color-coded buttons: Green (Play), Orange (Analytics), Red (Quit)
        - Layout architecture: Uses nested QVBoxLayout and QHBoxLayout
            - Vertical layout for overall structure with stretches for spacing
            - Horizontal layout for button arrangement
            - Centers title and evenly spaces buttons
        - Widget creation: Creates title label and three navigation buttons
        - Signal connections: Links button clicks to respective methods
 - play_game(self):
        - Transition from Menu to Configuration
 - show_analytics(self):
        - Transition from Menu to History Results
 - quit_game(self):
        - Quits the software
'''

class MainMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Boggle')
        self.setFixedSize(900, 700)
        self.setStyleSheet(style)

        v_layout = QVBoxLayout()
        h_layout = QHBoxLayout()

        title_label = QLabel('Boggle')
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignCenter)

        play_button = QPushButton('Play')
        play_button.setObjectName("PlayButton")
        play_button.clicked.connect(self.play_game)

        history_button = QPushButton('History')
        history_button.setObjectName("GameHistoryButton")
        history_button.clicked.connect(self.show_history)

        quit_button = QPushButton('Quit')
        quit_button.setObjectName("QuitButton")
        quit_button.clicked.connect(self.quit_game)

        h_layout.addStretch(1)
        h_layout.addWidget(play_button)
        h_layout.addWidget(history_button)
        h_layout.addWidget(quit_button)
        h_layout.addStretch(1)

        v_layout.addStretch(1)
        v_layout.addWidget(title_label)
        v_layout.addStretch(1)
        v_layout.addLayout(h_layout)
        v_layout.addStretch(2)

        self.setLayout(v_layout)

    def play_game(self):
        from modules.configWindow import ConfigWindow
        self.hide()
        self.config_window = ConfigWindow()
        self.config_window.main_menu = self
        self.config_window.show()

    def show_history(self):
        from modules.gameHistoryWindow import GameHistoryWindow
        self.hide()
        self.history_window = GameHistoryWindow(self)
        self.history_window.show()

    def quit_game(self):
        sys.exit()