import threading
from wordfreq import word_frequency
from modules.validation import WordValidator

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
        self.validator = WordValidator()
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
