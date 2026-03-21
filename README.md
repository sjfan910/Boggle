# Boggle — A-Level CS NEA Project

A full-featured implementation of the classic Boggle word-finding game built with Python and PyQt5. Includes an AI word suggestion system, persistent game history, post-game analytics, and configurable difficulty.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [How to Play](#how-to-play)
- [Architecture](#architecture)
- [Modules](#modules)
- [Algorithms](#algorithms)
- [Data Storage](#data-storage)
- [Configuration Options](#configuration-options)
- [Scoring](#scoring)

---

## Overview

This project is a complete desktop Boggle game written in Python. Players are presented with a grid of letter tiles and must find as many valid English words as possible by connecting adjacent tiles. The game supports 4×4 and 5×5 boards, multiple timer options, adjustable difficulty, and an optional AI helper that suggests high-value words.

---

## Features

- **4×4 and 5×5 boards** generated using authentic Boggle dice configurations
- **Difficulty levels** (Easy / Medium / Hard) that control board generation to ensure an appropriate number of findable words
- **Configurable timer** (3:00, 3:30, 4:00, or Off)
- **AI Helper** — suggests a word using a beam search algorithm scored by real English word frequency
- **Post-game analytics** showing found vs missed words and completion percentage
- **Persistent game history** saved to JSON, browsable and deletable
- **Per-game detail view** grouping words by length with found/missed colour coding
- **Word validation** via a Trie loaded from the 172K-word ENABLE1 dictionary
- **Drag-to-select** word input with real-time visual feedback

---

## Installation

**Requirements:** Python 3.7+

```bash
pip install -r requirements.txt
python main.py
```

### Dependencies

| Package | Purpose |
|---------|---------|
| `PyQt5==5.15.10` | GUI framework |
| `wordfreq` | English word frequency data for AI scoring |

---

## How to Play

1. Launch the game with `python main.py`
2. From the **Main Menu**, click **Play**
3. On the **Config Screen**, choose your grid size, timer, difficulty, and whether to enable the AI helper
4. Click **Start** — the board is generated and the timer begins (if set)
5. **Select words** by clicking tiles or click-and-dragging across adjacent tiles
6. Valid words are added to your word list and scored; invalid words flash red
7. When the timer expires (or you click **End Game**), the **Analytics Screen** appears
8. Optionally **save** the game to history, then return to the main menu

### Word Selection Rules

- Words must be at least **3 letters** long
- Each tile may only be used **once per word**
- Tiles must be **adjacent** (including diagonals)
- `Q` tiles are treated as **"Qu"** (one tile = two letters)

---

## Architecture

```
main.py
└── MainMenu  (homepageWindow.py)
    └── ConfigWindow  (configWindow.py)
        └── BoggleGame  (boggleGame.py)
            ├── BoardGenerator  (boardGen.py)
            ├── WordFinder      (wordFinder.py)
            ├── WordValidator   (validation.py)
            ├── AIHelper        (aiHelper.py)
            └── AnalyticsWindow (analyticsWindow.py)
                └── GameHistoryWindow (gameHistoryWindow.py)
                    └── GameDetailWindow (gameDetailWindow.py)
```

All persistent data lives in `data/game_history.json`.

---

## Modules

### `main.py`
Entry point. Creates the QApplication and launches `MainMenu`.

---

### `homepageWindow.py` — Main Menu
`MainMenu(QWidget)` displays the title screen with **Play**, **History**, and **Quit** buttons.

---

### `configWindow.py` — Game Configuration
`ConfigWindow(QWidget)` presents toggle-style buttons for:
- Grid size: `4×4` / `5×5`
- Timer: `3:00` / `3:30` / `4:00` / `Off`
- Difficulty: `Easy` / `Medium` / `Hard`
- AI Helper: `On` / `Off`

Passes the selected configuration to `BoggleGame` on start.

---

### `boggleGame.py` — Game Engine
The core gameplay module.

- **`BoggleGame(QWidget)`** — Manages board state, input handling, scoring, the countdown timer, and transitions to analytics.
- **`TileButton(QPushButton)`** — Represents an individual letter tile; handles mouse press, enter, and release events for drag-selection.
- **`EndGameDialog(QDialog)`** — Confirmation prompt shown when the player clicks End Game.

Key behaviours:
- Validates each completed word against `WordValidator`
- Animates AI-suggested word paths on the board
- Enforces a **20-second cooldown** between AI helper uses
- Calculates scores via `floor((word_length - 2) * 1.5)`

---

### `boardGen.py` — Board Generation
`BoardGenerator` creates the letter grid.

- Uses **real Boggle dice** — 16 dice for 4×4, 25 dice for 5×5 — rolling each to pick a face
- After generation, runs `WordFinder` to count available words
- Regenerates (up to 50 attempts) until the word count matches the chosen difficulty:

| Grid | Easy | Medium | Hard |
|------|------|--------|------|
| 4×4  | 80+  | 50–79  | <50  |
| 5×5  | 150+ | 100–149| <100 |

- Falls back to frequency-weighted random generation if no dice config is available

---

### `validation.py` — Word Validation
Implements a **Trie** data structure loaded from `data/enable1.txt` (172 000+ words).

- **`TrieNode`** — Single node storing child references and an `is_end` flag
- **`Trie`** — Insert and lookup with both `search` (exact word) and `starts_with` (prefix check)
- **`WordValidator`** — Public interface; enforces the 3-letter minimum

Word lookup: O(L) where L = word length.  
Prefix pruning in `WordFinder` uses `starts_with` to cut invalid search branches early.

---

### `wordFinder.py` — Word Discovery
`WordFinder` finds **every valid word** on the current board using **depth-first search with backtracking**.

- Starts a DFS from every cell
- Explores all 8 neighbours at each step
- Tracks visited cells to prevent tile reuse
- Prunes branches where the current prefix matches no dictionary words
- Returns a sorted, deduplicated list of all valid words

---

### `aiHelper.py` — AI Word Suggestion
`AIHelper` suggests one high-value word when the player requests a hint.

- **`BeamSearchNode`** — Represents a partial path (cells visited, letters accumulated)
- **Algorithm**: Multi-threaded **greedy beam search** (beam width = 2) launched from every board cell
- **Scoring**: Uses `wordfreq` to get the Zipf frequency (0–8 scale; higher = more common) of each candidate word
- Adaptive threshold: starts at 4.0, reduces if no qualifying word is found
- Excludes words already found by the player
- Caps suggestions at 5 letters to keep hints useful
- Animates the suggested word's path on the board tile-by-tile

---

### `analyticsWindow.py` — Post-Game Analytics
`AnalyticsWindow(QWidget)` is shown immediately after the game ends.

Displays:
- Final score and number of words found
- Completion percentage (found ÷ all possible words)
- Scrollable list of missed words
- Option to **save** the game (writes to `data/game_history.json`) or **discard**

`DeleteGameDialog(QDialog)` — confirmation before deleting a saved game from within analytics.

---

### `gameHistoryWindow.py` — Game History Browser
`GameHistoryWindow(QWidget)` lists all saved games in reverse chronological order.

- **`GameBlock(QFrame)`** — Card-style widget showing date, score, completion %, grid size, difficulty, and timer setting
- Clicking a card opens `GameDetailWindow`
- Each card has a delete button

---

### `gameDetailWindow.py` — Game Detail View
`GameDetailWindow(QWidget)` shows a full breakdown of one saved game.

- Words grouped by length: 3, 4, 5, 6, 7+
- **Green** = found by the player; **Red** = missed
- Per-group completion percentage
- Found words listed before missed words within each group

---

## Algorithms

### Depth-First Search — Word Finding

```
For each cell on the board:
    DFS(cell, path=[cell], current_word=""):
        if current_word is a valid word → add to results
        for each unvisited neighbour:
            if current_word + neighbour.letter is a valid prefix:
                DFS(neighbour, path + [neighbour], current_word + letter)
```

Complexity: O(8^L × N) — L = max word length, N = number of cells.

### Trie — Word Validation

Standard prefix tree. Insert all dictionary words at startup; each lookup is O(L).

### Beam Search — AI Suggestion

```
beam = [BeamSearchNode(start_cell) for every cell]
while beam not exhausted:
    expand each node to all valid neighbours
    score completed words with wordfreq Zipf score
    keep top-B candidates by score
return highest-scoring word above frequency threshold
```

---

## Data Storage

Games are saved to `data/game_history.json` as a JSON array. Each entry contains:

```json
{
  "score": 34,
  "found_words": ["REEF", "SOLD", "CHEER"],
  "all_possible_words": ["AFT", "CEE", "REEF", "SOLD"],
  "board": [["S","D","T","P"], ["O","L","C","T"], ["H","E","E","R"], ["T","S","D","P"]],
  "grid_size": 4,
  "time_played": 142,
  "ai_helper_uses": 1,
  "difficulty": "Easy",
  "timer": 180,
  "timestamp": "2026-02-02T12:01:52.521244"
}
```

Dictionary data lives in `data/enable1.txt` and is read once at startup into the Trie.

---

## Configuration Options

| Setting | Options | Default |
|---------|---------|---------|
| Grid Size | 4×4, 5×5 | 4×4 |
| Timer | 3:00, 3:30, 4:00, Off | 3:00 |
| Difficulty | Easy, Medium, Hard | Medium |
| AI Helper | On, Off | Off |

---

## Scoring

Points per word: `floor((word_length − 2) × 1.5)`

| Word Length | Points |
|-------------|--------|
| 3 letters   | 1      |
| 4 letters   | 3      |
| 5 letters   | 4      |
| 6 letters   | 6      |
| 7 letters   | 7      |
| 8 letters   | 9      |