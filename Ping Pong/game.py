"""
Single Player Pong
800x600 PyGame window with three states: MAIN_MENU, GAMEPLAY, LEADERBOARD.
"""

import os
import random
import pygame
from functions_unsolved import (   # swap to functions_unsolved to test stubs
    reflect_vector,
    is_out_of_bounds,
    clamp_paddle_movement,
    get_quadrant_occupancy,
    shorten_player_name,
    check_username_availability,
    validate_name_constraints,
    generate_seed_hash,
    find_longest_volley,
    calculate_weighted_score,
    determine_winning_player,
    calculate_game_analytics,
    get_score_milestone_multipliers,
)

# =============================================================
# CONFIG
# =============================================================

WIDTH, HEIGHT = 800, 600
FPS = 60

HUD_HEIGHT = 80
PLAY_TOP = HUD_HEIGHT
PLAY_HEIGHT = HEIGHT - HUD_HEIGHT

WALL_THICKNESS = 16
BALL_RADIUS = 10
PADDLE_W, PADDLE_H = 15, 100
PADDLE_X = WIDTH - WALL_THICKNESS - PADDLE_W - 14
PADDLE_MAX_SPEED = 10
BASE_BALL_SPEED = 5.0
STARTING_LIVES = 3
MILESTONES = [25, 75, 150, 300]
RESERVED_USERNAMES = ["ADMIN", "TEST", "GUEST", "PLAYER1"]

# ---- neon color palette ----
BG_DARK      = (8,   8,  22)
BG_PANEL     = (14,  14,  34)
NEON_CYAN    = (60, 240, 255)
NEON_MAGENTA = (255,  60, 180)
NEON_YELLOW  = (255, 225,  70)
NEON_GREEN   = (90,  255, 160)
WALL_COLOR   = (70,   90, 140)
TEXT_MAIN    = (235, 240, 255)
TEXT_DIM     = (120, 130, 165)
GRID_COLOR   = (24,   26,  52)

# kept for backward compatibility
WHITE  = TEXT_MAIN
BLACK  = BG_DARK
GREEN  = NEON_GREEN
RED    = NEON_MAGENTA
YELLOW = NEON_YELLOW
GRAY   = TEXT_DIM
BLUE   = NEON_CYAN


