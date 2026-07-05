"""
FLAPPY BIRD GAME - MAIN FILE  (Neon Arcade Edition)
==============================================

STUDENTS: Do not modify this file!
Your job is to complete the logic in logic_skeleton.py

This file contains the graphics and main game loop.
It handles:
- Pygame window setup and initialization
- Drawing graphics (bird, pipes, text)
- Event handling (keyboard and mouse inputs)
- Game state management (ready, playing, game over)
- Calling the functions from logic_skeleton.py

"""

import os
import pygame
import sys
import logic_skeleton  

# --- Pygame Initialization ---
pygame.init()
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird — Arcade Edition")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("consolas", 28, bold=True)
SMALL_FONT = pygame.font.SysFont("consolas", 14, bold=True)
BIG_FONT = pygame.font.SysFont("consolas", 40, bold=True)

# --- Neon Arcade Color Palette (matches Ping Pong / Launcher) ---
BG_DARK      = (8,   8,  22)
BG_PANEL     = (14,  14,  34)
NEON_CYAN    = (60, 240, 255)
NEON_MAGENTA = (255,  60, 180)
NEON_YELLOW  = (255, 225,  70)
NEON_GREEN   = (90,  255, 160)
NEON_ORANGE  = (255, 160,  40)
TEXT_MAIN    = (235, 240, 255)
TEXT_DIM     = (120, 130, 165)
GRID_COLOR   = (24,   26,  52)
PIPE_BODY    = (16,  24,  48)
PIPE_OUTLINE = NEON_CYAN

# Legacy aliases
COLOR_BG = BG_DARK
COLOR_BIRD = NEON_YELLOW
COLOR_PIPE = NEON_CYAN
COLOR_TEXT = TEXT_MAIN
COLOR_RED = NEON_MAGENTA

# --- Player name from arcade hub ---
PLAYER_NAME = os.environ.get("ARCADE_PLAYER_NAME", "")

# --- HUD height ---
HUD_HEIGHT = 50

# --- Game-over screen button rects (shared by drawing + click detection) ---
GAME_OVER_RESTART_BOX = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 30, 300, 40)
GAME_OVER_MENU_BOX = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 85, 300, 40)

# --- Game State Variables ---
bird = logic_skeleton.create_bird()
pipes = []
score = 0
game_over = False
pipe_speed = 2
game_started = False


# ===================== DRAWING HELPERS =====================

def draw_grid_background():
    """Draw subtle grid lines on the background."""
    for x in range(0, SCREEN_WIDTH, 30):
        pygame.draw.line(screen, GRID_COLOR, (x, HUD_HEIGHT), (x, SCREEN_HEIGHT))
    for y in range(HUD_HEIGHT, SCREEN_HEIGHT, 30):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))


def draw_glow_circle(color, center, radius):
    """Draw a circle with a soft neon glow."""
    glow = pygame.Surface((radius * 6, radius * 6), pygame.SRCALPHA)
    gx, gy = radius * 3, radius * 3
    for i in range(3, 0, -1):
        alpha = 30 * i
        pygame.draw.circle(glow, (*color, alpha), (gx, gy), radius + i * 3)
    screen.blit(glow, (center[0] - gx, center[1] - gy))
    pygame.draw.circle(screen, color, center, radius)


def draw_glow_text(text, x, y, color, font_obj=None, center=False):
    """Draw text with a neon glow effect."""
    f = font_obj or FONT
    # glow layers
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
        faint = f.render(text, True, color)
        faint.set_alpha(35)
        if center:
            r = faint.get_rect(center=(x + dx, y + dy))
        else:
            r = faint.get_rect(topleft=(x + dx, y + dy))
        screen.blit(faint, r)
    # main text
    surf = f.render(text, True, TEXT_MAIN)
    if center:
        r = surf.get_rect(center=(x, y))
    else:
        r = surf.get_rect(topleft=(x, y))
    screen.blit(surf, r)


