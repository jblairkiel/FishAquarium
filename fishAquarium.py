import pickle
import pygame
import random
import argparse

class FishAquariumGame():

	def __init__(self):
		pygame.init()
		self.ScreenWidth = 1600
		self.ScreenHeight = 1000
		self.ScrCenterX = self.ScreenWidth / 2
		self.ScrCenterY = self.ScreenHeight / 2
		self.gameOver = False
		self.clock = pygame.time.Clock()
		self.mouseX = 0;
		self.mouseY = 0;
		self.paused = False

		self.fc = FishController();
		self.Insp = Inspector();

	def load(self, filename):
		self.simName = filename[:-4]

		with open(filename, 'rb') as f:
			fish, food = pickle.load(f)
		self.fc.fishFood = food
		self.fc.fishInTank = fish

	def save(self, filename):
		with open(filename + ".dat", 'wb') as f:
    			pickle.dump([self.fc.fishInTank, self.fc.fishFood], f, protocol=2)

	def start(self):
		self.screen = pygame.display.set_mode((self.ScreenWidth, self.ScreenHeight))
		while not self.gameOver:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.gameOver = True
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_SPACE:
						self.fc.addFish(random.randint(self.ScrCenterX - 200,self.ScrCenterX + 200), random.randint(self.ScrCenterY - 200,self.ScrCenterY + 200))
				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 1: #left click
						#Dangling code from Inspector pane class
						if( self.ScreenWidth - 280 < self.mouseX < self.ScreenWidth -280 + 70 and self.ScreenHeight - 60 < self.mouseY < self.ScreenHeight- 60 + 25):
							self.save(self.simName)	
						elif( self.ScreenWidth - 200 < self.mouseX < self.ScreenWidth -200 + 80 and self.ScreenHeight - 60 < self.mouseY < self.ScreenHeight- 60 + 25):
							self.paused = not self.paused 
						if( self.ScreenWidth - 100 < self.mouseX < self.ScreenWidth - 100 + 80 and self.ScreenHeight - 60 < self.mouseY < self.ScreenHeight- 60 + 25):
							self.fc.printCurrentHighScores();
						else: 
							self.Insp.currentItem = self.fc.getAquariumItem(self.mouseX, self.mouseY)

					if event.button == 3: #right click
						for i in range(0, 50):
							self.fc.addFood(random.randint(10,self.ScreenWidth - 300 - 10), random.randint(10,self.ScreenHeight + 10))

				if event.type == pygame.MOUSEMOTION:
					position = event.pos
					self.mouseX = position[0]
					self.mouseY = position[1]	
			
			#Main Game Loop
			self.screen.fill((0,0,0))
			if not self.paused:
				self.fc.moveFish(self.ScreenWidth, self.ScreenHeight)
				self.fc.feedFish()

			#Draws
			self.fc.drawFood(self.screen)
			self.fc.drawFish(self.screen)
			self.Insp.drawPane(self.screen, self.ScreenWidth, self.ScreenHeight, self.mouseX, self.mouseY, self.paused)
			
			pygame.display.flip()
			self.clock.tick(60)

class Inspector():

	def __init__(self):
		self.currentItem = None

	def drawPane(self, screen, gameWidth, gameHeight, mosX, mosY, isPaused):
		#Draw Pane
		pygame.draw.rect(screen, (40, 40, 40), pygame.Rect(gameWidth - 300, 0, 300, gameHeight))

		#Type Mouse Cursor Pos Bottom
		fontSize = 30
		font = pygame.font.SysFont("comicsansms",fontSize)
		mouseText = font.render("X: " + str(mosX) + " Y: " + str(mosY), True, (120, 50, 20))
		screen.blit(mouseText, (gameWidth - 290, gameHeight - 25))	
			
		#Draw Save button
		saveText = font.render("Save", True, (50, 50, 50))
		if( gameWidth - 280 < mosX < gameWidth -280 + 70 and gameHeight - 60 < mosY < gameHeight - 60 + 25):
			pygame.draw.rect(screen, (70, 70, 230),(gameWidth - 280,gameHeight - 60,70,25))
		else: 
			pygame.draw.rect(screen, (100, 100, 200),(gameWidth - 280,gameHeight - 60,70,25))
		screen.blit(saveText, (gameWidth - 270, gameHeight - 55))	
		
		#Draw Pause/Play button
		if(isPaused):
			saveText = font.render("Play", True, (50, 50, 50))
		else:
			saveText = font.render("Pause", True, (50, 50, 50))
	
		if( gameWidth - 200 < mosX < gameWidth -200 + 80 and gameHeight - 60 < mosY < gameHeight - 60 + 25):
			pygame.draw.rect(screen, (70, 70, 230),(gameWidth - 200,gameHeight - 60,80,25))
		else: 
			pygame.draw.rect(screen, (100, 100, 200),(gameWidth - 200,gameHeight - 60,80,25))
		screen.blit(saveText, (gameWidth - 190, gameHeight - 55))	

		#Draw HighScore Button
		highScoreText = font.render("Hi Scores", True, (50, 50, 50))
	
		if( gameWidth - 100 < mosX < gameWidth - 100 + 80 and gameHeight - 60 < mosY < gameHeight - 60 + 25):
			pygame.draw.rect(screen, (70, 70, 230),(gameWidth - 100,gameHeight - 60,80,25))
		else: 
			pygame.draw.rect(screen, (100, 100, 200),(gameWidth - 100,gameHeight - 60,80,25))
		screen.blit(highScoreText, (gameWidth - 90, gameHeight - 55))	


		

		drawingYIter = 60
		if self.currentItem != None:
			#Draw Fish at top
			pygame.draw.rect(screen, self.currentItem.color, pygame.Rect(gameWidth - 200, drawingYIter, self.currentItem.lenX, self.currentItem.lenY))
			drawingYIter+=self.currentItem.lenY + 10
		
	
			#Label Descriptions
			fishAttributes = [a for a in dir(self.currentItem) if not a.startswith('__') and not callable(getattr(self.currentItem,a))]
			for attr in fishAttributes:
				drawingYIter += 10 + fontSize
				val = getattr(self.currentItem, attr)
				attrText = font.render(attr + ": " + str(val), True, (120, 50, 20))
				screen.blit(attrText, (gameWidth - 255, drawingYIter))	