def new_ball():
    dx = random.choice([-1, 1]) * BASE_BALL_SPEED
    dy = random.uniform(-BASE_BALL_SPEED, BASE_BALL_SPEED)
    return float(WIDTH // 2), float(PLAY_HEIGHT // 2), dx, dy


# =============================================================
# DRAWING HELPERS
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


def draw_glow_rect(screen, color, rect):
    glow = pygame.Surface((rect.width + 40, rect.height + 40), pygame.SRCALPHA)
    for i in range(3, 0, -1):
        alpha = 22 * i
        pad = i * 4
        pygame.draw.rect(
            glow, (*color, alpha),
            (20 - pad, 20 - pad, rect.width + pad * 2, rect.height + pad * 2),
            border_radius=6,
        )
    screen.blit(glow, (rect.x - 20, rect.y - 20))
    pygame.draw.rect(screen, color, rect, border_radius=4)


def draw_glow_text(screen, font, text, color, center, glow_color=None):
    glow_color = glow_color or color
    base = font.render(text, True, glow_color)
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
        faint = font.render(text, True, (*glow_color[:3],))
        faint.set_alpha(40)
        rect = faint.get_rect(center=(center[0] + dx, center[1] + dy))
        screen.blit(faint, rect)
    final = font.render(text, True, color)
    rect = final.get_rect(center=center)
    screen.blit(final, rect)


def draw_hud(screen, font, small_font, player_name, score, lives, hits):
    hud_rect = pygame.Rect(0, 0, WIDTH, HUD_HEIGHT)
    pygame.draw.rect(screen, BG_PANEL, hud_rect)
    pygame.draw.line(screen, NEON_CYAN, (0, HUD_HEIGHT), (WIDTH, HUD_HEIGHT), 2)

    name_surf = font.render(f"{player_name}", True, NEON_CYAN)
    screen.blit(name_surf, (24, HUD_HEIGHT // 2 - name_surf.get_height() // 2))

    title_surf = small_font.render("S O L O   P O N G", True, TEXT_DIM)
    screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 12))

    score_surf = font.render(f"SCORE {score}", True, NEON_YELLOW)
    screen.blit(score_surf, (WIDTH // 2 - score_surf.get_width() // 2, 34))

    lives_text = "♥ " * lives if lives > 0 else "-"
    lives_surf = font.render(lives_text, True, NEON_MAGENTA)
    screen.blit(lives_surf, (WIDTH - lives_surf.get_width() - 24, 12))

    hits_surf = small_font.render(f"HITS {hits}", True, TEXT_DIM)
    screen.blit(hits_surf, (WIDTH - hits_surf.get_width() - 24, 44))


def draw_play_field(screen, paddle_y, ball_x, ball_y):
    field_rect = pygame.Rect(0, PLAY_TOP, WIDTH, PLAY_HEIGHT)
    pygame.draw.rect(screen, BG_DARK, field_rect)
    draw_grid_background(screen, PLAY_TOP, PLAY_HEIGHT)

    for y in range(PLAY_TOP + 10, PLAY_TOP + PLAY_HEIGHT - 10, 24):
        pygame.draw.rect(screen, (40, 44, 80), (WIDTH // 2 - 2, y, 4, 12))

    pygame.draw.rect(screen, WALL_COLOR, (0, PLAY_TOP, WIDTH, WALL_THICKNESS))
    pygame.draw.rect(screen, WALL_COLOR,
                     (0, PLAY_TOP + PLAY_HEIGHT - WALL_THICKNESS, WIDTH, WALL_THICKNESS))
    pygame.draw.rect(screen, WALL_COLOR, (0, PLAY_TOP, WALL_THICKNESS, PLAY_HEIGHT))

    paddle_rect = pygame.Rect(PADDLE_X, PLAY_TOP + paddle_y, PADDLE_W, PADDLE_H)
    draw_glow_rect(screen, NEON_GREEN, paddle_rect)

    draw_glow_circle(screen, NEON_YELLOW,
                     (int(ball_x), PLAY_TOP + int(ball_y)), BALL_RADIUS)

    pygame.draw.rect(screen, NEON_CYAN, field_rect, 2)


def draw_menu(screen, font, big_font, small_font,
              input_text, input_error, blink_on, pulse_y):
    screen.fill(BG_DARK)
    draw_grid_background(screen, 0, HEIGHT)

    draw_glow_text(screen, big_font, "SOLO PONG", NEON_CYAN, (WIDTH // 2, 130), NEON_CYAN)

    prompt_surf = font.render("ENTER YOUR NAME", True, TEXT_MAIN)
    screen.blit(prompt_surf,
                (WIDTH // 2 - prompt_surf.get_width() // 2, 250))

    box_rect = pygame.Rect(WIDTH // 2 - 160, 290, 320, 46)
    pygame.draw.rect(screen, BG_PANEL, box_rect, border_radius=8)
    pygame.draw.rect(screen, NEON_MAGENTA, box_rect, 2, border_radius=8)

    cursor = "_" if blink_on else " "
    text_surf = font.render(input_text + cursor, True, TEXT_MAIN)
    screen.blit(text_surf, (box_rect.x + 14, box_rect.y + 10))

    if input_error:
        err_surf = small_font.render(input_error, True, NEON_MAGENTA)
        screen.blit(err_surf,
                    (WIDTH // 2 - err_surf.get_width() // 2, 344))

    if blink_on:
        hint_surf = font.render("PRESS ENTER TO START", True, NEON_YELLOW)
        screen.blit(hint_surf,
                    (WIDTH // 2 - hint_surf.get_width() // 2, 420))

    draw_glow_circle(screen, NEON_GREEN, (WIDTH // 2, pulse_y), 6)


_FONT_CACHE = {}


def get_font(size):
    if size not in _FONT_CACHE:
        _FONT_CACHE[size] = pygame.font.SysFont("consolas", size, bold=True)
    return _FONT_CACHE[size]


def fit_text_render(screen, text, x, y, max_width, base_size, color):
    """Render text, shrinking the font until it fits max_width."""
    size = base_size
    rendered_font = get_font(size)
    width, _ = rendered_font.size(text)
    while width > max_width and size > 10:
        size -= 2
        rendered_font = get_font(size)
        width, _ = rendered_font.size(text)
    surf = rendered_font.render(text, True, color)
    screen.blit(surf, (x, y))


def get_leaderboard_buttons():
    """Returns (restart_rect, main_menu_rect) for the leaderboard screen.
    Shared by drawing code and mouse click-detection so they always agree."""
    btn_y = HEIGHT - 90
    r_box = pygame.Rect(WIDTH // 2 - 260, btn_y, 240, 36)
    m_box = pygame.Rect(WIDTH // 2 + 20, btn_y, 240, 36)
    return r_box, m_box


def draw_leaderboard(screen, font, big_font, small_font, last_result):
    screen.fill(BG_DARK)
    draw_grid_background(screen, 0, HEIGHT)

    draw_glow_text(screen, big_font, "GAME OVER",
                   NEON_MAGENTA, (WIDTH // 2, 60), NEON_MAGENTA)

    panel_width, panel_height = 640, 360
    panel_rect = pygame.Rect(WIDTH // 2 - panel_width // 2, 100,
                             panel_width, panel_height)
    pygame.draw.rect(screen, BG_PANEL, panel_rect, border_radius=12)
    pygame.draw.rect(screen, NEON_CYAN, panel_rect, 2, border_radius=12)

    analytics      = last_result.get("analytics", {})
    quadrants      = last_result.get("quadrant_counts", {})
    quadrant_text  = " ".join(f"Q{k}:{v}" for k, v in sorted(quadrants.items()))

    rows = [
        ("PLAYER",        f"{last_result.get('name', '')} ({last_result.get('initials', '')})"),
        ("SCORE",         str(last_result.get("score", 0))),
        ("WEIGHTED SCORE",str(last_result.get("weighted_score", 0))),
        ("HITS / MISSES", f"{last_result.get('hits', 0)} / {last_result.get('misses', 0)}"),
        ("LONGEST VOLLEY",str(last_result.get("longest_volley", 0))),
        ("AVG HIT SPEED", f"{analytics.get('average_speed', 0):.2f} ({analytics.get('hit_count', 0)} hits)"),
        ("QUADRANT TIME", quadrant_text),
        ("REPLAY SEED",   str(last_result.get("seed_hash", ""))),
        ("SESSION WINNER",str(last_result.get("winner", ""))),
    ]

    left_pad, col_gap, top_pad, row_h = 28, 24, 26, 60
    col_width = (panel_width - left_pad * 2 - col_gap) // 2
    col_x = [panel_rect.x + left_pad,
              panel_rect.x + left_pad + col_width + col_gap]

    for i, (label, value) in enumerate(rows):
        col = i % 2
        row = i // 2
        x   = col_x[col]
        y   = panel_rect.y + top_pad + row * row_h

        label_surf = small_font.render(label, True, TEXT_DIM)
        screen.blit(label_surf, (x, y))
        fit_text_render(screen, value, x, y + 22,
                        col_width, base_size=18, color=TEXT_MAIN)

    # --- Restart / Main Menu choice buttons ---
    r_box, m_box = get_leaderboard_buttons()
    # Restart button
    pygame.draw.rect(screen, BG_PANEL, r_box, border_radius=8)
    pygame.draw.rect(screen, NEON_GREEN, r_box, 2, border_radius=8)
    r_label = small_font.render("R / CLICK   PLAY AGAIN", True, NEON_GREEN)
    screen.blit(r_label, (r_box.x + r_box.width // 2 - r_label.get_width() // 2,
                          r_box.y + r_box.height // 2 - r_label.get_height() // 2))
    # Main menu button
    pygame.draw.rect(screen, BG_PANEL, m_box, border_radius=8)
    pygame.draw.rect(screen, NEON_MAGENTA, m_box, 2, border_radius=8)
    m_label = small_font.render("ESC / CLICK   MAIN MENU", True, NEON_MAGENTA)
    screen.blit(m_label, (m_box.x + m_box.width // 2 - m_label.get_width() // 2,
                          m_box.y + m_box.height // 2 - m_label.get_height() // 2))

    hint_surf = small_font.render("CLICK A BUTTON OR PRESS A KEY", True, NEON_YELLOW)
    screen.blit(hint_surf,
                (WIDTH // 2 - hint_surf.get_width() // 2, HEIGHT - 40))


# =============================================================
# MAIN LOOP
# =============================================================

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Solo Pong")
    clock      = pygame.time.Clock()
    font       = pygame.font.SysFont("consolas", 22, bold=True)
    big_font   = pygame.font.SysFont("consolas", 54, bold=True)
    small_font = pygame.font.SysFont("consolas", 16, bold=True)

    # Check if launched from the arcade hub
    launched_from_hub = False
    hub_player_name = os.environ.get("ARCADE_PLAYER_NAME", "")

    game_state = "MAIN_MENU"

    input_text   = ""
    input_error  = ""
    used_usernames      = []
    leaderboard_history = {}

    # simple animated dot for the menu screen
    demo_pulse_y = 470
    pulse_direction = -1          # -1 = moving up, +1 = moving down
    blink_timer = 0
    blink_on    = True

    player_name  = ""
    score        = 0
    lives        = STARTING_LIVES
    hits         = 0
    misses       = 0
    paddle_y     = PLAY_HEIGHT // 2 - PADDLE_H // 2
    ball_x, ball_y, ball_dx, ball_dy = new_ball()
    scoreboard       = {"score": 0}
    game_history     = []
    score_events     = []
    performance_log  = []
    quadrant_counts  = {1: 0, 2: 0, 3: 0, 4: 0}
    last_result      = {}

    # If launched from hub, skip straight to gameplay
    if hub_player_name:
        launched_from_hub = True
        player_name = hub_player_name
        used_usernames.append(player_name)
        game_state = "GAMEPLAY"

    running = True
    while running:
        # ---- events ----------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif game_state == "MAIN_MENU":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        input_text  = input_text[:-1]
                        input_error = ""
                    elif event.key == pygame.K_RETURN:
                        if not validate_name_constraints(input_text):
                            input_error = "Name must be 2-16 letters only."
                        elif check_username_availability(
                                input_text, RESERVED_USERNAMES):
                            input_error = "That name is reserved, try another."
                        else:
                            player_name = input_text
                            used_usernames.append(player_name)
                            score           = 0
                            lives           = STARTING_LIVES
                            hits            = 0
                            misses          = 0
                            paddle_y        = PLAY_HEIGHT // 2 - PADDLE_H // 2
                            ball_x, ball_y, ball_dx, ball_dy = new_ball()
                            scoreboard      = {"score": 0}
                            game_history    = []
                            score_events    = []
                            performance_log = []
                            quadrant_counts = {1: 0, 2: 0, 3: 0, 4: 0}
                            input_text      = ""
                            input_error     = ""
                            game_state      = "GAMEPLAY"
                    elif event.unicode.isprintable() and len(input_text) < 16:
                        input_text += event.unicode

            elif game_state == "LEADERBOARD":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Restart with same player name
                        score           = 0
                        lives           = STARTING_LIVES
                        hits            = 0
                        misses          = 0
                        paddle_y        = PLAY_HEIGHT // 2 - PADDLE_H // 2
                        ball_x, ball_y, ball_dx, ball_dy = new_ball()
                        scoreboard      = {"score": 0}
                        game_history    = []
                        score_events    = []
                        performance_log = []
                        quadrant_counts = {1: 0, 2: 0, 3: 0, 4: 0}
                        game_state      = "GAMEPLAY"
                    elif event.key == pygame.K_ESCAPE:
                        if launched_from_hub:
                            running = False
                        else:
                            game_state = "MAIN_MENU"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    r_box, m_box = get_leaderboard_buttons()
                    if r_box.collidepoint(event.pos):
                        # Same as pressing R: restart with same player name
                        score           = 0
                        lives           = STARTING_LIVES
                        hits            = 0
                        misses          = 0
                        paddle_y        = PLAY_HEIGHT // 2 - PADDLE_H // 2
                        ball_x, ball_y, ball_dx, ball_dy = new_ball()
                        scoreboard      = {"score": 0}
                        game_history    = []
                        score_events    = []
                        performance_log = []
                        quadrant_counts = {1: 0, 2: 0, 3: 0, 4: 0}
                        game_state      = "GAMEPLAY"
                    elif m_box.collidepoint(event.pos):
                        # Same as pressing ESC
                        if launched_from_hub:
                            running = False
                        else:
                            game_state = "MAIN_MENU"

        # ---- update ----------------------------------------
        if game_state == "MAIN_MENU":
            blink_timer += 1
            if blink_timer >= 30:
                blink_timer = 0
                blink_on = not blink_on

            # simple bouncing dot (no decode_action_string needed)
            demo_pulse_y += pulse_direction * 2
            if demo_pulse_y <= 450:
                pulse_direction = 1
            elif demo_pulse_y >= 490:
                pulse_direction = -1

            draw_menu(screen, font, big_font, small_font,
                      input_text, input_error, blink_on, demo_pulse_y)

        elif game_state == "GAMEPLAY":
            # paddle input
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                target_y = paddle_y - 1000
            elif keys[pygame.K_DOWN]:
                target_y = paddle_y + 1000
            else:
                target_y = paddle_y
            paddle_y = clamp_paddle_movement(
                paddle_y, target_y, PADDLE_MAX_SPEED, PLAY_HEIGHT, PADDLE_H)

            # ball movement
            ball_x += ball_dx
            ball_y += ball_dy

            # top / bottom wall bounce
            if ball_y - BALL_RADIUS <= WALL_THICKNESS:
                ball_dx, ball_dy = reflect_vector(ball_dx, ball_dy, "TOP")
                ball_y = WALL_THICKNESS + BALL_RADIUS
                game_history.append("WALL")
            elif ball_y + BALL_RADIUS >= PLAY_HEIGHT - WALL_THICKNESS:
                ball_dx, ball_dy = reflect_vector(ball_dx, ball_dy, "BOTTOM")
                ball_y = PLAY_HEIGHT - WALL_THICKNESS - BALL_RADIUS
                game_history.append("WALL")

            # left (back) wall bounce
            if ball_x - BALL_RADIUS <= WALL_THICKNESS:
                ball_dx, ball_dy = reflect_vector(ball_dx, ball_dy, "BACK_WALL")
                ball_x = WALL_THICKNESS + BALL_RADIUS
                game_history.append("WALL")

            # paddle collision
            paddle_rect = pygame.Rect(PADDLE_X, paddle_y, PADDLE_W, PADDLE_H)
            ball_rect   = pygame.Rect(ball_x - BALL_RADIUS, ball_y - BALL_RADIUS,
                                      BALL_RADIUS * 2, BALL_RADIUS * 2)

            if ball_dx > 0 and paddle_rect.colliderect(ball_rect):
                ball_dx, ball_dy = reflect_vector(ball_dx, ball_dy, "PADDLE")
                ball_x = PADDLE_X - BALL_RADIUS

                hits += 1
                game_history.append("HIT")

                zone   = get_quadrant_occupancy(ball_x, ball_y, WIDTH, PLAY_HEIGHT)
                points = 5 if zone in (2, 4) else 10
                score += points
                score_events.append(points)

                scoreboard["score"] = score
                scoreboard = get_score_milestone_multipliers(scoreboard, MILESTONES)
                multiplier = scoreboard["speed_multiplier"]
                ball_dx = -BASE_BALL_SPEED * multiplier
                performance_log.append({"type": "paddle_hit", "speed": abs(ball_dx)})

            # quadrant tracking
            quadrant = get_quadrant_occupancy(ball_x, ball_y, WIDTH, PLAY_HEIGHT)
            quadrant_counts[quadrant] += 1

            # miss / life loss
            bounds_state = is_out_of_bounds(
                ball_x, ball_y, BALL_RADIUS, WIDTH, PLAY_HEIGHT)
            if bounds_state == "OUT_RIGHT":
                misses += 1
                lives  -= 1
                game_history.append("MISS")
                ball_x, ball_y, ball_dx, ball_dy = new_ball()

                if lives <= 0:
                    weighted_score  = calculate_weighted_score(score_events)
                    longest_volley  = find_longest_volley(game_history)
                    analytics       = calculate_game_analytics(performance_log)
                    seed_hash       = generate_seed_hash(player_name, score)
                    initials        = shorten_player_name(player_name)

                    leaderboard_history[player_name] = {
                        "score": score, "misses": misses}
                    winner = determine_winning_player(leaderboard_history)

                    last_result = {
                        "name":           player_name,
                        "initials":       initials,
                        "score":          score,
                        "weighted_score": weighted_score,
                        "hits":           hits,
                        "misses":         misses,
                        "longest_volley": longest_volley,
                        "analytics":      analytics,
                        "seed_hash":      seed_hash,
                        "quadrant_counts":dict(quadrant_counts),
                        "winner":         winner,
                    }
                    game_state = "LEADERBOARD"

            # draw
            screen.fill(BG_DARK)
            draw_play_field(screen, paddle_y, ball_x, ball_y)
            draw_hud(screen, font, small_font,
                     player_name, score, lives, hits)

        elif game_state == "LEADERBOARD":
            draw_leaderboard(screen, font, big_font, small_font, last_result)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()