def draw_hud():
    """Draw the top HUD bar with player name and score."""
    hud_rect = pygame.Rect(0, 0, SCREEN_WIDTH, HUD_HEIGHT)
    pygame.draw.rect(screen, BG_PANEL, hud_rect)
    pygame.draw.line(screen, NEON_CYAN, (0, HUD_HEIGHT), (SCREEN_WIDTH, HUD_HEIGHT), 2)

    # Player name (left)
    if PLAYER_NAME:
        name_surf = SMALL_FONT.render(PLAYER_NAME.upper(), True, NEON_CYAN)
        screen.blit(name_surf, (12, HUD_HEIGHT // 2 - name_surf.get_height() // 2))

    # Title (center)
    title = SMALL_FONT.render("F L A P P Y  B I R D", True, TEXT_DIM)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 8))

    # Score (center-bottom of HUD)
    score_surf = FONT.render(f"{score}", True, NEON_YELLOW)
    screen.blit(score_surf, (SCREEN_WIDTH // 2 - score_surf.get_width() // 2, 22))


def draw_neon_pipe(pipe):
    """Draw a pipe with neon outlines and dark fill."""
    pw = pipe['width']
    # Top pipe
    top_rect = pygame.Rect(pipe['x'], HUD_HEIGHT, pw, pipe['gap_top'] - HUD_HEIGHT)
    pygame.draw.rect(screen, PIPE_BODY, top_rect)
    pygame.draw.rect(screen, PIPE_OUTLINE, top_rect, 2)
    # Top pipe cap
    cap_h = 12
    cap_rect = pygame.Rect(pipe['x'] - 4, pipe['gap_top'] - cap_h, pw + 8, cap_h)
    pygame.draw.rect(screen, NEON_CYAN, cap_rect, border_radius=3)

    # Bottom pipe
    bot_rect = pygame.Rect(pipe['x'], pipe['gap_bottom'], pw, SCREEN_HEIGHT - pipe['gap_bottom'])
    pygame.draw.rect(screen, PIPE_BODY, bot_rect)
    pygame.draw.rect(screen, PIPE_OUTLINE, bot_rect, 2)
    # Bottom pipe cap
    cap_rect2 = pygame.Rect(pipe['x'] - 4, pipe['gap_bottom'], pw + 8, cap_h)
    pygame.draw.rect(screen, NEON_CYAN, cap_rect2, border_radius=3)


def draw_neon_bird(bird):
    """Draw the bird as a glowing neon circle with eye and beak."""
    cx = bird['x'] + bird['width'] // 2
    cy = bird['y'] + bird['height'] // 2

    # Glow body
    draw_glow_circle(NEON_YELLOW, (cx, cy), 17)

    # Eye
    pygame.draw.circle(screen, BG_DARK, (cx + 8, cy - 5), 4)
    pygame.draw.circle(screen, TEXT_MAIN, (cx + 8, cy - 5), 2)

    # Beak
    beak_points = [
        (cx + 15, cy + 2),
        (cx + 25, cy + 5),
        (cx + 15, cy + 8)
    ]
    pygame.draw.polygon(screen, NEON_ORANGE, beak_points)


def draw_text(text, x, y, center=False, color=COLOR_TEXT):
    """Helper function to draw text on the screen (legacy compat)."""
    surf = FONT.render(text, True, color)
    shadow_surf = FONT.render(text, True, (0, 0, 0))
    
    if center:
        rect = surf.get_rect(center=(x, y))
        screen.blit(shadow_surf, (rect.x + 2, rect.y + 2))
        screen.blit(surf, rect)
    else:
        screen.blit(shadow_surf, (x + 2, y + 2))
        screen.blit(surf, (x, y))


def reset_game():
    """Resets all game variables to their starting state."""
    global bird, pipes, score, game_over, game_started  
    bird = logic_skeleton.create_bird()
    pipes = []
    score = 0
    game_over = False
    game_started = False  


# --- Main Game Loop ---
while True:
    # 1. Event Handling (Inputs)
    is_jumping = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if game_over:
                # Game over: R or SPACE to restart, ESC to quit to hub
                if event.key == pygame.K_r or event.key == pygame.K_SPACE:
                    reset_game()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif not game_started:
                # Any key starts the game
                if event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                    game_started = True
            else:
                if event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                    is_jumping = True
                    
        # --- MOUSE INPUT ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_over:
                if GAME_OVER_RESTART_BOX.collidepoint(event.pos):
                    reset_game()
                elif GAME_OVER_MENU_BOX.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
            elif not game_started:           
                game_started = True          
            else:
                is_jumping = True


    # 2. Logic (Functions)
    if not game_over and game_started: 
        bird = logic_skeleton.update_bird(bird, is_jumping)
        pipes = logic_skeleton.update_pipes(pipes, pipe_speed, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        if logic_skeleton.check_collision(bird, pipes, SCREEN_HEIGHT):
            game_over = True
            
        score += logic_skeleton.update_score(bird, pipes)


    # 3. Draw Graphics 
    screen.fill(BG_DARK)
    draw_grid_background()

    # Draw HUD
    draw_hud()

    # Draw Pipes (neon style)
    for pipe in pipes:
        draw_neon_pipe(pipe)

    # Draw Bird (neon glow)
    draw_neon_bird(bird)

    # Draw "Press to start" screen
    if not game_started and not game_over:
        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 8, 22, 140))
        screen.blit(overlay, (0, 0))

        draw_glow_text("FLAPPY BIRD", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60,
                       NEON_CYAN, BIG_FONT, center=True)
        draw_glow_text("PRESS SPACE TO START", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10,
                       NEON_GREEN, SMALL_FONT, center=True)

    # Draw Game Over Screen
    if game_over:
        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 8, 22, 160))
        screen.blit(overlay, (0, 0))

        draw_glow_text("GAME OVER", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80,
                       NEON_MAGENTA, BIG_FONT, center=True)
        draw_glow_text(f"SCORE: {score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20,
                       NEON_YELLOW, FONT, center=True)

        # Two choice buttons
        # Restart option
        r_box = GAME_OVER_RESTART_BOX
        pygame.draw.rect(screen, BG_PANEL, r_box, border_radius=8)
        pygame.draw.rect(screen, NEON_GREEN, r_box, 2, border_radius=8)
        draw_glow_text("R / SPACE / CLICK   RESTART", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50,
                       NEON_GREEN, SMALL_FONT, center=True)

        # Main menu option
        m_box = GAME_OVER_MENU_BOX
        pygame.draw.rect(screen, BG_PANEL, m_box, border_radius=8)
        pygame.draw.rect(screen, NEON_MAGENTA, m_box, 2, border_radius=8)
        draw_glow_text("ESC / CLICK   MAIN MENU", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 105,
                       NEON_MAGENTA, SMALL_FONT, center=True)


    # 4. Update Display
    pygame.display.flip()
    clock.tick(60) 