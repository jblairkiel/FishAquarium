import csv
import math
from re import S
import pygame
import os
import random

class FishAquariumGame():

	def __init__(self):
		pygame.init()
		if (os.path.exists("generation.csv")):
			os.remove("generation.csv")
		self.ScreenWidth = 1400 # 1600
		self.ScreenHeight = 800 # 1000
		self.ScrCenterX = self.ScreenWidth / 2
		self.ScrCenterY = self.ScreenHeight / 2
		self.gameOver = False
		self.screen = pygame.display.set_mode((self.ScreenWidth, self.ScreenHeight))
		self.clock = pygame.time.Clock()
		self.mouseX = 0;
		self.mouseY = 0;
		self.DEBUG = False

		self.fc = FishController();
		self.Insp = Inspector();

	def start(self):
		while not self.gameOver:
			if self.DEBUG:

				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						self.gameOver = True
					if event.type == pygame.KEYDOWN:
						if event.key == pygame.K_SPACE:
							self.fc.addFish(self.mouseX, self.mouseY)
					if event.type == pygame.MOUSEBUTTONDOWN:
						if event.button == 1: #left click
							self.Insp.currentItem = self.fc.getAquariumItem(self.mouseX, self.mouseY)
						if event.button == 3: #right click
							self.fc.addFood(self.mouseX, self.mouseY)
	
					if event.type == pygame.MOUSEMOTION:
						position = event.pos
						self.mouseX = position[0]
						self.mouseY = position[1]	

			else:
							
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						self.gameOver = True
					if event.type == pygame.KEYDOWN:
						if event.key == pygame.K_SPACE:
							for i in range(0, 5):
								self.fc.addFish(random.randint(self.ScrCenterX - 200,self.ScrCenterX + 200), random.randint(self.ScrCenterY - 200,self.ScrCenterY + 200), pygame.time.get_ticks())
					if event.type == pygame.MOUSEBUTTONDOWN:
						if event.button == 1: #left click
							self.Insp.currentItem = self.fc.getAquariumItem(self.mouseX, self.mouseY)
						if event.button == 3: #right click
							for i in range(0, 50):
								self.fc.addFood(random.randint(10,self.ScreenWidth - 10), random.randint(10,self.ScreenHeight + 10))


					if event.type == pygame.MOUSEMOTION:
						position = event.pos
						self.mouseX = position[0]
						self.mouseY = position[1]	
			
			#Main Game Loop
			self.screen.fill((0,0,0))
			self.fc.lookFish(self.screen)
			self.fc.moveFish()
			#TODO determine move from matrix of vision (backpropogate to this data structure)
			self.fc.feedFish()

			#Draws
			self.fc.drawFood(self.screen)
			self.fc.drawFish(self.screen, pygame.time.get_ticks())
			self.Insp.drawPane(self.screen, self.ScreenWidth, self.ScreenHeight, self.mouseX, self.mouseY)
			
			pygame.display.flip()

			self.clock.tick(60)

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
	
	def addFish(self, x=0, y=0, clock=None):
		fish = Fish(x,y, clock);	
		self.fishInTank.append(fish);

	def getAquariumItem(self, x, y):
		chosenFish = None
		for fish in self.fishInTank:	
			#print("Fish X: " + str(fish.x) + " Fish Y: " + str(fish.y))
			#print("Mos X: " + str(x) + " Mos Y: " + str(y))
			#print("Fish X + lenX: " + str(fish.x + fish.lenX) + " Fish Y + lenY: " + str(fish.y + fish.lenY))
			fishIn = self.inFishBounds(fish, x, y)
			if(fishIn):
				print("made it here")
				chosenFish = fish
		return chosenFish 
	
	def getNearbyFish(self, screen, lookingFish, visonValueFront=None, visionValueLeft=None, visionValueRight=None):
		
		nearbyFish = []
		
		for curFish in self.fishInTank:	
			curFish.getNearbyFish(screen, self.fishInTank)
		return nearbyFish 

		

	def distance(self, fish, x, y):
		#returns distance between a fish and a point
		return math.sqrt((fish.x - x)**2 + (fish.y - y)**2)

	def inFishBounds(self, fish, x, y):
		if(fish.x < x < fish.x + fish.lenX and fish.y < y < fish.y + fish.lenY):
			print("true")
			return True;
		else:
			print("false")
			return False;

	def lookFish(self, screen):
		for fish in self.fishInTank:
			self.getNearbyFish(screen, fish)

	def drawFish(self, screen, curTicks):
		for fish in self.fishInTank:
			fish.draw(screen, curTicks);

	def moveFish(self):
		for fish in self.fishInTank:
			fish.move();

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


		if not (os.path.exists("generation.csv")):
			if (fishCount > 0) and (isAFishAlive == False):
				with open('generation.csv', 'wt', newline='') as csvfile:
					genWriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
					fishAttributes = [a for a in dir(self.fishInTank[0]) if not a.startswith('__') and not callable(getattr(self.fishInTank[0],a))]
					genWriter.writerow(fishAttributes)
					for writeFish in self.fishInTank:
						writeFish.writeCSVFish(genWriter)
						writeFish.alive = False
		
		

class Food():

	def __init__(self, x=0, y=0):
		self.uid = random.randint(0,63000)
		print("Food uid is: " + str(self.uid))
		self.x = x
		self.y = y
		self.radius = 5
		self.nutrition = 25 
		self.hitbox = (self.x, self.y, self.radius, self.radius) #
		
	def draw(self, screen):
		self.hitbox = (self.x, self.y, self.radius, self.radius) #
		pygame.draw.circle(screen,(100, 255, 0), (self.x, self.y), self.radius * 2);

class Fish():

	def __init__(self, x=0, y=0, clock=None):
		self.uid = random.randint(0,63000)
		#print("Fish uid is: " + str(self.uid))
		self.x = x	
		self.y = y
		self.lenX = 60
		self.lenY = 60
		self.Health = 100
		self.deathNum = 15000 #should be variable rate later
		self.birth = clock
		self.visionValueFront = 20
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

	def writeCSVFish(self, csvWriter):
		fishAttributes = [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self,a))]
		fishVals = []
		for attr in fishAttributes:
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

	def draw(self,screen, curTicks):
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
		pygame.draw.rect(screen, pygame.Color(55, 55, 55, a=220 ), pygame.Rect(self.lookingBounds[0], self.lookingBounds[1], self.lenX + (2*self.visionValueFront), self.lenY + (2*self.visionValueFront)))

		#Fish
		pygame.draw.rect(screen, self.color, pygame.Rect(self.x, self.y, self.lenX, self.lenY))

	def move(self):
		if self.alive:
			boundX1 = 0
			boundX2 = 1400
			boundY1 = 0
			boundY2 = 800
			tempX = -999
			tempY = -999

			while ( boundX1 > tempX) or (tempX > boundX2 ):
				dx = random.randint(-2 * int(self.Health / 100), 2 * int(self.Health / 100));
				tempX = self.x + dx;

			while ( (boundY1 > tempY) or (tempY > boundY2)):
				dy = random.randint(-2 * int(self.Health / 100), 2 * int(self.Health / 100));
				tempY = self.y + dy

			self.x = tempX
			self.y = tempY

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
					

game = FishAquariumGame();
game.start();
