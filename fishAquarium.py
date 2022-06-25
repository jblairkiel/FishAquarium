from ast import alias
import csv
import math
from re import S
import pygame
import os
import random
from copy import deepcopy
import numpy as np
import tflearn
import math
from tflearn.layers.core import input_data, fully_connected
from tflearn.layers.estimator import regression
import time

class FishAquariumTrainer():

	def __init__(self):
		self.fishNNDataFile = "fish_nn.tflearn"
		self.nn_model = self.model()
		self.ScreenWidth = 1400 # 1600
		self.ScreenHeight = 800 # 1000
		self.ScrCenterX = self.ScreenWidth / 2
		self.ScrCenterY = self.ScreenHeight / 2
		self.gameOver = False
		self.clock = time.perf_counter() #TODO Something here
		self.mouseX = 0
		self.mouseY = 0
		self.DEBUG = False
		self.timeToSpeedUp = 100

		self.fc = FishController()
		self.Insp = Inspector()

	def getCustomTimeTicks(self):
		return time.perf_counter()

	def train(self):
			if (os.path.exists("generation.csv")):
				os.remove("generation.csv")

			for i in range(0, 150):
				self.fc.addFood(random.randint(10,self.ScreenWidth - 10), random.randint(10,self.ScreenHeight + 10))

			numTimesToSimulate = 100
			trainingData = []
			allActions = []
			for i in range(0, numTimesToSimulate):
				self.fc.addFish(random.randint(10,self.ScreenWidth - 10), random.randint(10,self.ScreenHeight + 10), self.getCustomTimeTicks(), self.timeToSpeedUp)
				elapsedTime = 0
				for j in range(0, 10):
					self.fc.addFood(random.randint(10,self.ScreenWidth - 10), random.randint(10,self.ScreenHeight + 10))
				startTime = self.getCustomTimeTicks()
				while not self.fc.isAllFishDead():

    				#Sleep to get simmed time
					time.sleep(.3/self.timeToSpeedUp)
					#print(str(self.getCustomTimeTicks() - startTime))
					#sleep(60 - time() % 60)
				

					#Main Game Loop
					curTrainingData = self.fc.lookFish()
					action = self.fc.moveFish(None, self.getCustomTimeTicks())
					curTrainingData = np.append([action[2]], curTrainingData)
					curTrainingData = np.append([action[1]], curTrainingData)
					didFishFeed = self.fc.feedFish()
					didFishMoveCloserToFood = int(action[0])
					
					actionValue = -1
					if didFishMoveCloserToFood:
						if didFishFeed: 
							actionValue = 5
						else:
							actionValue = 3

					#TODO determine move from matrix of vision (backpropogate to this data structure)
					trainingToAdd = [curTrainingData, int(actionValue)]
					trainingData.append(trainingToAdd)
					allActions.append([i, curTrainingData[-1], curTrainingData[-2], action[2], action[1], actionValue])
					
					elapsedTime += self.getCustomTimeTicks()
					if elapsedTime > 5000:
						#print(trainingToAdd)
						elapsedTime = 0 
					
					#curTrainingData = np.append([trainingData], curTrainingData)

				self.fc.writeFishToFile()
				self.fc.writeActionsToFile(allActions)
				#print(trainingData)
				self.fc.fishInTank[0].alive = True
				self.fc.reproduceAll(self.getCustomTimeTicks())
				self.fc.fishInTank.pop(0)
				try:
					self.nn_model = self.train_model(trainingData, self.nn_model)
				except:
					[print(i) for i in trainingData if len(i[0]) != 7]
				
			#self.test_model(self.nn_model)
	def model(self):
		network = input_data(shape=[None, 7, 1], name='input')
		network = fully_connected(network, 20, activation='relu')
		network = fully_connected(network, 1, activation='linear')
		network = regression(network, optimizer='adam', learning_rate=1e-2, loss='mean_square', name='target')
		model = tflearn.DNN(network) #, tensorboard_dir='log')
		return model

	def train_model(self, training_data, model):
		X = np.array([i[0] for i in training_data]).reshape(-1, 7, 1)
		y = np.array([i[1] for i in training_data]).reshape(-1, 1)
		model.fit(X,y, n_epoch = 1, shuffle = True, run_id = self.fishNNDataFile)	
		model.save(self.fishNNDataFile)
		return model

