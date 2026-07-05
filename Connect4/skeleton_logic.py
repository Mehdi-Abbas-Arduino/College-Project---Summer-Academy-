"""
skeleton_logic.py -- CODE CRAFT ASSIGNMENT
--------------------------------------------
Your job: fill in the functions below so that Connect 4 works.

Once you're done, rename this file to "game_logic.py" and place it in
the same folder as main.py and sound_effects.py, then run:

    python main.py

You will practice:
    - lists and nested lists (the board)
    - loops and nested loops (scanning rows/columns)
    - conditionals (if / elif / else)
    - dictionaries (PLAYERS)
    - functions (every task below is one function)

Do NOT import tkinter or pygame in this file -- it should only use
plain Python. Test your work anytime by running:

    python skeleton_logic.py

That runs the little test at the bottom of this file.
"""

import random

ROWS = 6
COLS = 7
EMPTY = " "

# Dictionary storing each player's name and piece color.
PLAYERS = {
    "P1": "red",
    "P2": "yellow"
}

# How often a dropped piece turns out to be a bomb. 0.125 = 1 in 8 drops.
BOMB_CHANCE = 0.125

# How often a turn is decided by a dice roll instead of the player's
# own click. 0.2 = roughly 1 in 5 turns.
DICE_CHANCE = 0.2


def create_board():
    """
    TODO: Create and return a new board.

    The board should be a list of ROWS lists, and each of those lists
    should contain COLS items, all set to EMPTY.

    Hint: use a loop (or nested list comprehension) to build it.
    Example shape for ROWS=2, COLS=3:  [[" ", " ", " "], [" ", " ", " "]]
    """
    pass


def print_board(board):
    """
    TODO: Print the board to the terminal, one row per line.

    Hint: loop through each row in the board and print it. You can
    join the items in a row with "|" using "|".join(row) if you like.
    """
    pass


def is_valid_column(board, col):
    """
    TODO: Return True if 'col' is a legal column to drop a piece into.

    A column is valid if:
      1. It's within range: 0 <= col < COLS
      2. The TOP cell of that column (board[0][col]) is still EMPTY

    Return False otherwise.
    """
    pass


def get_next_open_row(board, col):
    """
    TODO: Find the lowest empty row in the given column.

    Hint: pieces fall to the bottom, so start checking from the last
    row (ROWS - 1) and work upward (row 0). Return the first row
    number you find that is EMPTY. If the column is full, return None.
    """
    pass


def drop_piece(board, row, col, piece):
    """
    TODO: Place 'piece' ("red" or "yellow") into board[row][col].
    """
    pass


def is_board_full(board):
    """
    TODO: Return True if there is no room left to drop any piece.

    Hint: the board is full when the TOP row (row 0) has no EMPTY
    cells left. Loop through each column and check board[0][col].
    """
    pass


def check_winner(board, piece):
    """
    TODO: Return True if 'piece' has four in a row anywhere on the
    board. You need to check FOUR directions:
      1. Horizontal  (row stays the same,     col increases)
      2. Vertical    (row increases,          col stays the same)
      3. Diagonal \\  (row increases,          col increases)
      4. Diagonal /  (row increases,          col decreases)

    Hint: each direction needs a nested loop (one loop for the
    starting row, one for the starting column), and then check 4
    cells in a row using that direction's pattern.

    This is the hardest function -- start with horizontal, get it
    fully working and tested, then copy/adapt your approach for the
    other three directions.
    """
    pass


def switch_player(current_player):
    """
    TODO: Return the OTHER player's piece color.

    Hint: use the PLAYERS dictionary. If current_player is
    PLAYERS["P1"], return PLAYERS["P2"], and vice versa.
    """
    pass


def create_scoreboard():
    """
    TODO: Create and return a dictionary that tracks wins for each
    player plus draws, so a score can carry across multiple rounds.

    The dictionary should have three keys:
        PLAYERS["P1"]  -> 0
        PLAYERS["P2"]  -> 0
        "draws"        -> 0
    """
    pass


