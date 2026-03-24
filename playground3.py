import threading
import random
from wordfreq import zipf_frequency
import os

'''
This file validates the current word with a dictionary
Uses a prefix tree (Trie) data structure
Enables real-time word validation during gameplay

TrieNode Class:
Key Attributes:
 - self.children - Dictionary mapping letters to child TrieNodes
 - self.is_word - Boolean value indicating if path to this node forms a word
 - Each node can have up to 26 children and may represent the end of a word

Trie Class:
Key Attributes:
 - self.root - The root TrieNode

Key Methods:
 - __init__(self):
        - Constructor that creates an empty Trie with root node
 - insert(self, word):
        - Adds a word to the Trie
        - Start at a root 
        - Process each letter in the word
        - If letter path doesn't exist, create new TrieNode
        - Move down the tree following/creating the path
        - Set 'is_word' to True at final node
        - Ensure multiple words share common prefixes
 - search(self, word):
        - Checks if complete word exists in dictionary
        - Follow path letter by letter from root
        - Return False if any letter path missing
        - Check is_word at final node
        - True only if complete path exists and is_word is True
        - O(n) where n = word length 
 - stars_with(self, prefix):
        - Check if prefix exists in dictionary
        - Follow prefix path letter by letter from root
        - Return False if prefix path does not exist
        - Return True if path exists 
    
WordValidator Class:
Key Attributes:
 - self.trie - Trie instance containing entire dictionary
 
Key Methods:
 - __init__(self, dictionary_path='data/enable1.txt'): 
        - Constructor that builds complete dictionary Trie
        - Attempts to load dictionary file
        - Fall back to basic word list if file is unavailable
 - load_dictionary(self, path)
        - Reads dictionary file and populates the Trie
        - Checks if dictionary exists
        - Strip whitespaces, converts to uppercase
        - Only include words ≥ 3 letters (According to Boggle rules)
        - Displays word count loaded
 - load_basic_words(self)
        - Fallback dictionary if 'enable1.txt' is unavailable
 - is_valid_word(self, word):
        - Public interface checking if word exists in dictionary
 - is_valid_prefix(self, prefix):
        - Public interface checking if prefix exists in dictionary 
'''

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word) -> None: # add a children node
        node = self.root
        for char in word.upper():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char] # Travel down a layer
        node.is_word = True

    def search(self, word) -> bool:
        node = self.root
        for char in word.upper():
            if char not in node.children:
                return False
            node = node.children[char] # Travel down a layer
        return node.is_word

    def starts_with(self, prefix) -> bool: # Stops early for better performance
        node = self.root
        for char in prefix.upper():
            if char not in node.children:
                return False
            node = node.children[char]
        return True

# class PreProcessing:
#     def __init__(self):
#         self.banned = set()
#         self.easy = 
        
class WordValidator:
    def __init__(self, dictionary_path='data/enable1.txt'):
        self.trie = Trie()
        self.load_dictionary(dictionary_path)

    def load_dictionary(self, path) -> bool:
        if not os.path.exists(path):
            print(f"Dictionary not found at {path}.")
            return False
        try:
            with open(path, 'r') as f:
                word_count = 0
                for line in f:
                    word = line.strip().upper()
                    if len(word) >= 3:
                        self.trie.insert(word) # Builds the dictionary trie
                        word_count += 1
                print(f"Loaded {word_count} words from dictionary")
        except Exception as e:
            print(f"Error loading dictionary: {e}")
            return False
        return True

    def is_valid_word(self, word):
        return self.trie.search(word)

    def is_valid_prefix(self, prefix):
        return self.trie.starts_with(prefix)

