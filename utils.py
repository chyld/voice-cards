import os
import random
from config_manager import config

class FlashcardUtils:
    @staticmethod
    def generate_flashcard():
        num1 = random.randint(config.min_value, config.max_value)
        num2 = random.randint(config.min_value, config.max_value)
        return num1, num2

    @staticmethod
    def clear_screen():
        # For Windows
        if os.name == 'nt':
            _ = os.system('cls')
        # For macOS and Linux
        else:
            _ = os.system('clear')

flashcard_utils = FlashcardUtils()