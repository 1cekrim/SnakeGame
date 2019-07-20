import numpy as np
import random as rnd
import matplotlib.pyplot as plt
import pygame as pg
import sys
import copy
from pygame.locals import *

# google colab
# %matplotlib inline

RIGHT = 0
DOWN = 1
LEFT = 2
UP = 3
DWALL = 0
DBODY = 1
DHEAD = 2
DFOOD = 3

class SnakeEnv:

    DIR = [[0, 1], [1, 0], [0, -1], [-1, 0]]

    def __init__(self, height, width, length, nFood):
        self.height = height
        self.width = width
        self.nFood = nFood
        self.length = length
        self.InitEnv()

    def InitEnv(self):
        self.board = np.zeros((4, self.height, self.width))
        self.direction = RIGHT
        
        for i in range(0, self.width):
            self.board[DWALL][0][i] = 1
            self.board[DWALL][self.height - 1][i] = 1
        
        for i in range(1, self.height):
            self.board[DWALL][i][0] = 1
            self.board[DWALL][i][self.width - 1] = 1
        
        self.body = [[self.height // 2, self.width // 2]]
        self.board[DHEAD][self.height // 2][self.width // 2] = 1

        for i in range(1, self.length):
            self.body.append([self.height // 2, self.width // 2 - i])
            self.board[1][self.height // 2][self.width // 2 - i] = 1
        
        for i in range(0, self.nFood):
            self.PutFood()

    def PutFood(self):
        i = 0
        while True:
            i += 1
            y, x = rnd.randrange(1, self.height - 1), rnd.randrange(1, self.width - 1)
            if self.board[DFOOD][y][x] == 0 and self.board[DHEAD][y][x] == 0 and self.board[DBODY][y][x] == 0:
                break
            if i > 1000:
                return True
        self.board[DFOOD][y][x] = 1
        return False

    def DoAction(self, action):
        isEnd = False

        if action == 0:
            self.direction -= 1
        elif action == 2:
            self.direction += 1
        
        if self.direction < 0:
            self.direction = 3
        elif self.direction > 3:
            self.direction = 0

        head = [self.body[0] + DIR[self.direction][0], self.body[1] + DIR[self.direction][1]]

        reward = -0.01

        if self.board[DWALL][head[0]][head[1]] == 1:
            reward = -1
            isENd = True
        elif self.board[DBODY][head[0]][head[1]] == 1:
            reward = -1
            isEnd = True
        elif self.board[DFOOD][head[0]][head[1]] == 1:
            reward = 1
            self.length += 1
            if self.PutFood():
                isEnd = True
        
        self.body.insert(0, head)
        self.board[DWALL][head[0]][head[1]] = 0
        self.board[DBODY][head[0]][head[1]] = 0
        self.board[DHEAD][head[0]][head[1]] = 1
        self.board[DFOOD][head[0]][head[1]] = 0

        self.board[DHEAD][self.body[1][0]][self.body[1][1]] = 0
        self.board[DBODY][self.body[1][0]][self.body[1][1]] = 1

        if reward <= 0:
            self.board[DBODY][self.body[self.length][0]][self.body[self.length][1]] = 0
            del self.body[self.length]

    def GetState(self):
        reshaped = np.zeros((4, self.height * self.width))

        for i in range(0, 4):
            reshaped[i] = self.board[i].reshape(self.height * self.width)
        
        return reshaped.T

    def ShowBoard(self):
        a = np.empty((self.height, self.width, 3))
        for i in range(0, self.height):
            for j in range(0, self.width):
                for k in range(0, 3):
                    a[i][j][k] = self.board[k][i][j]
                    a[i][j][k] += self.board[3][i][j]
        plt.imshow(a, interpolation="nearest")