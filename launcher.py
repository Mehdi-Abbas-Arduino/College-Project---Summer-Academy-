"""
ARCADE HUB – Unified Game Launcher
====================================
A single entry-point that presents a neon arcade main menu where the
player enters their name first, then picks which of the three games
to play.  Each game runs as a subprocess so a crash in one never
blocks the others.

Run with:  python launcher.py
"""

import os
import sys
import subprocess
import pygame

# =============================================================
# CONFIG
# =============================================================

WIDTH, HEIGHT = 800, 600
FPS = 60

# ---- neon color palette (matches Ping Pong) ----
BG_DARK      = (8,   8,  22)
BG_PANEL     = (14,  14,  34)
NEON_CYAN    = (60, 240, 255)
NEON_MAGENTA = (255,  60, 180)
NEON_YELLOW  = (255, 225,  70)
NEON_GREEN   = (90,  255, 160)
NEON_ORANGE  = (255, 160,  40)
WALL_COLOR   = (70,   90, 140)
TEXT_MAIN    = (235, 240, 255)
TEXT_DIM     = (120, 130, 165)
GRID_COLOR   = (24,   26,  52)
ERROR_COLOR  = (255,  70,  70)

# game directories (relative to this file)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GAME_DIRS = {
    "pong":    os.path.join(BASE_DIR, "Ping Pong"),
    "connect4": os.path.join(BASE_DIR, "Connect4"),
    "flappy":  os.path.join(BASE_DIR, "Flappy Bird"),
}
GAME_SCRIPTS = {
    "pong":    "game.py",
    "connect4": "game.py",
    "flappy":  "game.py",
}

RESERVED_USERNAMES = ["ADMIN", "TEST", "GUEST", "PLAYER1"]


# =============================================================
# DRAWING HELPERS  (same style as Ping Pong)
# =============================================================

def draw_grid_background(screen, top, height):
    for x in range(0, WIDTH, 40):
        pygame.draw.line(screen, GRID_COLOR, (x, top), (x, top + height))
    for y in range(top, top + height, 40):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))


def draw_glow_circle(screen, color, center, radius):
    glow = pygame.Surface((radius * 6, radius * 6), pygame.SRCALPHA)
    gx, gy = radius * 3, radius * 3
    for i in range(3, 0, -1):
        alpha = 26 * i
        pygame.draw.circle(glow, (*color, alpha), (gx, gy), radius + i * 4)
    screen.blit(glow, (center[0] - gx, center[1] - gy))
    pygame.draw.circle(screen, color, center, radius)


def draw_glow_rect(screen, color, rect, border_radius=8):
    glow = pygame.Surface((rect.width + 40, rect.height + 40), pygame.SRCALPHA)
    for i in range(3, 0, -1):
        alpha = 22 * i
        pad = i * 4
        pygame.draw.rect(
            glow, (*color, alpha),
            (20 - pad, 20 - pad, rect.width + pad * 2, rect.height + pad * 2),
            border_radius=border_radius,
        )
    screen.blit(glow, (rect.x - 20, rect.y - 20))
    pygame.draw.rect(screen, color, rect, border_radius=border_radius)


def draw_glow_text(screen, font, text, color, center, glow_color=None):
    glow_color = glow_color or color
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
        faint = font.render(text, True, glow_color)
        faint.set_alpha(40)
        rect = faint.get_rect(center=(center[0] + dx, center[1] + dy))
        screen.blit(faint, rect)
    final = font.render(text, True, color)
    rect = final.get_rect(center=center)
    screen.blit(final, rect)


def draw_outlined_rect(screen, color, rect, width=2, border_radius=8):
    pygame.draw.rect(screen, BG_PANEL, rect, border_radius=border_radius)
    pygame.draw.rect(screen, color, rect, width, border_radius=border_radius)


# =============================================================
# NAME VALIDATION  (same rules as Ping Pong)
# =============================================================

def validate_name(name):
    if len(name) < 2 or len(name) > 16:
        return False, "Name must be 2-16 characters."
    if not name.replace(" ", "").isalpha():
        return False, "Letters and spaces only."
    if name.upper() in RESERVED_USERNAMES:
        return False, "That name is reserved."
    return True, ""


# =============================================================
# GAME CARDS DATA
# =============================================================

GAMES = [
    {
        "key": "pong",
        "title": "SOLO PONG",
        "tagline": "Paddle • Bounce • Survive",
        "icon": "🏓",
        "color": NEON_GREEN,
        "hotkey": pygame.K_1,
    },
    {
        "key": "connect4",
        "title": "CONNECT 4",
        "tagline": "Dice Rolls • Surprise Bombs",
        "icon": "🔴",
        "color": NEON_MAGENTA,
        "hotkey": pygame.K_2,
    },
    {
        "key": "flappy",
        "title": "FLAPPY BIRD",
        "tagline": "Tap • Fly • Don't Crash",
        "icon": "🐦",
        "color": NEON_YELLOW,
        "hotkey": pygame.K_3,
    },
]


