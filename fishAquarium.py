import pygame
import random

class FishAquariumGame():

	def __init__(self):
		pygame.init()
		self.ScreenWidth = 1600
		self.ScreenHeight = 1000
		self.ScrCenterX = self.ScreenWidth / 2
		self.ScrCenterY = self.ScreenHeight / 2
		self.gameOver = False
		self.screen = pygame.display.set_mode((self.ScreenWidth, self.ScreenHeight))
		self.clock = pygame.time.Clock()
		self.mouseX = 0;
		self.mouseY = 0;

		self.fc = FishController();
		self.Insp = Inspector();

	def start(self):
		while not self.gameOver:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.gameOver = True
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_SPACE:
						self.fc.addFish(random.randint(self.ScrCenterX - 200,self.ScrCenterX + 200), random.randint(self.ScrCenterY - 200,self.ScrCenterY + 200))
				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 1: #left click
						self.Insp.currentItem = self.fc.getAquariumItem(self.mouseX, self.mouseY)
					if event.button == 3: #right click
						for i in range(0, 10):
							self.fc.addFood(random.randint(10,self.ScreenWidth - 300 - 10), random.randint(10,self.ScreenHeight + 10))

				if event.type == pygame.MOUSEMOTION:
					position = event.pos
					self.mouseX = position[0]
					self.mouseY = position[1]	
			
			#Main Game Loop
			self.screen.fill((0,0,0))
			self.fc.moveFish()
			self.fc.feedFish()

			#Draws
			self.fc.drawFood(self.screen)
			self.fc.drawFish(self.screen)
			self.Insp.drawPane(self.screen, self.ScreenWidth, self.ScreenHeight, self.mouseX, self.mouseY)
			
			pygame.display.flip()
			self.clock.tick(60)

class Inspector():

	def __init__(self):
		self.currentItem = None

	def drawPane(self, screen, gameWidth, gameHeight, mosX, mosY):
		#Draw Pane
		pygame.draw.rect(screen, (40, 40, 40), pygame.Rect(gameWidth - 300, 0, 300, gameHeight))

		#Type Mouse Cursor Pos Bottom
		fontSize = 30
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
			#print("Fish X: " + str(fish.x) + " Fish Y: " + str(fish.y))
			#print("Mos X: " + str(x) + " Mos Y: " + str(y))
			#print("Fish X + lenX: " + str(fish.x + fish.lenX) + " Fish Y + lenY: " + str(fish.y + fish.lenY))
			fishIn = self.inFishBounds(fish, x, y)
			if(fishIn):
				print("made it here")
				chosenFish = fish
		return chosenFish 
		

	def distance(self, fish, x, y):
		#returns distance between a fish and a point
		return math.sqrt((fish.x - x)**2 + (fishy - y)**2)

	def inFishBounds(self, fish, x, y):
		if(fish.x < x < fish.x + fish.lenX and fish.y < y < fish.y + fish.lenY):
			print("true")
			return True;
		else:
			print("false")
			return False;

	def drawFish(self, screen):
		for fish in self.fishInTank:
			fish.draw(screen);

	def moveFish(self):
		for fish in self.fishInTank:
			fish.move();

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
		print("Food uid is: " + str(self.uid))
		self.x = x
		self.y = y
		self.radius = 5
		self.nutrition = 25 
		
	def draw(self, screen):
		pygame.draw.circle(screen,(100, 255, 0), (self.x, self.y), self.radius * 2);

class Fish():

	def __init__(self, x=0, y=0):
		self.uid = random.randint(0,63000)
		print("Fish uid is: " + str(self.uid))
		self.x = x	
		self.y = y
		self.lenX = 60
		self.lenY = 60
		self.Health = 100
		self.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
	
	def draw(self,screen):
		pygame.draw.rect(screen, self.color, pygame.Rect(self.x, self.y, self.lenX, self.lenY))

	def move(self):
		dx = random.randint(-2 * int(self.Health / 100), 2 * int(self.Health / 100));
		dy = random.randint(-2 * int(self.Health / 100), 2 * int(self.Health / 100));
		self.x = self.x + dx;
		self.y = self.y + dy

	def eat(self, food):
	
		#returns eaten food
		foodToEatIDs = []
		for foo in food:	
			#Food is within box
			#if (self.x < foo.x < self.x + self.lenX) and (self.y < foo.y < self.y + self.lenY):
			if( 
				((self.x < foo.x - foo.radius < self.x + self.lenX) and (self.y < foo.y < self.y - self.lenY)) or 
				((self.x < foo.x - foo.radius < self.x + self.lenX) and (self.y < foo.y < self.y + self.lenY)) or 
				((self.x < foo.y + foo.radius < self.x + self.lenX) and (self.y < foo.y < self.y - self.lenY)) or 
				((self.x < foo.y + foo.radius < self.x + self.lenX) and (self.y < foo.y < self.y + self.lenY))
			):
				self.Health = self.Health + foo.nutrition;
				foodToEatIDs.append(foo.uid)		
		return foodToEatIDs
					

game = FishAquariumGame();
game.start();
