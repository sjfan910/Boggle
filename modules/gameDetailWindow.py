from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QFrame)
from PyQt5.QtCore import Qt
from css.gameDetailWindowcss import *
from modules.mergeSort import MergeSort

"""
GameDetailWindow displays detailed breakdown of a single game.
Shows completion percentage, timestamp, and words grouped by length.

Key Features:
- Words grouped by length (3-letter, 4-letter, etc., 7+ for long words)
- Color-coded: Green for found words, Red for missed words
- Green words displayed first, then red words
- Completion percentage shown for each word length category
- Back button returns to GameHistoryWindow
"""


def format_timestamp(timestamp_str):
    try:
        dt = datetime.fromisoformat(timestamp_str)
        day_name = dt.strftime('%A')
        day = dt.day
        month_name = dt.strftime('%B')
        time = dt.strftime('%H:%M')

        # Add ordinal suffix (st, nd, rd, th)
        # Days 11-20 always use 'th' (11th, 12th, 13th...)
        if 10 <= day % 100 <= 20:
            suffix = 'th'
        elif day % 10 == 1:
            suffix = 'st'
        elif day % 10 == 2:
            suffix = 'nd'
        elif day % 10 == 3:
            suffix = 'rd'
        else:
            suffix = 'th'

        return f"{day_name} {day}{suffix} {month_name} {time}"
    except:
        return "Unknown date"


class GameDetailWindow(QWidget):

    def __init__(self, game_data, history_window=None):
        super().__init__()
        self.game_data = game_data
        self.history_window = history_window
        self.__initUI()

    def __initUI(self):
        self.setWindowTitle('Game Details')
        self.setFixedSize(900, 700)
        self.setStyleSheet("background-color: #f0f0f0;")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 20, 30, 20)

        header_layout = QVBoxLayout()
        header_layout.setSpacing(10)

        found = len(self.game_data.get('found_words', []))
        total = len(self.game_data.get('all_possible_words', []))
        completion = (found / total * 100) if total > 0 else 0

        completion_label = QLabel(f'Completion: <span style="color: #FF9800;">{completion:.1f}%</span>')
        completion_label.setStyleSheet(completionLabelStyle)

        timestamp_str = self.game_data.get('timestamp', '')
        formatted_time = format_timestamp(timestamp_str)

        grid_size = self.game_data.get('grid_size', 4)
        difficulty = self.game_data.get('difficulty', 'Unknown')
        timer = self.game_data.get('timer', None)
        if timer is None or timer == 'Unknown':
            # Fallback: show time played in mm:ss format
            time_played = self.game_data.get('time_played', 0)
            minutes = time_played // 60
            seconds = time_played % 60
            timer = f"{minutes}:{seconds:02d} played"

        info_text = f"{formatted_time} • {grid_size}x{grid_size} Grid, {difficulty} mode, {timer}"
        info_label = QLabel(info_text)
        info_label.setStyleSheet(infoLabelStyle)

        top_bar = QHBoxLayout()
        back_btn = QPushButton('Back')
        back_btn.setFixedSize(120, 40)
        back_btn.setStyleSheet(backButtonStyle)
        back_btn.clicked.connect(self.back_to_history)

        top_bar.addStretch()
        top_bar.addWidget(back_btn)

        header_layout.addLayout(top_bar)
        header_layout.addWidget(completion_label)
        header_layout.addWidget(info_label)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #ddd;")
        separator.setFixedHeight(2)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(scrollAreaStyle)

        scroll_content = QWidget()
        words_layout = QVBoxLayout()
        words_layout.setSpacing(20)

        word_groups = self.__group_words_by_length()

        lengths = list(word_groups.keys())
        MergeSort.sort(lengths)
        for length in lengths:
            if length >= 7:
                continue  # Handle 7+ separately

            group_widget = self.__create_word_group_widget(length, word_groups[length])
            words_layout.addWidget(group_widget)

        # Collect all words of length 7 or more into a single '7+' group
        long_words = {'found': [], 'missed': []}
        for length in word_groups.keys():
            if length >= 7:
                long_words['found'].extend(word_groups[length]['found'])
                long_words['missed'].extend(word_groups[length]['missed'])

        if long_words['found'] or long_words['missed']:
            group_widget = self.__create_word_group_widget('7+', long_words)
            words_layout.addWidget(group_widget)

        words_layout.addStretch()
        scroll_content.setLayout(words_layout)
        scroll.setWidget(scroll_content)
        main_layout.addLayout(header_layout)
        main_layout.addWidget(separator)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)


    def __group_words_by_length(self):
        found_words = set(word.upper() for word in self.game_data.get('found_words', []))
        all_words = set(word.upper() for word in self.game_data.get('all_possible_words', []))
        missed_words = all_words - found_words
        word_groups = {}
        for word in all_words:
            length = len(word)
            if length not in word_groups:
                word_groups[length] = {'found': [], 'missed': []}

            if word in found_words:
                word_groups[length]['found'].append(word)
            else:
                word_groups[length]['missed'].append(word)
        for length in word_groups:
            MergeSort.sort(word_groups[length]['found'])
            MergeSort.sort(word_groups[length]['missed'])
        return word_groups

    def __create_word_group_widget(self, length, words_dict):
        container = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        found_count = len(words_dict['found'])
        total_count = found_count + len(words_dict['missed'])
        completion = (found_count / total_count * 100) if total_count > 0 else 0

        length_str = str(length)
        header = QLabel(f'{length_str} Letter Words <span style="color: #4CAF50;">{completion:.1f}%</span>')
        header.setStyleSheet(groupHeaderStyle)
        layout.addWidget(header)

        words_container = QWidget()
        words_container.setStyleSheet(wordsContainerStyle)

        words_layout = QVBoxLayout()
        words_layout.setSpacing(5)
        all_words = []

        for word in words_dict['found']:
            word_label = QLabel(word.capitalize())
            word_label.setStyleSheet(foundWordStyle)
            all_words.append(word_label)

        for word in words_dict['missed']:
            word_label = QLabel(word.capitalize())
            word_label.setStyleSheet(missedWordStyle)
            all_words.append(word_label)
        row_layout = QHBoxLayout()
        row_layout.setSpacing(10)
        words_per_row = 8

        for i, word_label in enumerate(all_words):
            row_layout.addWidget(word_label)
            if (i + 1) % words_per_row == 0 and i < len(all_words) - 1:
                row_layout.addStretch()
                words_layout.addLayout(row_layout)
                row_layout = QHBoxLayout()
                row_layout.setSpacing(10)

        if row_layout.count() > 0:
            row_layout.addStretch()
            words_layout.addLayout(row_layout)

        words_container.setLayout(words_layout)
        layout.addWidget(words_container)
        container.setLayout(layout)
        return container

    def back_to_history(self):
        if self.history_window:
            self.hide()
            self.history_window.show()
        else:
            self.close()