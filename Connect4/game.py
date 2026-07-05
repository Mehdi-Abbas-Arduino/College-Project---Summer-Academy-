"""
main.py
--------
This is the file that actually runs the Connect 4 game -- arcade
edition. It draws the board with tkinter, handles mouse clicks, and
calls out to:
    - game_logic.py     for the rules of the game
    - sound_effects.py  for sound effects

There are three screens, all inside ONE window:
    1. Main Menu   -- title screen with a PLAY button
    2. Game Screen -- the board itself
    3. Game Over   -- shows who won (or a draw) with PLAY AGAIN /
                       MAIN MENU buttons, instead of a popup box

Every turn has a small random chance of being a DICE turn (the column
is rolled instead of clicked, shown with a die graphic, a dice-roll
sound, and a 1-second "DICE ROLL!" banner) and every dropped piece has
a small random chance of being a BOMB (shown with an explosion
animation + sound that clears the entire column).

Students: you should not need to edit this file. Once the functions in
game_logic.py are written correctly, running this file plays the game.

Run with:  python main.py
"""

import tkinter as tk

import skeleton_logic
import sound_effects

# ----------------------- SCREEN SIZE -----------------------
# The game runs in FULLSCREEN mode. All sizes are calculated
# dynamically from the actual screen resolution.

# These will be set at runtime once we know the screen dimensions.
SCREEN_WIDTH = 0
SCREEN_HEIGHT = 0
SCALE = 1.0
PADDING = 10
DIE_SIZE = 60
CELL_SIZE = 55

# Reference height the original design targeted (9:16 at 405 wide = 720 tall)
REFERENCE_HEIGHT = 720

# ----------------------- ARCADE COLOR PALETTE -----------------------
BG_COLOR = "#0d0d1a"          # near-black window background
BOARD_BG = "#1a1a2e"          # dark board background
EMPTY_CELL = "#14142b"        # empty slot color
NEON_CYAN = "#00fff7"
NEON_PINK = "#ff2bd6"
NEON_YELLOW = "#faff00"
NEON_GREEN = "#39ff14"
BOMB_FLASH = "#ff8800"
DIE_NEUTRAL = "#e8e8e8"       # neutral (non-neon) color for the dice pips
DIM_TEXT = "#7d7d9c"

ARCADE_FONT = "Courier New"

# Maps each piece value from game_logic.PLAYERS to a bright display
# color, so game_logic.py itself never has to know about hex codes.
DISPLAY_COLORS = {
    skeleton_logic.PLAYERS["P1"]: "#ff2b4d",   # neon red
    skeleton_logic.PLAYERS["P2"]: NEON_YELLOW,  # neon yellow
}

# Pip (dot) layouts for a die face, as (x_fraction, y_fraction) pairs.
DIE_PIPS = {
    1: [(0.5, 0.5)],
    2: [(0.25, 0.25), (0.75, 0.75)],
    3: [(0.25, 0.25), (0.5, 0.5), (0.75, 0.75)],
    4: [(0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75)],
    5: [(0.25, 0.25), (0.75, 0.25), (0.5, 0.5), (0.25, 0.75), (0.75, 0.75)],
    6: [(0.25, 0.25), (0.75, 0.25), (0.25, 0.5), (0.75, 0.5), (0.25, 0.75), (0.75, 0.75)],
    7: [(0.25, 0.25), (0.75, 0.25), (0.25, 0.5), (0.5, 0.5), (0.75, 0.5), (0.25, 0.75), (0.75, 0.75)],
}

root = None
board = skeleton_logic.create_board()
current_player = skeleton_logic.PLAYERS["P1"]
circles = []
canvas = None
dice_canvas = None
status_label = None
turn_is_dice = False
current_dice_column = None


