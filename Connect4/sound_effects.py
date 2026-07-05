"""
sound_effects.py
-----------------
All pygame code lives in this one file. Keeping it separate means
game_logic.py (the rules) and main.py (the GUI) don't need to know
anything about pygame at all.

Students do not need to edit this file for the Code Craft assignment
-- it's provided so the game has sound effects right away.

Requires four audio files in the same folder as this script:
    another_one.mp3  -> played when a piece is dropped
    win.mp3           -> played when someone wins
    yeh_le.mp3        -> played when the dice is rolled
    aag.mp3           -> played when a bomb explodes
"""

import threading
import pygame

pygame.mixer.init()

drop_sound = pygame.mixer.Sound("another_one.mp3")
win_sound = pygame.mixer.Sound("win.mp3")
dice_sound = pygame.mixer.Sound("yeh_le.mp3")
bomb_sound = pygame.mixer.Sound("aag.mp3")


def play_drop_sound():
    """Plays the "piece dropped" sound effect."""
    threading.Thread(target=drop_sound.play, daemon=True).start()


def play_win_sound():
    """Plays the "someone won" sound effect."""
    threading.Thread(target=win_sound.play, daemon=True).start()


def play_win_sounds():
    """Plays BOTH aag.mp3 and win.mp3 together when a player wins."""
    threading.Thread(target=bomb_sound.play, daemon=True).start()
    threading.Thread(target=win_sound.play, daemon=True).start()


def play_dice_sound():
    """Plays the "dice rolled" sound effect."""
    threading.Thread(target=dice_sound.play, daemon=True).start()


def play_bomb_sound():
    """Plays the "bomb exploded" sound effect."""
    threading.Thread(target=bomb_sound.play, daemon=True).start()