class WordFinder:
    def __init__(self):
        self.validator = shared_validator

    def find_all_words(self, board): 
        # This is the public function
        found_words = set() # Prevent word duplication
        rows = len(board)
        cols = len(board[0])
        for row in range(rows): 
            for col in range(cols): 
                visited = [[False] * cols for _ in range(rows)]
                self.dfs(board, row, col, "", visited, found_words)

        return sorted(list(found_words))

    def dfs(self, board, row, col, current_word, visited, found_words) -> None: 
        # Private Function: purpose is to populate found_words = {all words in board}
        if row < 0 or row >= len(board) or col < 0 or col >= len(board[0]): # Base case
            return
        if visited[row][col]: # Base case
            return
        
        current_word += board[row][col]
        if not self.validator.is_valid_prefix(current_word):
            return

        visited[row][col] = True

        if len(current_word) >= 3 and self.validator.is_valid_word(current_word):
            found_words.add(current_word)

        directions = [(-1, -1), (0, -1), (1, -1), 
                      (-1, 0),           (1, 0),
                      (-1, 1),  (0, 1),  (1, 1)]
                      # Dig in all 8 directions   

        for dr, dc in directions:
            self.dfs(board, row + dr, col + dc, current_word, visited, found_words)

        visited[row][col] = False

shared_validator = WordValidator()

"""
AI Helper Module for Boggle Game
Implements a greedy beam search algorithm to suggest common words to the player.

Key Features:
- Greedy beam search with fixed beam width (5)
- Word frequency scoring using wordfreq library (Zipf scale)
- Excludes already-found words
- Multi-threaded search starting from all board tiles
- Adaptive threshold: starts at 4.0, decreases by 1.0 if no suggestions found

Algorithm Overview:
1. Start beam search from all tiles simultaneously (multi-threaded)
2. Maintain top 5 most promising paths based on word frequency
3. Expand paths in 8 directions, scoring by prefix/word frequency
4. Return first valid word above threshold
5. If no word found, recursively lower threshold and retry
"""

class BoardGenerator:
    """Generates Boggle boards based on Boggle Dice"""

    # Classic Boggle dice (16 dice for 4x4)
    CLASSIC_DICE = [
        "AAEEGN", "ELRTTY", "AOOTTW", "ABBJOO",
        "EHRTVW", "CIMOTU", "DISTTY", "EIOSST",
        "DELRVY", "ACHOPS", "HIMNQU", "EEINSU",
        "EEGHNW", "AFFKPS", "HLNNRZ", "DEILRX"
    ]

    # Big Boggle dice (25 dice for 5x5)
    BIG_DICE = [
        "AAAFRS", "AAEEEE", "AAFIRS", "ADENNN", "AEEEEM",
        "AEEGMU", "AEGMNN", "AFIRSY", "BJKQXZ", "CCNSTW",
        "CEIILT", "CEILPT", "CEIPST", "DDLNOR", "DHHLOR",
        "DHHNOT", "DHLNOR", "EIIITT", "EMOTTT", "ENSSSU",
        "FIPRSY", "GORRVW", "HIPRRY", "NOOTUW", "OOOTTU"
    ]

    def __init__(self, size=4, difficulty='Easy'):
        self.size = size
        self.difficulty = difficulty
        self.word_finder = WordFinder()

    def generate(self):
        max_attempts = 50

        for attempt in range(max_attempts):
            if self.size == 4:
                board = self.generate_from_dice(self.CLASSIC_DICE)
            elif self.size == 5:
                board = self.generate_from_dice(self.BIG_DICE)

            else: # Generate from random function (This was used for testing)
                board = self.generate_random()

            word_count = len(self.word_finder.find_all_words(board))
            if self.meets_difficulty(word_count):
                print(f"Board generated with {word_count} words (Difficulty: {self.difficulty})")
                return board

        print(f"Warning: Could not generate board meeting {self.difficulty} difficulty")
        return board

    def generate_from_dice(self, dice):
        """Generate board using Boggle dice"""
        shuffled_dice = dice.copy()
        random.shuffle(shuffled_dice)
        board = []
        dice_index = 0
        for row in range(self.size):
            board_row = []
            for col in range(self.size):
                die = shuffled_dice[dice_index]
                letter = random.choice(die)
                if letter == 'Q':
                    letter = 'Qu'
                board_row.append(letter)
                dice_index += 1
            board.append(board_row)
        return board

    def generate_random(self):
        """Generate board with weighted letters (This was used for testing)"""
        letter_weights = {
            'E': 12, 'T': 9, 'A': 8, 'O': 8, 'I': 7, 'N': 7,
            'S': 6, 'H': 6, 'R': 6, 'L': 4, 'D': 4, 'C': 3,
            'U': 3, 'M': 3, 'W': 2, 'F': 2, 'G': 2, 'Y': 2,
            'P': 2, 'B': 1, 'V': 1, 'K': 1, 'J': 1, 'X': 1,
            'Qu': 1, 'Z': 1
        }
        letter_pool = []
        for letter, weight in letter_weights.items():
            letter_pool.extend([letter] * weight)
        board = []
        for row in range(self.size):
            board_row = []
            for col in range(self.size):
                letter = random.choice(letter_pool)
                board_row.append(letter)
            board.append(board_row)
        return board

    def meets_difficulty(self, word_count):
        """Check if word count meets difficulty threshold"""
        if self.size == 4:
            if self.difficulty == 'Easy':
                return word_count >= 80
            elif self.difficulty == 'Medium':
                return 50 <= word_count < 80
            elif self.difficulty == 'Hard':
                return word_count < 50
        elif self.size == 5:
            # Adjust for 5x5 grid
            if self.difficulty == 'Easy':
                return word_count >= 150
            elif self.difficulty == 'Medium':
                return 100 <= word_count < 150
            elif self.difficulty == 'Hard':
                return word_count < 100
        return True
    

