import random

"""
FLAPPY BIRD LOGIC 
==========================================

STUDENTS: Your job is to complete the functions below using the basic python concepts.

The main.py file will use your logic to run the game.
"""
import random

"""
FLAPPY BIRD LOGIC 
==========================================
"""

def create_bird():
    return {
        'x': 100,
        'y': 300,
        'width': 34,
        'height': 24,
        'velocity': 0
    }


def update_bird(bird, is_jumping):
    if is_jumping:
        bird['velocity'] = -7
    else:
        bird['velocity'] += 0.4
    bird['y'] += bird['velocity']
    return bird


def create_pipe(screen_width, screen_height):
    gap_size = 200
    gap_top = random.randint(50, screen_height - gap_size - 50)
    gap_bottom = gap_top + gap_size
    return {
        'x': screen_width,
        'width': 60,
        'gap_top': gap_top,
        'gap_bottom': gap_bottom,
        'passed': False
    }


def update_pipes(pipes, pipe_speed, screen_width, screen_height):
    for pipe in pipes:
        pipe['x'] -= pipe_speed

    active_pipes = []
    for pipe in pipes:
        if pipe['x'] + pipe['width'] > 0:
            active_pipes.append(pipe)

    if not active_pipes or active_pipes[-1]['x'] < screen_width - 350:
        active_pipes.append(create_pipe(screen_width, screen_height))

    return active_pipes


def check_collision(bird, pipes, screen_height):
    if bird['y'] <= 0 or bird['y'] + bird['height'] >= screen_height:
        return True

    for pipe in pipes:
        if bird['x'] + bird['width'] > pipe['x'] and bird['x'] < pipe['x'] + pipe['width']:
            if bird['y'] < pipe['gap_top'] or bird['y'] + bird['height'] > pipe['gap_bottom']:
                return True

    return False


def update_score(bird, pipes):
    for pipe in pipes:
        if not pipe['passed'] and bird['x'] > pipe['x'] + pipe['width']:
            pipe['passed'] = True
            return 1
    return 0