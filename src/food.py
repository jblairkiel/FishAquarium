import random as rd  
from typing import Tuple
import pygame
class Food():

    def __init__(self, x=0, y=0):
        self.uid = rd.randint(0,63000)
        #print("Food uid is: " + str(self.uid))
        self.acquariumType = "Food"
        self.x = x
        self.y = y
        self.radius = 10
        self.nutrition = 25 
        self.hitbox = (self.x, self.y, self.radius, self.radius) #

        
    def __str__(self):
        return str(self.uid)
    def __repr__(self):
        return str(self)

    def draw(self, screen)-> Tuple[int, int, int]:
        self.hitbox = (self.x, self.y, self.radius, self.radius) #
        return (self.x, self.y, self.radius)
        #