from wordfreq import word_frequency

"""
AI Helper Module for Boggle Game
Implements a greedy beam search algorithm to suggest common words to the player.

Key Features:
- Greedy beam search with fixed beam width (5)
- Word frequency scoring using wordfreq library (Zipf scale)
- Excludes already-found words
- Multi-threaded search starting from all board tiles
- Adaptive threshold: starts at 4.0, decreases by 1.0 if no suggestions found

Algorithm Overview:
1. Start beam search from all tiles simultaneously (multi-threaded)
2. Maintain top 5 most promising paths based on word frequency
3. Expand paths in 8 directions, scoring by prefix/word frequency
4. Return first valid word above threshold
5. If no word found, recursively lower threshold and retry
"""


class BeamSearchNode:
    def __init__(self, row, col, word, path, visited):
        """
        Initialize a beam search node

        Args:
            row (int): Current row position
            col (int): Current column position
            word (str): Word formed so far
            path (list): List of (row, col) tuples representing the path
            visited (set): Set of (row, col) tuples marking visited tiles
        """
        self.row = row
        self.col = col
        self.word = word
        self.path = path.copy()
        self.visited = visited.copy()
        self.score = self._calculate_score()

    def _calculate_score(self):
        """
        Calculate frequency score for current word/prefix
        Uses Zipf frequency scale (0-8, higher = more common)

        Returns:
            float: Frequency score
        """
        if len(self.word) < 2:
            letter_freq = {
                'E': 8, 'T': 7.5, 'A': 7.5, 'O': 7, 'I': 7, 'N': 7,
                'S': 6.5, 'H': 6.5, 'R': 6, 'D': 5.5, 'L': 5.5, 'U': 5
            }
            return letter_freq.get(self.word[-1], 3.0)
        freq = word_frequency(self.word.lower(), 'en', wordlist='best')
        if freq > 0:
            import math
            zipf_score = math.log10(freq * 1e8)
            return max(0, zipf_score)  # Ensure non-negative
        return 0.0


