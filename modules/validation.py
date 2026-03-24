import os

"""
This file validates the current word with a dictionary
Uses a prefix tree (Trie) data structure
Enables real-time word validation during gameplay

_TrieNode Class:
Key Attributes:
 - self.children - Dictionary mapping letters to child _TrieNodes
 - self.is_word - Boolean value indicating if path to this node forms a word
 - Each node can have up to 26 children and may represent the end of a word

_Trie Class:
Key Attributes:
 - self.root - The root _TrieNode

Key Methods:
 - __init__(self):
        - Constructor that creates an empty _Trie with root node
 - insert(self, word):
        - Adds a word to the _Trie
        - Start at a root
        - Process each letter in the word
        - If letter path doesn't exist, create new _TrieNode
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
 - starts_with(self, prefix):
        - Check if prefix exists in dictionary
        - Follow prefix path letter by letter from root
        - Return False if prefix path does not exist
        - Return True if path exists

WordValidator Class:
Key Attributes:
 - self.trie - _Trie instance containing entire dictionary

Key Methods:
 - __init__(self, dictionary_path='data/enable1.txt'):
        - Constructor that builds complete dictionary _Trie
        - Attempts to load dictionary file
        - Fall back to basic word list if file is unavailable
 - __load_dictionary(self, path)
        - Reads dictionary file and populates the _Trie
        - Checks if dictionary exists
        - Strip whitespaces, converts to uppercase
        - Only include words ≥ 3 letters (According to Boggle rules)
        - Displays word count loaded
 - is_valid_word(self, word):
        - Public interface checking if word exists in dictionary
 - is_valid_prefix(self, prefix):
        - Public interface checking if prefix exists in dictionary
"""

class _TrieNode:
    def __init__(self):
        self.children = {}
        self.is_word = False

class _Trie:
    def __init__(self):
        self.root = _TrieNode()

    def insert(self, word) -> None: # add a children node
        node = self.root
        for char in word.upper():
            if char not in node.children:
                node.children[char] = _TrieNode()
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
#     """
#     Generates difficulty-filtered word list files from enable1.txt.
#     Run this once offline to produce easy.txt, medium.txt, hard.txt.
#     WordValidator then loads the appropriate file based on difficulty.
#
#     Difficulty thresholds (Zipf frequency scale, 0-8):
#      - Easy:   > 5.00  (very common words, e.g. "STONE", "PLACE")
#      - Medium: > 4.00  (moderately common words)
#      - Hard:   > 3.10  (includes rarer valid Boggle words)
#
#     Words are also filtered against a profanity wordlist and capped at
#     15 characters (Boggle boards produce no longer paths in practice).
#     """
#
#     DIFFICULTY_THRESHOLDS = {
#         'Easy':   5.00,
#         'Medium': 4.00,
#         'Hard':   3.10,
#     }
#
#     FILE_PATHS = {
#         'Easy':   'data/easy.txt',
#         'Medium': 'data/medium.txt',
#         'Hard':   'data/hard.txt',
#     }
#
#     def __init__(self, source_path='data/enable1.txt', profanity_path='data/profanity_wordlist.txt'):
#         self.source_path = source_path
#         self.banned = self.__load_banned(profanity_path)
#
#     def __load_banned(self, profanity_path):
#         banned = set()
#         if os.path.exists(profanity_path):
#             with open(profanity_path, 'r') as f:
#                 for line in f:
#                     banned.add(line.strip().upper())
#         return banned
#
#     def generate_all(self):
#         """Build and write easy.txt, medium.txt, hard.txt from enable1.txt."""
#         word_lists = {difficulty: [] for difficulty in self.DIFFICULTY_THRESHOLDS}
#
#         with open(self.source_path, 'r') as f:
#             for line in f:
#                 word = line.strip()
#                 if not (3 < len(word) < 16) or word.upper() in self.banned:
#                     continue
#                 frequency = zipf_frequency(word, 'en')
#                 for difficulty, threshold in self.DIFFICULTY_THRESHOLDS.items():
#                     if frequency > threshold:
#                         word_lists[difficulty].append(word)
#
#         for difficulty, words in word_lists.items():
#             with open(self.FILE_PATHS[difficulty], 'w') as f:
#                 for word in words:
#                     f.write(word + '\n')
#             print(f"Written {len(words)} words to {self.FILE_PATHS[difficulty]}")
#
#     @staticmethod
#     def get_path_for_difficulty(difficulty):
#         """Return the pre-built word list path for a given difficulty string."""
#         return PreProcessing.FILE_PATHS.get(difficulty, 'data/enable1.txt')

class WordValidator:
    def __init__(self, dictionary_path='/Users/sjf/Documents/My NEA/Boggle/data/enable1.txt'):
        self.trie = _Trie()
        self.__load_dictionary(dictionary_path)

    def __load_dictionary(self, path) -> bool:
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

# Shared singleton — dictionary loaded once and reused by all modules
shared_validator = WordValidator()