class FishAquariumGame():

	def __init__(self):
		pygame.init()
		self.fishNNDataFile = "fish_nn.tflearn"
		self.nn_model = self.model()
		self.ScreenWidth = 1400 # 1600
		self.ScreenHeight = 800 # 1000
		self.ScrCenterX = self.ScreenWidth / 2
		self.ScrCenterY = self.ScreenHeight / 2
		self.gameOver = False
		self.screen = pygame.display.set_mode((self.ScreenWidth, self.ScreenHeight))
		self.clock = pygame.time.Clock()
		self.mouseX = 0
		self.mouseY = 0

		self.fc = FishController()
		self.Insp = Inspector()

	def start(self):

		if (os.path.exists("fishNNDataFile.tflearn")):
			#os.remove("fishNNDataFile.tflearn")
			self.nn_model.load(self.filename)


			if (os.path.exists("generation.csv")):
				os.remove("generation.csv")

			for i in range(0, 150):
				self.fc.addFood(random.randint(10,self.ScreenWidth - 10), random.randint(10,self.ScreenHeight + 10))
			self.fc.addFish(random.randint(10,self.ScreenWidth - 10), random.randint(10,self.ScreenHeight + 10), pygame.time.get_ticks())

			while not self.gameOver:
				trainingData = []
				predictions = []

				elapsedTime = 0
				while not self.fc.isAllFishDead():
					for event in pygame.event.get():
						if event.type == pygame.QUIT:
							self.gameOver = True
				
					#Main Game Loop
					self.screen.fill((0,0,0))
					curTrainingData = self.fc.lookFish()

					#predict action
					actions = []
					predictedActions = []
					for i in range(0, 4):
						tempTrainingData = curTrainingData
						tempAction = self.fc.fishInTank[0].generateMove()
						tempTrainingData = np.append([tempAction[0]], tempTrainingData)
						tempTrainingData = np.append([tempAction[1]], tempTrainingData)
						#tempTrainingData = np.append([tempAction[2]], tempTrainingData)
						actions.append([tempAction[0], tempAction[1]])
						tempTrainingData = np.reshape([tempTrainingData], (-1, 7, 1))
						#tempTrainingData = np.expand_dims(tempTrainingData,axis=-1)
						predictedAction = self.nn_model.predict(tempTrainingData)
						predictedActions.append(predictedAction)
					curAction = np.argmax(np.array(predictedActions))
					actionDx = actions[curAction][0]
					actionDy = actions[curAction][1]
					print("CurAction Index: " + str(curAction) )
					print("Actions: " + str(actions[curAction]))

					currentMove = self.fc.moveFish([actionDx, actionDy], pygame.time.get_ticks())
					didFishFeed = self.fc.feedFish()
					didFishMoveCloserToFood = int(currentMove[0]) #This is the resultingAction needs real variable
					
					actionValue = -1
					if didFishMoveCloserToFood:
						if didFishFeed: 
							actionValue = 2
						else:
							actionValue = 1

					trainingToAdd = [curTrainingData, actionValue]
					trainingData.append(trainingToAdd)

					elapsedTime += pygame.time.get_ticks()
					if elapsedTime > 5000:
						#print(trainingToAdd)
						elapsedTime = 0 
					
					#curTrainingData = np.append([trainingData], curTrainingData)

					#Draws
					self.fc.drawFood(self.screen)
					self.fc.drawFish(self.screen, pygame.time.get_ticks())
					self.Insp.drawPane(self.screen, self.ScreenWidth, self.ScreenHeight, self.mouseX, self.mouseY)
					
					pygame.display.flip()

					self.clock.tick(120)
	
	def model(self):
		network = input_data(shape=[None, 7, 1], name='input')
		network = fully_connected(network, 20, activation='relu')
		network = fully_connected(network, 1, activation='linear')
		network = regression(network, optimizer='adam', learning_rate=1e-2, loss='mean_square', name='target')
		model = tflearn.DNN(network) #, tensorboard_dir='log')
		return model

	def train_model(self, training_data, model):
		X = np.array([i[0] for i in training_data]).reshape(-1, 7, 1)
		y = np.array([i[1] for i in training_data]).reshape(-1, 1)
		model.fit(X,y, n_epoch = 1, shuffle = True, run_id = self.fishNNDataFile)	
		model.save(self.fishNNDataFile)
		return model

