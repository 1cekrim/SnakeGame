import numpy as np
import random as rnd
import matplotlib.pyplot as plt
import pygame as pg
import sys
import copy
from pygame.locals import *

# google colab
# %matplotlib inline

def put_food(board: np.ndarray) -> np.ndarray:
    _, height, width = board.shape
    i = 0
    while True:
        i += 1
        y, x = rnd.randrange(1, height - 1), rnd.randrange(1, width - 1)
        if (board[1][y][x] == 0 and board[2][y][x] == 0 and board[3][y][x] == 0):
            break
        if (i > 1000):
            return board, True
    board[3][y][x] = 1
    return board, False

def init_game(height, width, length, food) -> np.ndarray:
    board = np.zeros((4, height, width))
    
    for i in range(0, width):
        board[0][0][i] = 1
        board[0][height - 1][i] = 1
    
    for i in range(1, height):
        board[0][i][0] = 1
        board[0][i][width - 1] = 1

    body = [[height // 2, width // 2]]
    board[2][height // 2][width // 2] = 1

    for i in range(1, length):
        body.append([height // 2, width // 2 - i])
        board[1][height // 2][width // 2 - i] = 1

    for i in range(0, food):
        put_food(board)

    def get():
        return board, body, 0, length
    
    return get

def show_board_plt(board: np.ndarray):
    depth, height, width = board.shape

    buf = np.empty((height, width, depth))
    
    for y in range(0, height):
        for x in range(0, width):
            for d in range(0, depth):
                buf[y][x][d] = board[d][y][x]
    
    plt.imshow(buf, interpolation="nearest")

def get_pygame_renderer(board, rect_size):
    depth, height, width = board.shape

    pg.init()
    screen = pg.display.set_mode((width * rect_size, height * rect_size), DOUBLEBUF)
    pg.display.set_caption('snakegame')

    EMPTY = (0, 0, 0)
    WALL = (255, 0, 0)
    FOOD = (0, 255, 0)
    BODY = (0, 0, 255)
    HEAD = (128, 128, 255)

    def render(board):
        screen.fill((0, 0, 0))
        
        for y in range(0, height):
            for x in range(0, width):
                if board[0][y][x] == 1:
                    block = WALL
                elif board[1][y][x] == 1:
                    block = BODY
                elif board[2][y][x] == 1:
                    block = HEAD
                elif board[3][y][x] == 1:
                    block = FOOD
                else:
                    block = EMPTY
                pg.draw.rect(screen, block, (x * rect_size, y * rect_size, rect_size, rect_size))
        pg.display.flip()
    
    return render

def play(init, env, player, renderer):
    clock = pg.time.Clock()
    board, body, direction, length = init()
    
    while True:
        action = 1

        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    action = 0
                elif event.key == K_RIGHT:
                    action = 2
        
        state = dict(board = board, body = body, direction = direction, length = length)
        

        renderer()
        clock.tick(1)

def get_env(board):
    depth, height, width = board.shape
    dir = [[0, 1], [1, 0], [0, -1], [-1, 0]]

    def env(state: dict, action: int):
        is_ended = False
        
        board: np.ndarray = copy.deepcopy(state["board"])
        body: list = copy.deppcopy(state["body"])
        direction: int = state["direction"]
        length: int = state["length"]

        if action == 0:
            direction -= 1
        elif action == 2:
            direction += 1
        
        if direction < 0:
            direction = 3
        elif direction > 3:
            direction = 0

        head: list = [body[0][0] + dir[direction][0], body[0][1] + dir[direction][1]]

        reward = -0.01

        headY = head[0]
        headX = head[1]

        if board[0][headY][headX] == 1:
            reward = -1
            is_ended = True
        elif board[1][headY][headX] == 1:
            reward = -1
            is_ended = True
        elif board[3][headY][headX] == 1:
            length += 1
            rewart = 1
            board, is_ended = put_food(board)

        body.insert(0, head)

        board[1][head[0]][head[1]] = 0
        board[2][head[0]][head[1]] = 1
        board[3][head[0]][head[1]] = 0
        
        board[2][body[1][0]][body[1][1]] = 1

        if reward != 1:
            board[1][body[length][0]][body[length][1]] = 0
            del body[length]
        
        return dict(board = board, body = body, direction = direction, length = length), reward

def main():
    print("state init success!")
    
    renderer = get_pygame_renderer(board, 50)
    env = get_env(board)
    
    play(init_game(15, 15, 5, 5), env, None, renderer)
    
main()