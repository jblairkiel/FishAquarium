from src.fish import Fish
from src.food import Food
import csv
from graphics.Colors import Colors
import numpy as np
import math
import pygame as pg


class FishController:
    def __init__(self):
        self.fishInTank = []
        self.fishFood = []
        self.defaultVisionValueFront = 20  # pixels square
        self.defaultVisionValueLeft = 10  # pixels square
        self.defaultVisionValueRight = 10  # pixels square

    def addFood(self, x=0, y=0):
        food = Food(x, y)
        self.fishFood.append(food)

    def drawFood(self, pg: pg, screen):
        for food in self.fishFood:
            food_x, food_y, food_radius = food.draw()
            pg.draw.circle(screen, (100, 255, 0), (food_x, food_y), food_radius)
            # PygameHelper.drawfood(pg, food.draw())

    def writeFishToFile(self):
        with open("generation.csv", "wt", newline="") as csvfile:
            genWriter = csv.writer(
                csvfile, delimiter="\t", quotechar="|", quoting=csv.QUOTE_MINIMAL
            )
            fishAttributes = [
                a
                for a in dir(self.fishInTank[0])
                if not a.startswith("__")
                and not callable(getattr(self.fishInTank[0], a))
            ]

            # UID as Primary Key
            fishAttributes.insert(0, "uid")
            genWriter.writerow(fishAttributes)
            for writeFish in self.fishInTank:
                writeFish.writeCSVFish(genWriter)

    def writeActionsToFile(self, actionList):
        with open("actions.csv", "wt", newline="") as csvfile:
            actionWriter = csv.writer(
                csvfile, delimiter="\t", quotechar="|", quoting=csv.QUOTE_MINIMAL
            )
            actionWriter.writerow(["Gen", "Fish X", "Fish Y", "Dx", "Dy", "Action"])
            for action in actionList:
                actionWriter.writerow(action)

    def killAll(self):
        # Remove the dead
        tempFishTank = []
        for fish in self.fishInTank:
            if fish.alive:
                tempFishTank.append(fish)
            else:
                del fish
        self.fishInTank = tempFishTank

    def killAll(self):
        # Remove the dead
        tempFishTank = []
        for fish in self.fishInTank:
            if fish.alive:
                tempFishTank.append(fish)
            else:
                del fish
        self.fishInTank = tempFishTank

    def reproduceAll(self, clock):
        newTank = []
        self.fishInTank.sort(key=lambda x: x.Health, reverse=True)
        # Take %50
        for i in range(0, len(self.fishInTank)):
            prevFish = self.fishInTank[i]
            newFish = prevFish.reproduce(clock)
            # newFish #Attributes.
            newTank.append(newFish)
        self.killAll()
        self.fishInTank = newTank

    def insertFish(self, fish):
        if fish != None:
            self.fishInTank.append(fish)

    def addFish(self, x=0, y=0, clock=None):
        fish = Fish(x, y, clock)
        self.insertFish(fish)

    def getAquariumItem(self, x, y):
        chosenFish = None
        for fish in self.fishInTank:
            # print("Fish X: " + str(fish.x) + " Fish Y: " + str(fish.y))
            # print("Mos X: " + str(x) + " Mos Y: " + str(y))
            # print("Fish X + lenX: " + str(fish.x + fish.lenX) + " Fish Y + lenY: " + str(fish.y + fish.lenY))
            fishIn = self.inFishBounds(fish, x, y)
            if fishIn:
                chosenFish = fish
        return chosenFish

    def getNearbyFish(
        self,
        screen,
        lookingFish,
        visonValueFront=None,
        visionValueLeft=None,
        visionValueRight=None,
    ):
        nearbyFish = []

        for curFish in self.fishInTank:
            curFish.getNearbyFish(screen, self.fishInTank)
        return nearbyFish

    def distance(self, fish, x, y):
        # returns distance between a fish and a point
        return math.sqrt((fish.x - x) ** 2 + (fish.y - y) ** 2)

    def inFishBounds(self, fish, x, y):
        if fish.x < x < fish.x + fish.lenX and fish.y < y < fish.y + fish.lenY:
            return True
        else:
            return False

    def lookFish(self, screen):
        observationBefore = []
        for thisFish in self.fishInTank:
            self.getNearbyFish(screen, thisFish)
            # Get Objects in vision
            # Should investigate Speeding up
            # thisFish.objectsInVision = []
            thisFish.fishInVision = []
            thisFish.foodInVision = []
            for food in self.fishFood:
                thisFish.checkAndAddIfIsInVision(food)
            for otherFish in self.fishInTank:
                if otherFish != thisFish:
                    thisFish.checkAndAddIfIsInVision(otherFish)

            # Oberservation
            observationBefore = thisFish.generateObservation()
        return observationBefore

    def get_drawFish(self, pg: pg, screen, curTicks):
        for fish in self.fishInTank:
            x, y, px, py = fish.draw(screen, curTicks)
            pg.draw.rect(screen, Colors.FISHCOLOR, x, y, px, py)

    def moveFish(self, dxdyAction=None):
        observationBefore = []
        for thisFish in self.fishInTank:
            action = thisFish.move(dxdyAction)
            observationBefore = np.append([action[0]], observationBefore)
            observationBefore = np.append([action[1]], observationBefore)
            observationBefore = np.append([action[2]], observationBefore)
        return observationBefore

    def feedFish(self):
        isAFishAlive = None
        fishCount = 0
        for fish in self.fishInTank:
            fishCount = fishCount + 1
            if fish.alive:
                isAFishAlive = True
                eatenFoodIDs = fish.eat(self.fishFood)
                self.eatenFood = [x for x in self.fishFood if x.uid in eatenFoodIDs]
                self.fishFood = [x for x in self.fishFood if x.uid not in eatenFoodIDs]
                for food in self.eatenFood:
                    del food
        if (fishCount > 0) and (isAFishAlive == None):
            isAFishAlive = False
        return len(self.eatenFood) > 0

    def isAllFishDead(self):
        boolAllDead = True
        for fish in self.fishInTank:
            if fish.alive:
                boolAllDead = False
        return boolAllDead

        # if not (os.path.exists("generation.csv")):
        # 	if (fishCount > 0) and (isAFishAlive == False):
        # 		with open('generation.csv', 'wt', newline='') as csvfile:
        # 			genWriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        # 			fishAttributes = [a for a in dir(self.fishInTank[0]) if not a.startswith('__') and not callable(getattr(self.fishInTank[0],a))]
        # 			genWriter.writerow(fishAttributes)
        # 			for writeFish in self.fishInTank:
        # 				writeFish.writeCSVFish(genWriter)
        # 				writeFish.alive = False