def compute_sizes():
    """Recalculate all dynamic sizes from the actual screen resolution.
    
    The SCALE is based on screen HEIGHT (not width) because the board
    is the main visual element and its 6-row height is what constrains
    the layout. This prevents oversized fonts/elements on wide monitors.
    """
    global SCREEN_WIDTH, SCREEN_HEIGHT, SCALE, PADDING, DIE_SIZE, CELL_SIZE

    SCREEN_WIDTH = root.winfo_screenwidth()
    SCREEN_HEIGHT = root.winfo_screenheight()

    # Scale based on height so fonts/UI elements stay proportional
    SCALE = SCREEN_HEIGHT / REFERENCE_HEIGHT

    PADDING = round(8 * SCALE)
    DIE_SIZE = round(50 * SCALE)

    # Board gets ~65% of screen height. Calculate cell size from that.
    available_height = int(SCREEN_HEIGHT * 0.65)
    max_cell_h = (available_height - PADDING * 2) // skeleton_logic.ROWS

    # Also limit by width so the board doesn't overflow horizontally
    max_cell_w = (SCREEN_WIDTH - PADDING * 2) // skeleton_logic.COLS

    CELL_SIZE = min(max_cell_w, max_cell_h)


# ----------------------- SCREEN MANAGEMENT -----------------------
def clear_window():
    """Removes every widget currently in the window so a new screen
    can be built in its place."""
    for widget in root.winfo_children():
        widget.destroy()


def make_arcade_button(parent, text, color, command):
    """Builds a flat, neon-outlined button in the arcade style."""
    return tk.Button(
        parent, text=text, command=command,
        font=(ARCADE_FONT, round(14 * SCALE), "bold"),
        bg=BG_COLOR, fg=color,
        activebackground=color, activeforeground=BG_COLOR,
        relief="flat", bd=0,
        highlightthickness=2, highlightbackground=color, highlightcolor=color,
        padx=round(18 * SCALE), pady=round(10 * SCALE), cursor="hand2"
    )


def draw_glow_text(target_canvas, x, y, text, color, size=32):
    """
    Draws text with a simple neon 'glow' effect: several offset
    copies in the neon color behind a bright white copy on top.
    """
    f = (ARCADE_FONT, size, "bold")
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2), (-2, 2), (2, -2)]:
        target_canvas.create_text(x + dx, y + dy, text=text, font=f, fill=color)
    target_canvas.create_text(x, y, text=text, font=f, fill="white")


def show_banner(text, background):
    """
    Shows a short-lived banner across the top of the window (e.g.
    "DICE ROLL!") for 1 second, then removes itself automatically.
    """
    banner = tk.Label(
        root, text=text, font=(ARCADE_FONT, round(16 * SCALE), "bold"),
        bg=background, fg=BG_COLOR,
        padx=round(20 * SCALE), pady=round(8 * SCALE)
    )
    banner.place(relx=0.5, rely=0.02, anchor="n")
    root.after(1000, banner.destroy)


