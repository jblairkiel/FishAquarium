"""Module for testing fish"""
import sys

sys.path.insert(0, "..")
sys.path.insert(0, "../..")
from src.fish import Fish
from src.graphics.Colors import Colors


class TestFish:
    """Class for testing fish"""

    def test_fish_creation(self):
        """Testing creation of Fish"""
        fish = Fish(5, 10)
        assert fish.x == 5
        assert isinstance(type(fish.color), type(Colors.FISH_COLOR))
