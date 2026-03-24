from modules.validation import shared_validator

"""
This file discovers all valid words hidden in a Boggle board.
We use DFS with prefix pruning to ensure optimisation.

Key Attributes:
 - self.validator - WordValidator instance containing the Trie dictionary

Key Methods:
 - __init__(self): 
        - Constructor that initialises the word finder
        - Creates a WordValidator instance with loaded dictionary Trie
 - find_all_words(self, board):
        - Completes the search across the board
        - Creates empty set to store unique words
        - Determines board dimensions (4x4 or 5x5)
        - Stats DFS from every possible starting position
        - Creates new visited matrix for each starting position
        - Returns a sorted list of all discovered words
        - We must start from every cell because words can begin anywhere on the board
 - dfs(self, board, row, col, current_word, visited, found_words):
        - Recursive depth-first search that explores all possible word paths
        - Parameters:
            - board - Boggle board represented as a list of lists
            - row, col - int values of current position
            - current_word - Word being built as we traverse
            - visited - 2D boolean array tracking used tiles in current path
            - found_words - Set of all discovered valid words (Prevent duplication) 
        - Algorithm flow:
            - Base case - Stops recursion if pointer is at grid boundary (prevent searching outside the grid)
            - Revisit prevention - Prevents visiting tiles already visited 
            - Word building - Append current tile's letter to 'current_word' (process 'Qu' as single letter)
            - Prefix pruning - Prefix pruning using self.validator
            - Path marking - Marks the current tile as visited temporarily
            - Word Validation - Checks if current word is complete and valid according to Boggle Rules
            - Append found word - Add the current word if valid
            - Directional search - Recursively explores all 8 adjacent tiles 
            - Backtracking - Unmarks the current tile as unvisited
        - Complexity:
            - Time complexity - O(n)
            - Space complexity - O(n) 
        
FUNCTION dfs(board, row, col, current_word, visited, found_words):
    IF row < 0 OR row >= board_height OR col < 0 OR col >= board_width:
        RETURN
    
    IF visited[row][col] == TRUE:
        RETURN
        
    current_word = current_word + board[row][col]
    
    IF NOT is_valid_prefix(current_word):
        RETURN
        
    visited[row][col] = TRUE
    
    IF length(current_word) >= 3 AND is_valid_word(current_word):
        found_words.add(current_word)
        
    FOR i in direction [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1),
"""
class WordFinder:
    def __init__(self):
        self.validator = shared_validator

    def find_all_words(self, board): 
        # This is the public function
        found_words = set() # Different pathways same words don't duplicate
        rows = len(board)
        cols = len(board[0])
        for row in range(rows): 
            for col in range(cols): 
                visited = [[False] * cols for _ in range(rows)]
                self.__dfs(board, row, col, "", visited, found_words)

        return sorted(list(found_words))

    def __dfs(self, board, row, col, current_word, visited, found_words) -> None: 
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
            self.__dfs(board, row + dr, col + dc, current_word, visited, found_words)

        visited[row][col] = False