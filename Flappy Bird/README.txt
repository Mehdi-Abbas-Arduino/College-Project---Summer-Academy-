# Flappy Bird Game

## How to Play
Welcome to Flappy Bird! Your goal is to navigate the bird through the gaps between the green pipes and score as many points as possible.


### Controls
- **UP Arrow** or **SPACEBAR**: Make the bird jump


### Game States
1. **Ready State**: When the game starts, the bird will hover in place. Press SPACE, UP arrow, or click to begin.

2. **Playing State**: Once you start, gravity will pull the bird down. Each time you press a key or click, the bird will jump upward. Navigate through the gaps in the pipes.

3. **Game Over**: If the bird hits a pipe, the floor, or the ceiling, the game ends. You'll see "GAME OVER!" with your final score. Press SPACE or click to restart.


### Scoring
- You earn **1 point** for every pipe you successfully pass through
- The score is displayed in the top-left corner of the screen


### Tips
- Time your jumps carefully - don't jump too early or too late
- The gaps between pipes are randomly placed, so stay alert
- The bird falls due to gravity, so you need to keep tapping to stay airborne
- Practice makes perfect!


## How to Run the Game
1. Make sure you have Python installed on your computer
2. Install Pygame by running: `pip install pygame`
3. Make sure you have both files in the same folder:
   - `main.py` (the game engine)
   - `logic_skeleton.py` (the game logic)
4. Run the game by executing: `python main.py`


## Educational Notes
This game is designed to teach fundamental programming concepts:
- **Functions**: Organizing code into reusable blocks
- **Dictionaries**: Storing game object properties (bird position, pipe gaps)
- **Lists**: Managing multiple objects (pipes on screen)
- **Loops**: Iterating through game objects
- **Conditionals**: Making decisions (collision detection, scoring)

The game is split into two files:
- `main.py`: Handles graphics and game loop 
- `logic_skeleton.py`: Contains the game logic (Student's file)


Enjoy the game and happy coding!