# =============================================================
# LAUNCH GAME
# =============================================================

def launch_game(game_key, player_name):
    """Launch a game as a subprocess.  Returns (success, error_msg)."""
    game_dir = GAME_DIRS.get(game_key)
    script   = GAME_SCRIPTS.get(game_key)
    if not game_dir or not script:
        return False, "Unknown game."

    script_path = os.path.join(game_dir, script)
    if not os.path.isfile(script_path):
        return False, f"{script} not found."

    env = os.environ.copy()
    env["ARCADE_PLAYER_NAME"] = player_name

    try:
        proc = subprocess.Popen(
            [sys.executable, script_path],
            cwd=game_dir,
            env=env,
        )
        proc.wait()  # block until the child game window closes
        return True, ""
    except Exception as exc:
        return False, str(exc)[:60]


# =============================================================
# SCREENS
# =============================================================

def name_entry_screen(screen, clock):
    """Show the name entry screen.  Returns the validated player name."""
    font       = pygame.font.SysFont("consolas", 22, bold=True)
    big_font   = pygame.font.SysFont("consolas", 52, bold=True)
    small_font = pygame.font.SysFont("consolas", 16, bold=True)
    tiny_font  = pygame.font.SysFont("consolas", 13, bold=True)

    input_text  = ""
    input_error = ""
    blink_timer = 0
    blink_on    = True
    pulse_y     = 470.0
    pulse_dir   = -1

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_BACKSPACE:
                    input_text  = input_text[:-1]
                    input_error = ""
                elif event.key == pygame.K_RETURN:
                    ok, err = validate_name(input_text)
                    if ok:
                        return input_text
                    else:
                        input_error = err
                elif event.unicode.isprintable() and len(input_text) < 16:
                    input_text += event.unicode
                    input_error = ""

        # ---- animation ----
        blink_timer += 1
        if blink_timer >= 30:
            blink_timer = 0
            blink_on = not blink_on

        pulse_y += pulse_dir * 2
        if pulse_y <= 450:
            pulse_dir = 1
        elif pulse_y >= 490:
            pulse_dir = -1

        # ---- draw ----
        screen.fill(BG_DARK)
        draw_grid_background(screen, 0, HEIGHT)

        draw_glow_text(screen, big_font, "ARCADE HUB", NEON_CYAN,
                       (WIDTH // 2, 120))

        # subtitle
        sub = small_font.render("3  G A M E S  •  1  L A U N C H E R", True, TEXT_DIM)
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 170))

        # prompt
        prompt = font.render("ENTER YOUR NAME", True, TEXT_MAIN)
        screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 250))

        # input box
        box = pygame.Rect(WIDTH // 2 - 160, 290, 320, 46)
        draw_outlined_rect(screen, NEON_MAGENTA, box)
        cursor = "_" if blink_on else " "
        txt = font.render(input_text + cursor, True, TEXT_MAIN)
        screen.blit(txt, (box.x + 14, box.y + 10))

        # error
        if input_error:
            err = small_font.render(input_error, True, NEON_MAGENTA)
            screen.blit(err, (WIDTH // 2 - err.get_width() // 2, 344))

        # hint
        if blink_on:
            hint = font.render("PRESS ENTER TO CONTINUE", True, NEON_YELLOW)
            screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 420))

        # bouncing dot
        draw_glow_circle(screen, NEON_GREEN, (WIDTH // 2, int(pulse_y)), 6)

        # footer
        esc = tiny_font.render("ESC TO EXIT", True, TEXT_DIM)
        screen.blit(esc, (WIDTH // 2 - esc.get_width() // 2, HEIGHT - 30))

        pygame.display.flip()
        clock.tick(FPS)


def game_selection_screen(screen, clock, player_name):
    """Show the game selection screen.  Returns the chosen game key or None (ESC)."""
    font       = pygame.font.SysFont("consolas", 22, bold=True)
    big_font   = pygame.font.SysFont("consolas", 36, bold=True)
    small_font = pygame.font.SysFont("consolas", 15, bold=True)
    tiny_font  = pygame.font.SysFont("consolas", 13, bold=True)
    icon_font  = pygame.font.SysFont("segoeUIemoji", 36)

    # card layout
    card_w, card_h = 600, 100
    card_x  = WIDTH // 2 - card_w // 2
    card_gap = 20
    total_h  = len(GAMES) * card_h + (len(GAMES) - 1) * card_gap
    start_y  = 200

    hovered = -1      # index of card under mouse
    error_msg = ""
    error_timer = 0

    while True:
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None   # go back to name entry
                for i, g in enumerate(GAMES):
                    if event.key == g["hotkey"]:
                        return g["key"]

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, g in enumerate(GAMES):
                    cy = start_y + i * (card_h + card_gap)
                    rect = pygame.Rect(card_x, cy, card_w, card_h)
                    if rect.collidepoint(mx, my):
                        return g["key"]

        # ---- draw ----
        screen.fill(BG_DARK)
        draw_grid_background(screen, 0, HEIGHT)

        # welcome
        draw_glow_text(screen, big_font, "SELECT YOUR GAME", NEON_CYAN,
                       (WIDTH // 2, 70))
        welcome = font.render(f"WELCOME, {player_name.upper()}", True, NEON_GREEN)
        screen.blit(welcome, (WIDTH // 2 - welcome.get_width() // 2, 120))

        # cards
        for i, g in enumerate(GAMES):
            cy = start_y + i * (card_h + card_gap)
            rect = pygame.Rect(card_x, cy, card_w, card_h)
            is_hovered = rect.collidepoint(mx, my)

            if is_hovered:
                # glow behind card
                draw_glow_rect(screen, g["color"], rect, border_radius=12)
            else:
                draw_outlined_rect(screen, g["color"], rect, width=2, border_radius=12)

            # hotkey badge
            badge_rect = pygame.Rect(card_x + 16, cy + card_h // 2 - 18, 36, 36)
            pygame.draw.rect(screen, g["color"], badge_rect, border_radius=6)
            num = font.render(str(i + 1), True, BG_DARK)
            screen.blit(num, (badge_rect.x + badge_rect.width // 2 - num.get_width() // 2,
                              badge_rect.y + badge_rect.height // 2 - num.get_height() // 2))

            # icon (emoji)
            try:
                icon_surf = icon_font.render(g["icon"], True, g["color"])
                screen.blit(icon_surf, (card_x + 68, cy + card_h // 2 - icon_surf.get_height() // 2))
            except Exception:
                pass  # emoji rendering can fail on some systems

            # title
            title = font.render(g["title"], True, TEXT_MAIN)
            screen.blit(title, (card_x + 120, cy + 20))

            # tagline
            tag = small_font.render(g["tagline"], True, TEXT_DIM)
            screen.blit(tag, (card_x + 120, cy + 55))

        # error toast
        if error_msg and error_timer > 0:
            error_timer -= 1
            err_surf = font.render(error_msg, True, ERROR_COLOR)
            screen.blit(err_surf, (WIDTH // 2 - err_surf.get_width() // 2, HEIGHT - 80))

        # footer
        foot = tiny_font.render("ESC  BACK  •  1 / 2 / 3  OR  CLICK TO PLAY", True, TEXT_DIM)
        screen.blit(foot, (WIDTH // 2 - foot.get_width() // 2, HEIGHT - 30))

        pygame.display.flip()
        clock.tick(FPS)


# =============================================================
# MAIN LOOP
# =============================================================

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("ARCADE HUB")
    clock = pygame.time.Clock()

    while True:
        # 1) Name entry
        player_name = name_entry_screen(screen, clock)

        while True:
            # 2) Game selection
            choice = game_selection_screen(screen, clock, player_name)
            if choice is None:
                # ESC pressed — go back to name entry
                break

            # 3) Launch the chosen game
            #    Minimize the launcher while the game runs
            pygame.display.iconify()

            success, err = launch_game(choice, player_name)

            # Restore the launcher window.
            # NOTE: simply calling pygame.display.set_mode() again is not
            # enough here -- on many OS/window-manager combos, SDL keeps
            # reusing the same (still-minimized) window handle, so the
            # hub would stay hidden in the taskbar even though a new
            # surface was created. Fully tearing down and reinitializing
            # the display subsystem forces SDL to create a brand new,
            # un-minimized, focused window.
            pygame.display.quit()
            pygame.display.init()
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("ARCADE HUB")
            pygame.event.clear()
            pygame.event.pump()

            if not success:
                # The game_selection_screen will be re-drawn;
                # we show the error briefly via a quick overlay
                font = pygame.font.SysFont("consolas", 20, bold=True)
                screen.fill(BG_DARK)
                draw_grid_background(screen, 0, HEIGHT)
                err_text = f"COULD NOT LAUNCH: {err}"
                err_surf = font.render(err_text, True, ERROR_COLOR)
                screen.blit(err_surf, (WIDTH // 2 - err_surf.get_width() // 2,
                                       HEIGHT // 2))
                hint = font.render("PRESS ANY KEY TO CONTINUE", True, TEXT_DIM)
                screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2,
                                   HEIGHT // 2 + 40))
                pygame.display.flip()

                # wait for keypress
                waiting = True
                while waiting:
                    for ev in pygame.event.get():
                        if ev.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if ev.type == pygame.KEYDOWN:
                            waiting = False

    pygame.quit()


if __name__ == "__main__":
    main()
