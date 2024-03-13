import numpy as np
import pygame
import sys
import math
import ray
import time
import psutil

serialExecutionTime = 0
parallelExecutionTime = 0


# initialize the pygame program
pygame.init()

# static variables
ROW_COUNT = 15
COL_COUNT = 15

# define screen size
BLOCKSIZE = 50  # individual grid
S_WIDTH = COL_COUNT * BLOCKSIZE  # screen width
S_HEIGHT = ROW_COUNT * BLOCKSIZE  # screen height
PADDING_RIGHT = 200  # for game menu
SCREENSIZE = (S_WIDTH, S_HEIGHT)
RADIUS = 20  # game piece radius

# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BROWN = (234, 198, 150)

# create a board array
def create_board(row, col):
    board = np.zeros((row, col))
    return board

# draw a board in pygame window
def draw_board(screen):
    for x in range(0, S_WIDTH, BLOCKSIZE):
        for y in range(0, S_HEIGHT, BLOCKSIZE):
            rect = pygame.Rect(x, y, BLOCKSIZE, BLOCKSIZE)
            pygame.draw.rect(screen, BROWN, rect)

    # draw inner grid lines
    # draw vertical lines
    for x in range(BLOCKSIZE // 2, S_WIDTH - BLOCKSIZE // 2 + BLOCKSIZE, BLOCKSIZE):
        line_start = (x, BLOCKSIZE // 2)
        line_end = (x, S_HEIGHT - BLOCKSIZE // 2)
        pygame.draw.line(screen, BLACK, line_start, line_end, 2)

    # draw horizontal lines
    for y in range(BLOCKSIZE // 2, S_HEIGHT - BLOCKSIZE // 2 + BLOCKSIZE, BLOCKSIZE):
        line_start = (BLOCKSIZE // 2, y)
        line_end = (S_WIDTH - BLOCKSIZE // 2, y)
        pygame.draw.line(screen, BLACK, line_start, line_end, 2)
    pygame.display.update()

# drop a piece
def drop_piece(board, row, col, piece):
    board[row][col] = piece

# draw a piece on the board
def draw_piece(screen, board):
    # draw game pieces at mouse location
    for x in range(COL_COUNT):
        for y in range(ROW_COUNT):
            circle_pos = (x * BLOCKSIZE + BLOCKSIZE // 2, y * BLOCKSIZE + BLOCKSIZE // 2)
            if board[y][x] == 1:
                pygame.draw.circle(screen, BLACK, circle_pos, RADIUS)
            elif board[y][x] == 2:
                pygame.draw.circle(screen, WHITE, circle_pos, RADIUS)
    pygame.display.update()

# check if it is a valid location
def is_valid_loc(board, row, col):
    return board[row][col] == 0

@ray.remote
# horizontal win check
def horizontalWin(board, piece):
    for c in range(COL_COUNT - 4):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece \
                    and board[r][c+4] == piece:
                return True
    return False

@ray.remote
# vertical win check
def verticalWin(board, piece):
    for c in range(COL_COUNT):
        for r in range(ROW_COUNT - 4):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece \
                    and board[r+4][c] == piece:
                return True
    return False

@ray.remote
# check for positively sloped diagonal win
def positiveSlopedDiagonalWin(board, piece):
    for c in range(COL_COUNT - 4):
        for r in range(4, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece \
                    and board[r-4][c+4] == piece:
                return True
    return False

@ray.remote
# check for negatively sloped diagonal win
def negativeSlopedDiagonalWin(board, piece):
    for c in range(COL_COUNT - 4):
        for r in range(ROW_COUNT - 4):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece \
                    and board[r+4][c+4] == piece:
                return True
    return False

def who_wins(board, piece):
    global serialExecutionTime
    global parallelExecutionTime
    WinResult = False
    
    startSerialTime = time.time()
    # Serial
    # check for horizontal win
    for c in range(COL_COUNT - 4):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece \
                    and board[r][c+4] == piece:
                WinResult = True

    # check for vertical win
    for c in range(COL_COUNT):
        for r in range(ROW_COUNT - 4):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece \
                    and board[r+4][c] == piece:
                WinResult = True

    # check for positively sloped diagonal win
    for c in range(COL_COUNT - 4):
        for r in range(4, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece \
                    and board[r-4][c+4] == piece:
                WinResult = True

    # check for negatively sloped diagonal win
    for c in range(COL_COUNT - 4):
        for r in range(ROW_COUNT - 4):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece \
                    and board[r+4][c+4] == piece:
                WinResult = True
    endSerialTime = time.time()

    # Parallel
    startParallelTime = time.time()
    win_checks = [horizontalWin.remote(board, piece), verticalWin.remote(board, piece),
                  positiveSlopedDiagonalWin.remote(board, piece), negativeSlopedDiagonalWin.remote(board, piece)]
    win_results = ray.get(win_checks)
    if any(win_results):
        WinResult = True
    endParallelTime = time.time()

    serialExecutionTime += (endSerialTime - startSerialTime)
    parallelExecutionTime += (endParallelTime - startParallelTime)
    return WinResult

def efficiency(serial_time, parallel_time, num_cores):
    serial_fraction = serial_time / (serial_time + (parallel_time / num_cores))
    parallel_fraction = 1 - serial_fraction
    return serial_fraction + (parallel_fraction / num_cores)

def speedup(serial_time, parallel_time):
    return serial_time / parallel_time

def main():
    # initializing ray with given number of cores (here it is 2 cores)
    ray.init(num_cpus=2)

    # get the resources available to Ray
    resources = ray.cluster_resources()
    num_cpus = int(resources.get("CPU", 1))  # default to 1 if not found

    # game variables
    game_over = False
    turn = 0  # turn == 0 for player 1, turn == 1 for player 2
    piece_1 = 1  # black
    piece_2 = 2  # white

    # FPS
    FPS = 60
    frames_per_sec = pygame.time.Clock()

    # board 2D array
    board = create_board(ROW_COUNT, COL_COUNT)
    # print(board)

    print("Number of CPU cores:", num_cpus)
    # game screen
    SCREEN = pygame.display.set_mode(SCREENSIZE)
    SCREEN.fill(WHITE)
    pygame.display.set_caption('Gomoku')

    # font
    my_font = pygame.font.Font('freesansbold.ttf', 45)

    # text message
    label_1 = my_font.render('BLACK WINS!!!', True, WHITE, BLACK)
    label_2 = my_font.render('WHITE WINS!!!', True, WHITE, BLACK)

    # display the screen
    draw_board(SCREEN)

    # game loop
    while not game_over:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x_pos = event.pos[0]
                y_pos = event.pos[1]

                col = int(math.floor(x_pos / BLOCKSIZE))
                row = int(math.floor(y_pos / BLOCKSIZE))

                # turn decision, if black(1)/white(2) piece already placed, go back to the previous turn
                if board[row][col] == 1:
                    turn = 0
                if board[row][col] == 2:
                    turn = 1
                
                #center_y = 25  # Adjust the y-coordinate as needed

                # Ask for Player 1 move
                if turn == 0:
                    # check if it's a valid location then drop a piece
                    if is_valid_loc(board, row, col):
                        drop_piece(board, row, col, piece_1)
                        draw_piece(SCREEN, board)

                        if who_wins(board, piece_1):
                            print("Serial Time: {:.4f}\nParallel Time: {:.4f}".format(serialExecutionTime, parallelExecutionTime))

                            #SCREEN.blit(label_1, (280, 25))
                            center_x = (SCREEN.get_width() - label_1.get_width()) // 2
                            center_y = (SCREEN.get_height() - label_1.get_height()) // 2
                            SCREEN.blit(label_1, (center_x, center_y))
                            pygame.display.update()
                            game_over = True

                # Ask for Player 2 move
                else:
                    # check if it's a valid location then drop a piece
                    if is_valid_loc(board, row, col):
                        drop_piece(board, row, col, piece_2)
                        draw_piece(SCREEN, board)

                        if who_wins(board, piece_2):
                            print("Serial Time: {:.4f}\nParallel Time: {:.4f}".format(serialExecutionTime, parallelExecutionTime))
                            
                            #SCREEN.blit(label_2, (280, 25))
                            center_x = (SCREEN.get_width() - label_2.get_width()) // 2
                            center_y = (SCREEN.get_height() - label_2.get_height()) // 2
                            SCREEN.blit(label_2, (center_x, center_y))
                            pygame.display.update()
                            game_over = True

                # increment turn
                turn += 1
                turn = turn % 2

                if game_over:
                    efficiency_value = efficiency(serialExecutionTime, parallelExecutionTime, num_cpus)
                    speedup_value = speedup(serialExecutionTime, parallelExecutionTime)
                    print("Efficiency: {:.4f}\nSpeed Up: {:.4f}".format(efficiency_value,speedup_value))
                    pygame.time.wait(2000)

        frames_per_sec.tick(FPS)

if __name__ == '__main__':
    main()

