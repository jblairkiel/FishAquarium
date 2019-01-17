import pygame
import random

class FishAquariumGame():

	def __init__(self):
		pygame.init()
		self.ScreenWidth = 1200
		self.ScreenHeight = 900
		self.ScrCenterX = self.ScreenWidth / 2
		self.ScrCenterY = self.ScreenHeight / 2
		self.gameOver = False
		self.screen = pygame.display.set_mode((self.ScreenWidth, self.ScreenHeight))
		self.fc = FishController();
		self.clock = pygame.time.Clock()
		self.mouseX = 0;
		self.mouseY = 0;

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
						self.fc.addFood(self.mouseX,self.mouseY)
					if event.button == 3: #right click
						for i in range(0, 10):
							self.fc.addFood(random.randint(self.ScrCenterX - 400,self.ScrCenterX + 400), random.randint(self.ScrCenterY - 400,self.ScrCenterY + 400))

				if event.type == pygame.MOUSEMOTION:
					position = event.pos
					self.mouseX = position[0]
					self.mouseY = position[1]	
			
			#Main Game Loop
			self.screen.fill((0,0,0))
			self.fc.moveFish()
			self.fc.feedFish()
			self.fc.drawFood(self.screen)
			self.fc.drawFish(self.screen)
			
			pygame.display.flip()
			self.clock.tick(60)

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

	def drawFish(self, screen):
		for fish in self.fishInTank:
			fish.draw(screen);

	def moveFish(self):
		for fish in self.fishInTank:
			fish.move();

	def feedFish(self):
		for fish in self.fishInTank:
			eatenFoodIDs = fish.eat(self.fishFood)
			self.fishFood = [x for x in self.fishFood if x.uid not in eatenFoodIDs]
		

class Food():

	def __init__(self, x=0, y=0):
		self.uid = random.randint(0,63000)
		print("Food uid is: " + str(self.uid))
		self.x = x
		self.y = y
		self.nutrition = 25 
		
	def draw(self, screen):
		pygame.draw.circle(screen,(100, 255, 0), (self.x, self.y), 5);
class Fish():

	def __init__(self, x=0, y=0):
		self.x = x	
		self.y = y
		self.lenX = 60
		self.lenY = 60
		self.Health = 100
	
	def draw(self,screen):
		pygame.draw.rect(screen, (255, 100, 0), pygame.Rect(self.x, self.y, self.lenX, self.lenY))

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
			if (self.x < foo.x < self.x + self.lenX) & (self.y < foo.y < self.y + self.lenY):
				self.Health = self.Health + foo.nutrition;
				foodToEatIDs.append(foo.uid)		
		return foodToEatIDs
					

game = FishAquariumGame();
game.start();
