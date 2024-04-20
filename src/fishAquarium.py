import csv
from enum import Enum
import math
import pygame as pg
import os
import random as rd
import numpy as np
import math
import sys

# Adjusting PATH
abovePath = os.path.join(__file__, "..")
print("Adding Path: " + os.path.abspath(abovePath))
sys.path.append(abovePath)
print("SysPath: " + sys.path.__str__())

from FishNN import FishNN
from fish_controller import FishController
from inspector import Inspector


class GameMode(Enum):
    SIM = "SIM"
    DEBUG = "DEBUG"
    TRAINING = "TRAINING"


class FishAquariumGame:
    def __init__(self, gamemode=GameMode.TRAINING):
        pg.init()
        self.nn_model = FishNN()
        self.ScreenWidth = 1400  # 1600
        self.ScreenHeight = 800  # 1000
        self.ScrCenterX = self.ScreenWidth / 2
        self.ScrCenterY = self.ScreenHeight / 2
        self.gameOver = False
        self.screen = pg.display.set_mode((self.ScreenWidth, self.ScreenHeight))
        self.clock = pg.time.Clock()
        self.mouseX = 0
        self.mouseY = 0
        self.mode = gamemode

        self.fc = FishController()
        self.Insp = Inspector()

    def start(self):
        if self.mode == GameMode.TRAINING:
            pass
            # os.remove("fishNNDataFile.tflearn")

        if self.mode == GameMode.DEBUG:
            if os.path.exists("generation.csv"):
                os.remove("generation.csv")

            for i in range(0, 150):
                self.fc.addFood(
                    rd.randint(10, self.ScreenWidth - 10),
                    rd.randint(10, self.ScreenHeight + 10),
                )

            numTimesToSimulate = 10
            trainingData = []
            allActions = []
            for i in range(0, numTimesToSimulate):
                self.fc.addFish(
                    rd.randint(10, self.ScreenWidth - 10),
                    rd.randint(10, self.ScreenHeight + 10),
                    pg.time.get_ticks(),
                )
                elapsedTime = 0
                for j in range(0, 10):
                    self.fc.addFood(
                        rd.randint(10, self.ScreenWidth - 10),
                        rd.randint(10, self.ScreenHeight + 10),
                    )

                while not self.fc.isAllFishDead():
                    for event in pg.event.get():
                        if event.type == pg.QUIT:
                            self.gameOver = True

                    # Main Game Loop
                    self.screen.fill((0, 0, 0))
                    curTrainingData = self.fc.lookFish(self.screen)
                    action = self.fc.moveFish()
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

                    # TODO determine move from matrix of vision (backpropogate to this data structure)
                    trainingToAdd = [curTrainingData, int(actionValue)]
                    trainingData.append(trainingToAdd)
                    allActions.append(
                        [
                            i,
                            curTrainingData[-1],
                            curTrainingData[-2],
                            action[2],
                            action[1],
                            actionValue,
                        ]
                    )

                    elapsedTime += pg.time.get_ticks()
                    if elapsedTime > 5000:
                        # print(trainingToAdd)
                        elapsedTime = 0

                    # curTrainingData = np.append([trainingData], curTrainingData)

                    # Draws
                    self.fc.drawFood(self.screen)
                    self.fc.drawFish(self.screen, pg.time.get_ticks())
                    self.Insp.drawPane(
                        self.screen,
                        self.ScreenWidth,
                        self.ScreenHeight,
                        self.mouseX,
                        self.mouseY,
                    )

                    pg.display.flip()

                    self.clock.tick(120)
                self.fc.writeFishToFile()
                self.fc.writeActionsToFile(allActions)
                # print(trainingData)
                self.fc.fishInTank[0].alive = True
                self.fc.reproduceAll(pg.time.get_ticks())
                self.fc.fishInTank.pop(0)
                try:
                    self.nn_model = self.train_model(trainingData, self.nn_model)
                except:
                    [print(i) for i in trainingData if len(i[0]) != 7]
        if self.mode == GameMode.SIM:
            if os.path.exists("generation.csv"):
                os.remove("generation.csv")

            for i in range(0, 150):
                self.fc.addFood(
                    rd.randint(10, self.ScreenWidth - 10),
                    rd.randint(10, self.ScreenHeight + 10),
                )
            self.fc.addFish(
                rd.randint(10, self.ScreenWidth - 10),
                rd.randint(10, self.ScreenHeight + 10),
                pg.time.get_ticks(),
            )

            while not self.gameOver:
                trainingData = []
                predictions = []
                game_memory = []

                elapsedTime = 0

                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.gameOver = True
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_SPACE:
                            self.fc.addFish(self.mouseX, self.mouseY)
                        if event.key == pg.K_n:
                            self.fc.reproduceAll(pg.time.get_ticks())
                        if event.key == pg.K_k:
                            self.fc.killAll()

                    if event.type == pg.MOUSEBUTTONDOWN:
                        if event.button == 1:  # left click
                            self.Insp.currentItem = self.fc.getAquariumItem(
                                self.mouseX, self.mouseY, pg.time.get_ticks()
                            )
                        if event.button == 3:  # right click
                            self.fc.addFood(self.mouseX, self.mouseY)

                    if event.type == pg.MOUSEMOTION:
                        position = event.pos
                        self.mouseX = position[0]
                        self.mouseY = position[1]

                    # Main Game Loop
                    self.screen.fill((0, 0, 0))
                    self.fc.lookFish(self.screen)

                    for action in range(-1, 2):
                        np.append([action], predictions).reshape(-1, 7, 1)
                        predictedAction = model.predict(predictions)
                        np.append([predictedAction], predictions)

                    action = np.argmax(np.array(predictions))
                    curTrainingData = self.fc.moveFish(action)
                    didFishFeed = self.fc.feedFish()
                    trainingToAdd = [curTrainingData, int(didFishFeed)]
                    trainingData.append(trainingToAdd)

                    done, _, snake, _ = game.step(game_action)
                    game_memory.append([prev_observation, action])
                    if done:
                        break
                    else:
                        prev_observation = self.generate_observation(snake)
                        steps += 1
                    steps_arr.append(steps)

                    elapsedTime += pg.time.get_ticks()
                    if elapsedTime > 5000:
                        # print(trainingToAdd)
                        elapsedTime = 0

                    # Draws
                    self.fc.drawFood(self.screen)
                    self.fc.drawFish(self.screen, pg.time.get_ticks())
                    self.Insp.drawPane(
                        self.screen,
                        self.ScreenWidth,
                        self.ScreenHeight,
                        self.mouseX,
                        self.mouseY,
                    )

                    pg.display.flip()

                    self.clock.tick(120)
            self.fc.writeFishToFile()
            # print(trainingData)
            self.fc.fishInTank[0].alive = True
            self.fc.reproduceAll(pg.time.get_ticks())
            self.fc.fishInTank.pop(0)
        self.nn_model = self.train_model(trainingData, self.nn_model)


game = FishAquariumGame()
game.start()