class Inspector():

	def __init__(self):
		self.currentItem = None

	def drawPane(self, screen, gameWidth, gameHeight, mosX, mosY):

		if (self.currentItem != None):
			#Draw Pane
			pygame.draw.rect(screen, (40, 40, 40), pygame.Rect(gameWidth - 300, 0, 300, gameHeight))

			#Type Mouse Cursor Pos Bottom
			fontSize = 20
			font = pygame.font.SysFont("comicsansms",fontSize)
			mouseText = font.render("X: " + str(mosX) + " Y: " + str(mosY), True, (120, 50, 20))
			screen.blit(mouseText, (gameWidth - 250, gameHeight - 50))	

			drawingYIter = 60
			if self.currentItem != None:
				#Draw Fish at top
				pygame.draw.rect(screen, self.currentItem.color, pygame.Rect(gameWidth - 150, drawingYIter, self.currentItem.lenX, self.currentItem.lenY))
				drawingYIter+=self.currentItem.lenY + 10
			
		
				#Label Descriptions
				fishAttributes = [a for a in dir(self.currentItem) if not a.startswith('__') and not callable(getattr(self.currentItem,a))]
				for attr in fishAttributes:
					drawingYIter += 10 + fontSize
					val = getattr(self.currentItem, attr)
					attrText = font.render(attr + ": " + str(val), True, (120, 50, 20))
					screen.blit(attrText, (gameWidth - 225, drawingYIter))	

