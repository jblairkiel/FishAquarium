import sys
import os
from typing import Literal, Tuple

#Adjusting PATH
abovePath = os.path.join(__file__, "..", "..")
print("Adding Path: " + os.path.abspath(abovePath))
sys.path.append(abovePath)
print("SysPath: " + sys.path.__str__())

from src.fish import Fish
from src.graphics.Colors import Colors
class TestFish:
    def test_fish_creation(self):
        fish = Fish(5, 10)
        assert fish.x == 5
        assert type(fish.color) == type(Colors.FISH_COLOR)

    def test_fish_swim(self):
        fish = Fish(5, 10)
        assert fish