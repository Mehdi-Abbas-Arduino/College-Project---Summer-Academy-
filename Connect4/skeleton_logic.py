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

PLAYERS = {
    "P1": "red",
    "P2": "yellow"
}

BOMB_CHANCE = 0.125
DICE_CHANCE = 0.2


def create_board():
    board = []
    for i in range(ROWS):
        row = []
        for j in range(COLS):
            row.append(EMPTY)
        board.append(row)
    return board


def print_board(board):
    for row in board:
        print("|".join(row))
    print()


def is_valid_column(board, col):
    if col < 0 or col >= COLS:
        return False

    if board[0][col] != EMPTY:
        return False

    return True


def get_next_open_row(board, col):
    for row in range(ROWS - 1, -1, -1):
        if board[row][col] == EMPTY:
            return row
    return None


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def is_board_full(board):
    for col in range(COLS):
        if board[0][col] == EMPTY:
            return False
    return True


def check_winner(board, piece):

    # Horizontal
    for row in range(ROWS):
        for col in range(COLS - 3):
            if (board[row][col] == piece and
                board[row][col + 1] == piece and
                board[row][col + 2] == piece and
                board[row][col + 3] == piece):
                return True

    # Vertical
    for row in range(ROWS - 3):
        for col in range(COLS):
            if (board[row][col] == piece and
                board[row + 1][col] == piece and
                board[row + 2][col] == piece and
                board[row + 3][col] == piece):
                return True

    # Diagonal \
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            if (board[row][col] == piece and
                board[row + 1][col + 1] == piece and
                board[row + 2][col + 2] == piece and
                board[row + 3][col + 3] == piece):
                return True

    # Diagonal /
    for row in range(ROWS - 3):
        for col in range(3, COLS):
            if (board[row][col] == piece and
                board[row + 1][col - 1] == piece and
                board[row + 2][col - 2] == piece and
                board[row + 3][col - 3] == piece):
                return True

    return False


def switch_player(current_player):
    if current_player == PLAYERS["P1"]:
        return PLAYERS["P2"]
    else:
        return PLAYERS["P1"]


def create_scoreboard():
    return {
        PLAYERS["P1"]: 0,
        PLAYERS["P2"]: 0,
        "draws": 0
    }


def update_score(scoreboard, result):
    if result == "draw":
        scoreboard["draws"] += 1
    else:
        scoreboard[result] += 1


def format_scoreboard(scoreboard):
    return (
        f"{PLAYERS['P1'].capitalize()}: {scoreboard[PLAYERS['P1']]}  |  "
        f"{PLAYERS['P2'].capitalize()}: {scoreboard[PLAYERS['P2']]}  |  "
        f"Draws: {scoreboard['draws']}"
    )


def record_move(move_history, row, col, piece):
    move = {
        "row": row,
        "col": col,
        "piece": piece
    }
    move_history.append(move)


def undo_last_move(board, move_history):
    if len(move_history) == 0:
        return None

    move = move_history.pop()

    row = move["row"]
    col = move["col"]

    board[row][col] = EMPTY

    return move


def roll_dice():
    return random.randint(0, COLS - 1)


def is_dice_turn():
    return random.random() < DICE_CHANCE


def get_dice_column(board):
    col = roll_dice()

    while not is_valid_column(board, col):
        col = roll_dice()

    return col


def is_bomb_drop():
    return random.random() < BOMB_CHANCE


def get_bomb_cells(row, col):
    cells = []

    for r in range(row - 1, row + 2):
        for c in range(col - 1, col + 2):
            if 0 <= r < ROWS and 0 <= c < COLS:
                cells.append((r, c))

    return cells


def explode_bomb(board, row, col):
    cells = get_bomb_cells(row, col)

    for r, c in cells:
        board[r][c] = EMPTY


if __name__ == "__main__":
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

    history = []
    record_move(history, row, 3, PLAYERS["P1"])
    print("Move history:", history)

    scoreboard = create_scoreboard()
    update_score(scoreboard, PLAYERS["P1"])
    print(format_scoreboard(scoreboard))

    undone = undo_last_move(board, history)
    print("Undone move:", undone)
    print_board(board)