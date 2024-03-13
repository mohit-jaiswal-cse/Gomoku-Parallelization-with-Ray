# Gomoku-Parallelization-with-Ray 
This software is a Python-based implementation of the popular game Gomoku. Gomoku involves strategically placing player pieces on a 15×15 grid in order to create a straight line of five consecutive pieces, either horizontally, vertically, or diagonally.

The code consists of several key components:

### *Game Logic:*
The game's logic is implemented using a two-dimensional NumPy array, which is initialized by the create_board function. Various functions, such as horizontalWins, verticalWin, positive-slopedDiagonalWin, and negative-slopedDiagonalWin, ensure that winning situations are detected in different orientations.

### *Parallelization with Ray:*
To improve performance, certain calculations, such as win-checking, are parallelized using the Ray library. The Ray remote decorator allows the definition of functions that can be executed in parallel.

### *Main Game Loop:*
The main game loop allows participants to take turns placing their pieces on the board. The code automatically detects a winning player after each move, and the game ends once a win is detected.

### *Performance Metrics:*
The code provides information on the execution time of both the serial and parallel sections of the algorithm. It also calculates and displays the speed-up and efficiency achieved by the parallel version.

### *User Interface:*
The Pygame library is used to create a user-friendly interface for the game, allowing players to interact with the game on screen.

### *Graphical Output:*
At the end of the game, the winner is displayed on the screen.

### *Analysis and Efficiency Metrics:*
The code allows for the analysis of speed-up and efficiency for different core configurations and board sizes. This capability is useful for evaluating the performance of parallel algorithms in board games.


<p align="center">
  <img src="https://github.com/Bhakti-08/Gomoku-Parallelization-with-Ray/assets/103896834/97bcf272-1b7c-42d1-99ab-17381e3be1df" alt="gomoku"/>
</p>


<p align="center">Figure 1: Gomoku Board</p>


<p align="center">
  <img src="https://github.com/Bhakti-08/Gomoku-Parallelization-with-Ray/assets/103896834/95f65924-8a5a-471e-9498-07bb7299a9da" alt="Analysis"/>
</p>

<p align="center">Figure 2: Graphical Analysis</p>

This code serves as a valuable resource for understanding various techniques for parallelizing board games and testing the efficiency of parallel algorithms. It is particularly suitable for individuals interested in learning about parallel programming using Python.
