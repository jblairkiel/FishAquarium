from copy import deepcopy
import math
import random as rd
import numpy as np
from typing import Tuple
class Fish():

    def __init__(self, x=0, y=0, clock=None):
        self.uid = rd.randint(0,63000)
        #print("Fish uid is: " + str(self.uid))
        self.acquariumType = "Fish"
        self.x = x	
        self.y = y
        self.ancestors = []
        self.parent = None
        self.generation = 1
        self.lenX = 60
        self.lenY = 60
        self.moveSpeed = 3
        self.distanceToClosestFood = 999999
        self.lastDistanceToClosestFood = 999999
        self.Health = 100
        self.deathNum = 15000 #should be variable rate later
        self.birth = clock
        self.showVision = True
        #self.objectsInVision = []
        self.fishInVision = []
        self.foodInVision = []
        self.visionValueFront = 60
        self.visionValueLeft = 10
        self.visionValueRight = 10
        self.hitbox = (self.x, self.y, self.lenX, self.lenY) #
        self.color = (rd.randint(0,255), rd.randint(0,255), rd.randint(0,255))
        self.lookingBounds = (self.x - self.visionValueFront, 
            self.y - self.visionValueFront,
            self.x + self.lenX + self.visionValueFront, 
            self.y + self.lenY + self.visionValueFront)
        self.age = 0
        self.alive = True

    def __str__(self):
        return str(self.uid)
    def __repr__(self):
        return str(self)

    def checkAndAddIfIsInVision(self, acquariumObject):
        #If within Bounds add to vision
        if ((acquariumObject.y < self.lookingBounds[1] + self.lookingBounds[3] and acquariumObject.y  >self.lookingBounds[1]) and # Checks x coords
            (acquariumObject.x > self.lookingBounds[0] and acquariumObject.x < self.lookingBounds[0] + self.lookingBounds[2])):  # Checks y coords
            #self.objectsInVision.append(acquariumObject)
            if (acquariumObject.acquariumType == "Food"):
                self.foodInVision.append(acquariumObject)
            elif(acquariumObject.acquariumType == "Fish"):
                self.fishInVision.append(acquariumObject)


    def reproduce(self, clock):
        #childFish = self
        childFish = deepcopy(self)


        # Mutate Function
        childFish.birth = clock
        childFish.uid = rd.randint(0,63000)
        childFish.color = (rd.randint(0,255), rd.randint(0,255), rd.randint(0,255))
        childFish.ancestors.append(self)
        childFish.generation = self.generation + 1
        childFish.parent = self
        return childFish

    def writeCSVFish(self, csvWriter):


        fishAttributes = [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self,a))]
        #Write Ancestors
        if (self.ancestors != []):
            for ancestors in self.ancestors:
                fishVals = []
                #UID as Primary Key
                fishVals.append(getattr(ancestors, "uid"))
                for attr in fishAttributes:
                    if (attr == "parent"):
                        tempParent = getattr(ancestors, attr)
                        tempParentStr = ""
                        if (tempParent != None):
                            tempParentStr = tempParent.uid
                        fishVals.append(tempParentStr)
                    elif (attr == "ancestors"):
                        fishVals.append("")
                    else:
                        fishVals.append(getattr(ancestors, attr))
                        

                #fishAttributes.insert(0, self.uid)
                csvWriter.writerow(fishVals)

        #Write Self
        fishVals = []
        #UID as Primary Key
        fishVals.append(getattr(self, "uid"))
        for attr in fishAttributes:
            if (attr == "parent"):
                tempParent = getattr(self, attr)
                tempParentStr = ""
                if (tempParent != None):
                    tempParentStr = tempParent.uid
                fishVals.append(tempParentStr)
            elif (attr == "ancestors"):
                fishVals.append("")
            else:
                fishVals.append(getattr(self, attr))

        #fishAttributes.insert(0, self.uid)
        csvWriter.writerow(fishVals)

    def getNearbyFish(self, screen, allFish, visonValueFront=None, visionValueLeft=None, visionValueRight=None):
        nearbyFish = []
        if visonValueFront is None:
            visionValueFront = self.visionValueFront
            visionValueLeft = self.visionValueLeft 
            visionValueRight = self.visionValueRight 
        for curFish in allFish:	
            if self != curFish: #Skip the fish that are "Looking"
                
                if ((curFish.y < self.lookingBounds[1] + self.lookingBounds[3] and curFish.y + curFish.lenY >self.lookingBounds[1]) and # Checks x coords
                    (curFish.x + curFish.lenX > self.lookingBounds[0] and curFish.x < self.lookingBounds[0] + self.lookingBounds[2])):  # Checks y coords
                    #print("NearbyFish: ")
                    nearbyFish.append(curFish)
        return nearbyFish 

    def get_draw(self,screen, curTicks)->Tuple[int, int, int, int]:
        if self.alive:
            self.age = curTicks - self.birth
            if (self.age > self.deathNum):
                self.alive = False


        self.hitbox = (self.x, self.y, self.lenX, self.lenY) #
        self.lookingBounds = (self.x - self.visionValueFront, 
            self.y - self.visionValueFront,
            self.x + self.lenX + self.visionValueFront, 
            self.y + self.lenY + self.visionValueFront)
        
        #Fish vision
        if (self.showVision):
            bound_x = self.lenX + (2*self.visionValueFront)
            bound_y = self.lenY + (2*self.visionValueFront)
            return self.lookingBounds[0], self.lookingBounds[1], bound_x, bound_y
            #pg.draw.rect(screen,, pg.Rect(self.lookingBounds[0], self.lookingBounds[1], self.lenX + (2*self.visionValueFront), self.lenY + (2*self.visionValueFront)))
           
        #Fish
        return self.x, self.y, self.lenX, self.lenY
        #pg.draw.rect(screen, self.color, pg.Rect(self.x, self.y, self.lenX, self.lenY))

    def generateMove(self, omitMovedCloser=False):
        
        dx = 0
        dy = 0
        if self.alive:
            boundX1 = 0
            boundX2 = 1400
            boundY1 = 0
            boundY2 = 800
            tempX = -999
            tempY = -999

            while ( boundX1 > tempX) or (tempX > boundX2 ):
                dx = rd.randint((0-self.moveSpeed) * int(self.Health / 100), self.moveSpeed * int(self.Health / 100));
                tempX = self.x + dx;

            while ( (boundY1 > tempY) or (tempY > boundY2)):
                dy = rd.randint((0-self.moveSpeed) * int(self.Health / 100), self.moveSpeed * int(self.Health / 100));
                tempY = self.y + dy
        
        #If moved closer to food
        movedCloser = 0
        if not omitMovedCloser:
            closestValues, closestIndex = self.getClosestFood(tempX, tempY)
            

            if len(closestIndex) != 0:
                self.distanceToClosestFood = closestValues[0]
                if self.distanceToClosestFood < self.lastDistanceToClosestFood:
                    movedCloser = 1
            else:
                self.distanceToClosestFood = 999999

            self.lastDistanceToClosestFood = self.distanceToClosestFood

        return [dx, dy, movedCloser]

    def move(self, dxdyAction=None):
        if (dxdyAction is not None):
            dx = dxdyAction[0] 
            dy = dxdyAction[1]
        else:
            [dx, dy, movedCloser] = self.generateMove(omitMovedCloser=True)
        
        self.x = self.x + dx
        self.y = self.y + dy

        #If moved closer to food
        closestValues, closestIndex = self.getClosestFood()
        movedCloser = 0
        if len(closestIndex) != 0:
            self.distanceToClosestFood = closestValues[0]
            if self.distanceToClosestFood < self.lastDistanceToClosestFood:
                movedCloser = 1
        else:
            self.distanceToClosestFood = 999999

        self.lastDistanceToClosestFood = self.distanceToClosestFood
        return [dx, dy, movedCloser]

    def realMove(self):
        print("Here")

    def getClosestFood(self, injectedX=None, injectedY=None):
        tempX = None
        tempY = None
        if (injectedX == None and injectedY == None):
            tempX = self.x
            tempY = self.y
        else:
            tempX = injectedX
            tempY = injectedY
        closestIndex = []
        closestValues = []
        for i in range(0, len(self.foodInVision)-1):
            distance = math.dist([tempX, tempY], [self.foodInVision[i].x, self.foodInVision[i].y])
            closestValues.append(distance)
            closestIndex.append(i)

        if closestIndex != []:
            closestValues, closestIndex = zip(*sorted(zip(closestValues, closestIndex)))
        return closestValues, closestIndex

    def generateObservation(self):

        #Target is an array of 16, 2 for the currentFishPosition, 15 for the food positions
        targetFoodSize = 1
        customLimiterSize = 2 + (3* targetFoodSize)
        isFood = 1
        isNotFood = 0
        curObservation = np.array([
                self.x,
                self.y
        ])

        # Get Closest
        if (len(self.foodInVision) != 0):
            closestIndex = []
            closestValues = []
            closestValues, closestIndex = self.getClosestFood()
            if (len(closestValues) < targetFoodSize):

                counter = 0
                for i in range(0, len(closestValues)-1):
                    #print(len(self.foodInVision))
                    #print(self.foodInVision[i])
                    curObservation = np.append(self.foodInVision[closestIndex[i]-1].x, curObservation)
                    curObservation = np.append(self.foodInVision[closestIndex[i]-1].y, curObservation)
                    curObservation = np.append([isFood], curObservation)
                    counter = counter + 1


                # Remainder
                for i in range(0, customLimiterSize - 2):
                    curObservation = np.append([isNotFood], curObservation)
            
            else:

                for i in range(0, targetFoodSize):
                    #print(len(self.foodInVision))
                    #print(self.foodInVision[i])
                    curObservation = np.append(self.foodInVision[closestIndex[i]-1].x, curObservation)
                    curObservation = np.append(self.foodInVision[closestIndex[i]-1].y, curObservation)
                    curObservation = np.append([isFood], curObservation)

        else:

            for i in range(0, (targetFoodSize*3)):
                curObservation = np.append([isNotFood], curObservation)

        return curObservation
            

    def eat(self, food):
    
        if self.alive:
            #returns eaten food
            foodToEatIDs = []
            for foo in food:	
                #Food is within box
                #if (self.x < foo.x < self.x + self.lenX) and (self.y < foo.y < self.y + self.lenY):
                # if( 
                # 	((self.x < foo.x - foo.radius < self.x + self.lenX) and (self.y < foo.y < self.y - self.lenY)) or 
                # 	((self.x < foo.x - foo.radius < self.x + self.lenX) and (self.y < foo.y < self.y + self.lenY)) or 
                # 	((self.x < foo.y + foo.radius < self.x + self.lenX) and (self.y < foo.y < self.y - self.lenY)) or 
                # 	((self.x < foo.y + foo.radius < self.x + self.lenX) and (self.y < foo.y < self.y + self.lenY))
                # ):
                #print("FOOD: x - " + str(foo.x) + "y - " str(foo.y))
                #print("Fish: x - " + str(self.x) + "y - " str(foo.y))
                if ((foo.y - foo.radius < self.hitbox[1] + self.hitbox[3] and foo.y + foo.radius > self.hitbox[1]) and # Checks x coords
                    (foo.x + foo.radius > self.hitbox[0] and foo.x - foo.radius < self.hitbox[0] + self.hitbox[2])):  # Checks y coords
                        self.Health = self.Health + foo.nutrition;
                        foodToEatIDs.append(foo.uid)		
            return foodToEatIDs
                    