class FishController():

	def __init__(self):
		self.fishInTank = []
		self.fishFood = []
		self.defaultVisionValueFront = 20 #pixels square
		self.defaultVisionValueLeft = 10 #pixels square
		self.defaultVisionValueRight = 10 #pixels square

	def addFood(self, x=0, y=0):
		food = Food(x,y)
		self.fishFood.append(food);	

	def drawFood(self, screen):
		for food in self.fishFood:
			food.draw(screen)

	def writeFishToFile(self):
	
			
		with open('generation.csv', 'wt', newline='') as csvfile:
			genWriter = csv.writer(csvfile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
			fishAttributes = [a for a in dir(self.fishInTank[0]) if not a.startswith('__') and not callable(getattr(self.fishInTank[0],a))]
			
			#UID as Primary Key
			fishAttributes.insert(0, "uid")
			genWriter.writerow(fishAttributes)
			for writeFish in self.fishInTank:
				writeFish.writeCSVFish(genWriter)

	def writeActionsToFile(self, actionList):
		with open('actions.csv', 'wt', newline='') as csvfile:
			actionWriter = csv.writer(csvfile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
			actionWriter.writerow(["Gen", "Fish X", "Fish Y", "Dx", "Dy", 'Action'])
			for action in actionList:
				actionWriter.writerow(action)

	def killAll(self):
		#Remove the dead
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
		#Take %50
		for i in range(0, len(self.fishInTank)):
			prevFish = self.fishInTank[i]
			newFish = prevFish.reproduce(clock) 
			#newFish #Attributes.
			newTank.append(newFish)
		self.killAll()
		self.fishInTank = newTank
		

	def insertFish(self, fish):
		if (fish != None):
			self.fishInTank.append(fish);
			
	
	def addFish(self, x=0, y=0, clock=None, timeToSpeedUp=None):
		fish = Fish(x,y, clock, timeToSpeedUp);
		self.insertFish(fish)	

	def getAquariumItem(self, x, y):
		chosenFish = None
		for fish in self.fishInTank:	
			#print("Fish X: " + str(fish.x) + " Fish Y: " + str(fish.y))
			#print("Mos X: " + str(x) + " Mos Y: " + str(y))
			#print("Fish X + lenX: " + str(fish.x + fish.lenX) + " Fish Y + lenY: " + str(fish.y + fish.lenY))
			fishIn = self.inFishBounds(fish, x, y)
			if(fishIn):
				chosenFish = fish
		return chosenFish 
	
	def getNearbyFish(self, lookingFish, visonValueFront=None, visionValueLeft=None, visionValueRight=None):
		
		nearbyFish = []
		
		for curFish in self.fishInTank:	
			curFish.getNearbyFish(self.fishInTank)
		return nearbyFish 

		

	def distance(self, fish, x, y):
		#returns distance between a fish and a point
		return math.sqrt((fish.x - x)**2 + (fish.y - y)**2)

	def inFishBounds(self, fish, x, y):
		if(fish.x < x < fish.x + fish.lenX and fish.y < y < fish.y + fish.lenY):
			return True;
		else:
			return False;

	def lookFish(self):
		observationBefore = []
		for thisFish in self.fishInTank:
			self.getNearbyFish( thisFish)
			#Get Objects in vision
			# Should investigate Speeding up
			#thisFish.objectsInVision = []
			thisFish.fishInVision = []
			thisFish.foodInVision = []
			for food in self.fishFood:
				thisFish.checkAndAddIfIsInVision(food)
			for otherFish in self.fishInTank:
				if (otherFish != thisFish):
					thisFish.checkAndAddIfIsInVision(otherFish)
		
			#Oberservation
			observationBefore = thisFish.generateObservation()
		return observationBefore

	def drawFish(self, screen, curTicks):
		for fish in self.fishInTank:
			fish.draw(screen, curTicks)


	def moveFish(self, dxdyAction=None, injectedCurTicks=None):
		observationBefore = []
		for thisFish in self.fishInTank:
			action = thisFish.move(dxdyAction, injectedCurTicks)
			observationBefore = np.append([ action[0]], observationBefore)
			observationBefore = np.append([ action[1]], observationBefore) 
			observationBefore = np.append([ action[2]], observationBefore) 
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
		
		

class Food():

	def __init__(self, x=0, y=0):
		self.uid = random.randint(0,63000)
		#print("Food uid is: " + str(self.uid))
		self.acquariumType = "Food"
		self.x = x
		self.y = y
		self.radius = 5
		self.nutrition = 25 
		self.hitbox = (self.x, self.y, self.radius, self.radius) #
		
	def __str__(self):
		return str(self.uid)
	def __repr__(self):
		return str(self)

	def draw(self, screen):
		self.hitbox = (self.x, self.y, self.radius, self.radius) #
		pygame.draw.circle(screen,(100, 255, 0), (self.x, self.y), self.radius * 2);

class Fish():

	def __init__(self, x=0, y=0, clock=None, timeToSpeedUp=None):
		self.uid = random.randint(0,63000)
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
		if timeToSpeedUp != None:
			self.deathNum = 15000/(timeToSpeedUp/10)
		else:
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
		self.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
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
		childFish.uid = random.randint(0,63000)
		childFish.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
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

	def getNearbyFish(self,  allFish, visonValueFront=None, visionValueLeft=None, visionValueRight=None):
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

	def draw(self,screen, curTicks):
		self.hitbox = (self.x, self.y, self.lenX, self.lenY) #
		self.lookingBounds = (self.x - self.visionValueFront, 
			self.y - self.visionValueFront,
			self.x + self.lenX + self.visionValueFront, 
			self.y + self.lenY + self.visionValueFront)
		
		#Fish vision
		if (self.showVision):
			pygame.draw.rect(screen, pygame.Color(55, 55, 55, a=220 ), pygame.Rect(self.lookingBounds[0], self.lookingBounds[1], self.lenX + (2*self.visionValueFront), self.lenY + (2*self.visionValueFront)))

		#Fish
		pygame.draw.rect(screen, self.color, pygame.Rect(self.x, self.y, self.lenX, self.lenY))

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

			xCounter = 0
			while ( boundX1 > tempX) or (tempX > boundX2 ):
				dx = random.randint((0-self.moveSpeed) * int(self.Health / 100), self.moveSpeed * int(self.Health / 100));
				tempX = self.x + dx;
				xCounter = xCounter + 1
				if xCounter > 10:
					print("Problem Solving x")

			yCounter = 0
			while ( (boundY1 > tempY) or (tempY > boundY2)):
				dy = random.randint((0-self.moveSpeed) * int(self.Health / 100), self.moveSpeed * int(self.Health / 100));
				tempY = self.y + dy
				yCounter = yCounter + 1
				if yCounter > 10:
					print("Problem Solving y")
		
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

	def move(self, dxdyAction=None, injectedAge=None):
		if injectedAge == None:
			if self.alive:
				self.age = time.perf_counter() - self.birth
				if (self.age > self.deathNum):
					self.alive = False
		else:
			if self.alive:
				self.age = (injectedAge - self.birth) * 1000
				if (self.age > self.deathNum):
					self.alive = False


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
		
debug = True			
if debug:
	fishTraining = FishAquariumTrainer()
	fishTraining.train()
else:
	game = FishAquariumGame()
	game.start()
