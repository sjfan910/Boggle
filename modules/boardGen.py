import random
from modules.wordFinder import WordFinder
from modules.validation import PreProcessing

"""
This file generates a Boggle board using real dice configurations. 
We use wordFinder to validate if there are enough words in the board generated matching the difficulty

Key Attributes:
 - self.size - Grid dimensions (4 for classic, 5 for big)
 - self.difficulty - String value of 'Easy', 'Medium', or 'Hard'
 - self.word_finder - WordFinder instance to analyse generated boards
 
Constants (These are static data fixed for this file):
 - CLASSIC_DICE - Array of 16 Boggle dice, each containing 6 letters
 - BIG_DICE - Array of 25 Boggle dice, suitable for 5x5 variant
 - We use these dice to add weights to characters
 - These Boggle dice are designed to capture the frequency of English letter in words
 - This ensure generations have higher chance creating more words 
 
Key Methods:
 - __init__(self, size=4, difficulty='Easy'):
        - Constructor that initialises the parameters
        - size - Grid size (4 or 5)
        - difficulty - String value of 'Easy' or 'Medium' or 'Hard'
 - generate(self):
        - Creates a board that meets the specified difficulty
        - We loop through 50 times to generate the suitable board
        - We use dice-based generation for 4x4/5x5
        - In case this doesn't work, we fall back to randomising the board
        - We count the words using WordFinder
        - We ensure the word present matches the difficulty level
        - We return the first suitable board or final attempt if none qualified
        
 - generate_from_dice(self, dice):
        - This creates board using real Boggle dice mechanics
        - We shuffle where each die go
        - We randomly select one of the 6 faces for each die
        - We convert 'Q' to 'Qu' 
        - We place letters into 2D array structure

 - generate_random(self):
        - This is the fallback method using weighted letter frequencies
        - We use English letter frequency weights (E=12, T=9, A=8, etc.)
        - Includes 'Qu' as a single tile
        - We must have fallback logic in case Main method fails
        
 - meets_difficulty(self, word_count):
        - Ensures the board is playable regardless of difficulty
        - Difficulty affects word frequency (via PreProcessing/WordValidator), not word count
        - Minimum threshold: 50 words on any board size
            
 Algorithm Flow: 
    - generate() called
    - Loop up to 50 times
    - generate_from_dice() 
    - WordFinder.find_all_words() 
    - meets_difficulty() 
    - Return if suitable
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
        self.band_validator = PreProcessing(difficulty)

    def generate(self):
        max_attempts = 100

        for attempt in range(max_attempts):
            if self.size == 4:
                board = self.__generate_from_dice(self.CLASSIC_DICE)
            elif self.size == 5:
                board = self.__generate_from_dice(self.BIG_DICE)

            else: # Generate from random function (This was used for testing)
                board = self.__generate_random()

            all_words = self.word_finder.find_all_words(board)
            band_count = sum(1 for w in all_words if self.band_validator.is_valid_word(w))
            if self.__meets_difficulty(band_count):
                print(f"Board generated in {attempt} attempts with {band_count} difficulty-band words (Difficulty: {self.difficulty})")
                return board

        print(f"Warning: Could not generate board meeting {self.difficulty} difficulty")
        return board

    def __generate_from_dice(self, dice):
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

    def __generate_random(self):
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

    def __meets_difficulty(self, word_count):
        """Check board has enough words to be playable (min 50, regardless of difficulty)"""
        return word_count >= 50