class FishController():

	def __init__(self):
		self.fishInTank = []
		self.fishFood = []

	def addFood(self, x=0, y=0):
		food = Food(x,y)
		self.fishFood.append(food);	

	def drawFood(self, screen):
		for food in self.fishFood:
			food.draw(screen)
	
	def addFish(self, x=0, y=0):
		fish = Fish(x,y);	
		self.fishInTank.append(fish);

	def getAquariumItem(self, x, y):
		chosenFish = None
		for fish in self.fishInTank:	
			fishIn = self.inFishBounds(fish, x, y)
			if(fishIn):
				chosenFish = fish
		
		return chosenFish 
	
	def printCurrentHighScores(self):
		fishScores = self.fishInTank
		fishScores.sort(key=lambda x: x.Health, reverse=True)
		
		print("-------High Scores-------")
		for fish in fishScores:
			print(str(fish.uid) + ": " + str(fish.Health))
			
		

	def distance(self, fish, x, y):
		#returns distance between a fish and a point
		return math.sqrt((fish.x - x)**2 + (fishy - y)**2)

	def inFishBounds(self, fish, x, y):
		if(fish.x < x < fish.x + fish.lenX and fish.y < y < fish.y + fish.lenY):
			return True;
		else:
			return False;

	def drawFish(self, screen):
		for fish in self.fishInTank:
			fish.draw(screen);

	def moveFish(self, screenWidth, screenHeight):
		for fish in self.fishInTank:
			fish.move(screenWidth, screenHeight);

	def feedFish(self):
		for fish in self.fishInTank:
			eatenFoodIDs = fish.eat(self.fishFood)
			self.eatenFood = [x for x in self.fishFood if x.uid in eatenFoodIDs]
			self.fishFood = [x for x in self.fishFood if x.uid not in eatenFoodIDs]
			for food in self.eatenFood:
				del food
		

class Food():

	def __init__(self, x=0, y=0):
		self.uid = random.randint(0,63000)
		self.x = x
		self.y = y
		self.radius = 3
		self.nutrition = 25 

	def __str__(self):
		foodAttributes = [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self,a))]
		attrText = 'Food: ( '
		for attr in foodAttributes: 
			val = getattr(self, attr)
			attrText += attr + ": " + str(val) + ", "
		attrText += " ) " 
		return attrText
		
		
	def draw(self, screen):
		pygame.draw.circle(screen,(100, 255, 0), (self.x, self.y), self.radius * 2);

class Fish():

	def __init__(self, x=0, y=0):
		self.uid = random.randint(0,63000)
		self.x = x	
		self.y = y
		self.lenX = 30
		self.lenY = 30
		self.Generation = 1
		self.Sight = 20
		self.Health = 100
		self.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
	
	def draw(self,screen):
		pygame.draw.rect(screen, self.color, pygame.Rect(self.x, self.y, self.lenX, self.lenY))

	def move(self, screenWidth, screenHeight):
		#Find Nearby Food

		#Run X,Y and nearby items to food

	#	dx = random.randint(-2 * int(self.Health / 100), 2 * int(self.Health / 100));
	#	dy = random.randint(-2 * int(self.Health / 100), 2 * int(self.Health / 100));
		dx = max(min(10,(random.randint(-2, 2) * int(self.Health / 100))),-10) ;
		dy = max(min(10,(random.randint(-2, 2) * int(self.Health / 100))),-10) ;
		#Make sure it is within the bounds of the screeen
		if(0 > self.x + dx ):
			self.x += 2
		elif( self.x + dx + self.lenX > screenWidth - 300):
			self.x -= 2	
		else:
			self.x = self.x + dx;

		if(0 > self.y + dy):
			self.y += 2
		elif( self.y + dy + self.lenY > screenHeight):
			self.y -= 2
		else:
			self.y = self.y + dy

	def eat(self, food):
	
		#returns eaten food
		foodToEatIDs = []
		for foo in food:	
			#Food is within box
			#if (self.x < foo.x < self.x + self.lenX) and (self.y < foo.y < self.y + self.lenY):
			if( 
				((self.x < foo.x - foo.radius < self.x + self.lenX) and (self.y < foo.y - foo.radius < self.y + self.lenY)) or 
				((self.x < foo.x - foo.radius < self.x + self.lenX) and (self.y < foo.y + foo.radius < self.y + self.lenY)) or 
				((self.x < foo.x + foo.radius < self.x + self.lenX) and (self.y < foo.y - foo.radius < self.y + self.lenY)) or 
				((self.x < foo.x + foo.radius < self.x + self.lenX) and (self.y < foo.y + foo.radius < self.y + self.lenY))
			):
				self.Health = self.Health + foo.nutrition;
				foodToEatIDs.append(foo.uid)		
		return foodToEatIDs
			
parser = argparse.ArgumentParser(description="Fish Aquarium Simulation")
parser.add_argument("filename", nargs="?", help="Load a saved aquarium")
args = parser.parse_args()

game = FishAquariumGame();
if(args.filename):
	print(args.filename)
	game.load(args.filename)
else:
	fileName = input("Enter the Name for this Fish Simulation: ")
	game.simName = fileName
	
game.start();

