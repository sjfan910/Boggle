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

# Shared singleton — dictionary loaded once and reused by all modules
shared_validator = WordValidator()