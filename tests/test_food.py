"""This module tests the food class"""
import sys
sys.path.insert(0, "..")
sys.path.insert(0, "../..")
from src.food import Food

# from src.graphics.Colors import Colors


class TestFood:
    """Class for fish"""

    def test_food_creation(self):
        """Tests the creatin of a fish"""
        food = Food()
        assert food
        # assert isinstance(type(food.color), type(Colors.FISH_COLOR))