# ----------------------- MAIN MENU -----------------------
def show_menu_screen():
    clear_window()
    # Remove the game-over-only shortcuts (r / Enter) so they don't leak
    # into this screen. <Escape> stays bound globally the whole time.
    root.unbind("<r>")
    root.unbind("<R>")
    root.unbind("<Return>")
    root.configure(bg=BG_COLOR)
    root.title("CONNECT 4 -- ARCADE")

    # Center content vertically using a container frame
    container = tk.Frame(root, bg=BG_COLOR)
    container.place(relx=0.5, rely=0.5, anchor="center")

    title_w = round(400 * SCALE)
    title_h = round(80 * SCALE)
    title_canvas = tk.Canvas(container, width=title_w, height=title_h, bg=BG_COLOR, highlightthickness=0)
    title_canvas.pack(pady=(0, round(15 * SCALE)))
    draw_glow_text(title_canvas, title_w // 2, title_h // 2, "CONNECT 4", NEON_CYAN, size=round(36 * SCALE))

    tk.Label(container, text="RANDOM DICE ROLLS  *  SURPRISE BOMBS",
             font=(ARCADE_FONT, round(11 * SCALE), "bold"), bg=BG_COLOR, fg=NEON_PINK,
             wraplength=round(500 * SCALE), justify="center").pack(pady=(0, round(30 * SCALE)))

    make_arcade_button(container, "> PLAY <", NEON_GREEN, show_game_screen).pack(pady=round(10 * SCALE))

    tk.Label(container, text="Code Craft Edition", font=(ARCADE_FONT, round(10 * SCALE)),
             bg=BG_COLOR, fg=DIM_TEXT).pack(pady=(round(40 * SCALE), 0))

    # ESC hint at very bottom of screen
    tk.Label(root, text="PRESS ESC TO EXIT", font=(ARCADE_FONT, round(9 * SCALE)),
             bg=BG_COLOR, fg=DIM_TEXT).pack(side="bottom", pady=round(15 * SCALE))


# ----------------------- GAME SCREEN -----------------------
def draw_empty_board():
    """Draws an empty grid of dark circles with neon outlines."""
    global circles
    circles = []
    circle_gap = round(6 * SCALE)
    for row in range(skeleton_logic.ROWS):
        row_circles = []
        for col in range(skeleton_logic.COLS):
            x1 = col * CELL_SIZE + PADDING
            y1 = row * CELL_SIZE + PADDING
            x2 = x1 + CELL_SIZE - circle_gap
            y2 = y1 + CELL_SIZE - circle_gap
            circle = canvas.create_oval(x1, y1, x2, y2, fill=EMPTY_CELL,
                                         outline=NEON_CYAN, width=2)
            row_circles.append(circle)
        circles.append(row_circles)


def set_status(message):
    if status_label is not None:
        status_label.config(text=message)


def show_die(value):
    """Draws a die face (value 1-7) in the little dice canvas."""
    dice_canvas.delete("all")
    dice_canvas.create_rectangle(2, 2, DIE_SIZE - 2, DIE_SIZE - 2,
                                  fill=BOARD_BG, outline=NEON_CYAN, width=2)
    for (fx, fy) in DIE_PIPS[value]:
        x = fx * DIE_SIZE
        y = fy * DIE_SIZE
        r = round(5 * SCALE)
        dice_canvas.create_oval(x - r, y - r, x + r, y + r, fill=DIE_NEUTRAL, outline="")


def hide_die():
    dice_canvas.delete("all")


def animate_bomb(row, col, exploded_cells, on_done):
    """
    Plays a short explosion animation at (row, col): a bomb emoji
    appears, pauses briefly, flashes the affected cells orange, then
    clears them.
    """
    circle_gap = round(6 * SCALE)
    x1 = col * CELL_SIZE + PADDING
    y1 = row * CELL_SIZE + PADDING
    x2 = x1 + CELL_SIZE - circle_gap
    y2 = y1 + CELL_SIZE - circle_gap
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

    bomb_text = canvas.create_text(cx, cy, text="\U0001F4A3", font=("Arial", round(24 * SCALE)))
    canvas.itemconfig(circles[row][col], outline=BOMB_FLASH, width=4)

    def flash():
        for (r, c) in exploded_cells:
            canvas.itemconfig(circles[r][c], fill=BOMB_FLASH)
        canvas.after(180, clear)

    def clear():
        canvas.delete(bomb_text)
        for (r, c) in exploded_cells:
            canvas.itemconfig(circles[r][c], fill=EMPTY_CELL, outline=NEON_CYAN, width=2)
        on_done()

    canvas.after(400, flash)


def begin_turn():
    """
    Called at the start of every turn. Randomly decides if this turn
    is a dice turn, and if so, plays the dice sound, shows the
    "DICE ROLL!" banner, and displays the rolled die.
    """
    global turn_is_dice, current_dice_column

    turn_is_dice = skeleton_logic.is_dice_turn()
    player_num = 1 if current_player == skeleton_logic.PLAYERS["P1"] else 2

    if turn_is_dice:
        current_dice_column = skeleton_logic.get_dice_column(board)
        show_die(current_dice_column + 1)  # dice faces shown as 1-7
        sound_effects.play_dice_sound()
        show_banner("\U0001F3B2 DICE ROLL!", NEON_CYAN)
        set_status(f"P{player_num} -- DICE ROLLED COLUMN {current_dice_column}! CLICK TO DROP")
    else:
        current_dice_column = None
        hide_die()
        set_status(f"P{player_num}'S TURN -- CLICK A COLUMN")


def finish_turn():
    """
    Runs after a piece has fully landed (and any bomb animation has
    finished): checks for a winner, checks for a draw, or starts the
    next turn.
    """
    global current_player

    if skeleton_logic.check_winner(board, current_player):
        sound_effects.play_win_sounds()
        show_game_over_screen(current_player)
        return

    if skeleton_logic.is_board_full(board):
        show_game_over_screen(None)
        return

    current_player = skeleton_logic.switch_player(current_player)
    begin_turn()


def attempt_drop(col):
    """
    Handles dropping a piece into 'col': placing it, and handling a
    bomb if this drop turns out to be one. Control passes to
    finish_turn() either immediately or after the bomb animation ends.
    """
    global current_player

    if not skeleton_logic.is_valid_column(board, col):
        return

    row = skeleton_logic.get_next_open_row(board, col)
    skeleton_logic.drop_piece(board, row, col, current_player)
    canvas.itemconfig(circles[row][col], fill=DISPLAY_COLORS[current_player])
    sound_effects.play_drop_sound()

    if skeleton_logic.is_bomb_drop():
        exploded_cells = skeleton_logic.get_bomb_cells(row, col)
        skeleton_logic.explode_bomb(board, row, col)   # board data updates now
        sound_effects.play_bomb_sound()
        show_banner("\U0001F4A3 BOOM!", BOMB_FLASH)
        set_status("BOOM! BOMB PIECE!")
        animate_bomb(row, col, exploded_cells, finish_turn)  # visual, then continue
    else:
        finish_turn()


def handle_click(event):
    """
    On a dice turn, any click drops into the rolled column. On a
    normal turn, the column clicked is the column played.
    """
    if turn_is_dice:
        attempt_drop(current_dice_column)
    else:
        col = (event.x - PADDING) // CELL_SIZE
        if col < 0 or col >= skeleton_logic.COLS:
            return
        attempt_drop(col)


def reset_game():
    """Quick in-place reset (right-click) without leaving the game screen."""
    global board, current_player
    board = skeleton_logic.create_board()
    current_player = skeleton_logic.PLAYERS["P1"]
    for row in range(skeleton_logic.ROWS):
        for col in range(skeleton_logic.COLS):
            canvas.itemconfig(circles[row][col], fill=EMPTY_CELL, outline=NEON_CYAN, width=2)
    begin_turn()


def show_game_screen():
    """Builds (or rebuilds, for Play Again) the game screen."""
    global canvas, dice_canvas, status_label, board, current_player

    clear_window()
    # Remove the game-over-only shortcuts (r / Enter) so they don't leak
    # into gameplay. <Escape> stays bound globally the whole time.
    root.unbind("<r>")
    root.unbind("<R>")
    root.unbind("<Return>")
    root.configure(bg=BG_COLOR)
    root.title("CONNECT 4 -- ARCADE")

    board = skeleton_logic.create_board()
    current_player = skeleton_logic.PLAYERS["P1"]

    # --- Top bar: dice + status, centered ---
    top_frame = tk.Frame(root, bg=BG_COLOR)
    top_frame.pack(pady=(round(15 * SCALE), round(8 * SCALE)))

    dice_canvas = tk.Canvas(top_frame, width=DIE_SIZE, height=DIE_SIZE,
                             bg=BG_COLOR, highlightthickness=0)
    dice_canvas.pack(side="left", padx=round(10 * SCALE))

    status_label = tk.Label(top_frame, text="", font=(ARCADE_FONT, round(11 * SCALE), "bold"),
                             bg=BG_COLOR, fg=NEON_CYAN, wraplength=round(500 * SCALE), justify="left")
    status_label.pack(side="left")

    # --- Board canvas, centered ---
    board_width = CELL_SIZE * skeleton_logic.COLS + PADDING * 2
    board_height = CELL_SIZE * skeleton_logic.ROWS + PADDING * 2

    canvas = tk.Canvas(root, width=board_width, height=board_height, bg=BOARD_BG,
                        highlightthickness=4, highlightbackground=NEON_PINK)
    canvas.pack(pady=(0, round(8 * SCALE)))

    draw_empty_board()
    canvas.bind("<Button-1>", handle_click)
    canvas.bind("<Button-3>", lambda e: reset_game())

    # Bottom instructions
    tk.Label(root, text="RIGHT-CLICK TO RESET  |  LEFT-CLICK A COLUMN TO DROP  |  ESC TO EXIT",
             font=(ARCADE_FONT, round(9 * SCALE)), bg=BG_COLOR, fg=DIM_TEXT,
             justify="center").pack(side="bottom", pady=round(15 * SCALE))

    begin_turn()


# ----------------------- GAME OVER SCREEN -----------------------
def show_game_over_screen(winner):
    """
    Shown instead of a popup box when the game ends. 'winner' is a
    piece color string (e.g. "red") for a win, or None for a draw.
    """
    clear_window()
    root.configure(bg=BG_COLOR)
    root.title("GAME OVER -- ARCADE")

    # Center content vertically
    container = tk.Frame(root, bg=BG_COLOR)
    container.place(relx=0.5, rely=0.45, anchor="center")

    over_w = round(450 * SCALE)
    over_h = round(80 * SCALE)
    over_canvas = tk.Canvas(container, width=over_w, height=over_h, bg=BG_COLOR, highlightthickness=0)
    over_canvas.pack(pady=(0, round(15 * SCALE)))

    if winner is None:
        draw_glow_text(over_canvas, over_w // 2, over_h // 2, "IT'S A DRAW!", NEON_YELLOW, size=round(30 * SCALE))
    else:
        player_num = 1 if winner == skeleton_logic.PLAYERS["P1"] else 2
        draw_glow_text(over_canvas, over_w // 2, over_h // 2, f"PLAYER {player_num} WINS!",
                        DISPLAY_COLORS[winner], size=round(28 * SCALE))

    btn_frame = tk.Frame(container, bg=BG_COLOR)
    btn_frame.pack(pady=round(30 * SCALE))

    make_arcade_button(btn_frame, "PLAY AGAIN", NEON_GREEN, show_game_screen).pack(pady=round(8 * SCALE))
    # "Main Menu" here means the arcade hub, not Connect 4's own splash
    # screen -- closing the window returns control to launcher.py, which
    # then brings the (minimized) arcade hub window back to the front.
    make_arcade_button(btn_frame, "MAIN MENU", NEON_PINK, root.destroy).pack(pady=round(8 * SCALE))

    # Keyboard shortcuts, in addition to clicking the buttons above.
    root.bind("<r>", lambda e: show_game_screen())
    root.bind("<R>", lambda e: show_game_screen())
    root.bind("<Return>", lambda e: show_game_screen())
    # <Escape> is already bound globally (in start_game) to close the
    # window, which also returns to the arcade hub.

    tk.Label(root, text="R / ENTER  PLAY AGAIN   |   ESC  MAIN MENU   |   OR CLICK A BUTTON",
             font=(ARCADE_FONT, round(9 * SCALE)), bg=BG_COLOR, fg=DIM_TEXT,
             justify="center").pack(side="bottom", pady=round(15 * SCALE))


# ----------------------- ENTRY POINT -----------------------
def start_game():
    global root
    root = tk.Tk()

    # Compute dynamic sizes based on actual screen resolution
    compute_sizes()

    # Go fullscreen
    root.attributes("-fullscreen", True)
    root.configure(bg=BG_COLOR)

    # Escape key exits the game
    root.bind("<Escape>", lambda e: root.destroy())

    show_menu_screen()
    root.mainloop()


if __name__ == "__main__":
    start_game()