def update_score(scoreboard, result):
    """
    TODO: Update the scoreboard after a round ends.

    'result' will be either a piece color (that player won) or the
    exact string "draw". Add 1 to the correct entry in the scoreboard
    dictionary.
    """
    pass


def format_scoreboard(scoreboard):
    """
    TODO: Turn the scoreboard dictionary into a readable one-line
    string, for example:

        "Red: 2  |  Yellow: 1  |  Draws: 0"

    Hint: use an f-string and .capitalize() on the player names.
    """
    pass


def record_move(move_history, row, col, piece):
    """
    TODO: Add a move to move_history so it can be undone later.

    Store each move as a dictionary with keys "row", "col", "piece",
    and append it to the move_history list.
    """
    pass


def undo_last_move(board, move_history):
    """
    TODO: Remove the most recent move from BOTH the board and
    move_history.

    Steps:
      1. If move_history is empty, return None (nothing to undo).
      2. Otherwise, remove the last item from move_history
         (Hint: lists have a .pop() method that removes and returns
         the last item).
      3. Set that cell on the board back to EMPTY.
      4. Return the move you removed, so main.py knows which circle
         to clear and whose turn it becomes again.
    """
    pass


def roll_dice():
    """
    TODO: Roll a single 7-sided die -- one number per column.

    Hint: use random.randint(low, high) to get a random whole number
    between 0 and COLS - 1 (inclusive on both ends).
    """
    pass


def is_dice_turn():
    """
    TODO: Decide if THIS turn is a dice turn (instead of the player
    clicking a column themselves).

    Hint: same pattern as is_bomb_drop -- compare random.random() to
    DICE_CHANCE.
    """
    pass


def get_dice_column(board):
    """
    TODO: Roll the dice to pick a column for a dice turn.

    Rules:
      - Players do NOT get to reroll just because they don't like the
        column that came up.
      - The ONLY time you roll again is if the column that came up is
        completely full (use is_valid_column to check).

    Hint: roll once, then use a while loop that keeps rerolling only
    while the column is invalid.
    """
    pass


def is_bomb_drop():
    """
    TODO: Decide if this drop is a bomb.

    Hint: random.random() gives you a random decimal between 0 and 1.
    Compare it to BOMB_CHANCE to decide True or False.
    """
    pass


def get_bomb_cells(row, col):
    """
    TODO: Return a list of every (row, col) cell a bomb at (row, col)
    would clear -- that's the cell itself plus its 8 neighbors (a 3x3
    block centered on the drop).

    Hint: use two nested loops, one for rows from (row - 1) to
    (row + 1) and one for columns from (col - 1) to (col + 1). Only
    add a cell to your list if it's actually on the board (check
    0 <= r < ROWS and 0 <= c < COLS) -- otherwise you'll get an error
    for cells that don't exist near the edges/corners.
    """
    pass


def explode_bomb(board, row, col):
    """
    TODO: Clear every cell that get_bomb_cells(row, col) returns,
    setting each one back to EMPTY.
    """
    pass


if __name__ == "__main__":
    # Quick self-test -- run this file directly to check your work
    # as you go, without needing the full GUI.
    board = create_board()
    print_board(board)

    print("Column 3 valid?", is_valid_column(board, 3))

    row = get_next_open_row(board, 3)
    print("Next open row in column 3:", row)

    drop_piece(board, row, 3, PLAYERS["P1"])
    print_board(board)

    print("Board full?", is_board_full(board))
    print("P1 wins yet?", check_winner(board, PLAYERS["P1"]))
    print("Next player after P1:", switch_player(PLAYERS["P1"]))

    print("Dice-rolled column:", get_dice_column(board))
    print("Is this a dice turn?", is_dice_turn())
    print("Bomb cells around (5, 3):", get_bomb_cells(5, 3))

    # --- New features to test ---
    history = []
    record_move(history, row, 3, PLAYERS["P1"])
    print("Move history:", history)

    scoreboard = create_scoreboard()
    update_score(scoreboard, PLAYERS["P1"])
    print(format_scoreboard(scoreboard))

    undone = undo_last_move(board, history)
    print("Undone move:", undone)
    print_board(board)