class AIHelper:
    def __init__(self):
        self.validator = shared_validator
        self.beam_width = 2
        self.max_word_length = 5

    def suggest_word(self, board, found_words, initial_threshold=4.0):
        """
        Suggest a common word from the board using beam search

        Args:
            board (list): 2D list representing the Boggle board
            found_words (set): Set of words already found by the player
            initial_threshold (float): Minimum Zipf frequency score (default 4.0)

        Returns:
            tuple: (word, path) where path is list of (row, col) coordinates
                   Returns (None, None) if no suggestion found
        """
        threshold = initial_threshold
        while threshold >= 0:
            result = self._search_with_threshold(board, found_words, threshold)
            if result[0] is not None:
                return result
            threshold -= 1.0
        return (None, None)

    def _search_with_threshold(self, board, found_words, threshold):
        """
        Search for words above given threshold using multi-threaded beam search
        Args:
            board (list): 2D list representing the Boggle board
            found_words (set): Set of words already found
            threshold (float): Minimum frequency threshold

        Returns:
            tuple: (word, path) or (None, None)
        """
        rows = len(board)
        cols = len(board[0])
        results = []
        results_lock = threading.Lock()
        found_result = threading.Event()

        def search_from_tile(start_row, start_col):
            """Thread worker: beam search starting from a specific tile"""
            if found_result.is_set():
                return
            result = self._beam_search(board, start_row, start_col, found_words, threshold, found_result)
            if result[0] is not None:
                with results_lock:
                    results.append(result)
                    found_result.set()

        # Create threads for each starting position
        threads = []
        for row in range(rows):
            for col in range(cols):
                thread = threading.Thread(target=search_from_tile, args=(row, col))
                threads.append(thread)
                thread.start()

        print(f"Starting search from {len(threads)} positions")

        for thread in threads:
            thread.join()

        if results:
            results.sort(key=lambda x: word_frequency(x[0].lower(), 'en', wordlist='best'), reverse=True)
            return results[0]
        return (None, None)

    def _beam_search(self, board, start_row, start_col, found_words, threshold, found_result):
        """
        Args:
            board (list): 2D list representing the board
            start_row (int): Starting row
            start_col (int): Starting column
            found_words (set): Words already found
            threshold (float): Minimum frequency threshold
            found_result (Event): Threading event to signal early termination

        Returns:
            tuple: (word, path) or (None, None)
        """
        rows = len(board)
        cols = len(board[0])
        print(f"Searching from ({start_row}, {start_col})")
        visited = set()
        visited.add((start_row, start_col))
        initial_node = BeamSearchNode(
            start_row, start_col,
            board[start_row][start_col],
            [(start_row, start_col)],
            visited
        )
        beam = [initial_node]
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1), (0, 1),
                      (1, -1), (1, 0), (1, 1)]

        while beam and len(beam[0].word) <= self.max_word_length:
            if found_result.is_set():
                return (None, None)

            for node in beam:
                if (len(node.word) >= 3 and
                        node.word.upper() not in found_words and
                        self.validator.is_valid_word(node.word)):
                    freq = word_frequency(node.word.lower(), 'en', wordlist='best')
                    import math
                    if freq > 0:
                        zipf_score = math.log10(freq * 1e8)
                        if zipf_score >= threshold:
                            return (node.word.upper(), node.path)

            candidates = []
            for node in beam:
                for dr, dc in directions:
                    new_row = node.row + dr
                    new_col = node.col + dc

                    if not (0 <= new_row < rows and 0 <= new_col < cols):
                        continue
                    if (new_row, new_col) in node.visited:
                        continue
                    new_word = node.word + board[new_row][new_col]
                    if not self.validator.is_valid_prefix(new_word):
                        continue

                    new_visited = node.visited.copy()
                    new_visited.add((new_row, new_col))
                    new_path = node.path + [(new_row, new_col)]
                    new_node = BeamSearchNode(
                        new_row, new_col,
                        new_word,
                        new_path,
                        new_visited
                    )
                    candidates.append(new_node)

            if not candidates:
                break

            candidates.sort(key=lambda n: n.score, reverse=True)
            beam = candidates[:self.beam_width]
            print(f"Beam size: {len(beam)}, Word length: {len(beam[0].word) if beam else 0}")
        return (None, None)


gen = BoardGenerator()
board = gen.generate()
print(board)
helper = AIHelper()
print(helper.suggest_word(board, {}))