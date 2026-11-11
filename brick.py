import math
import os
import random
import tkinter as tk

WIDTH, HEIGHT = 610, 440
FRAME_MS = 16

BG_COLOR = '#0f172a'
PADDLE_COLOR = '#38bdf8'
BALL_COLOR = '#fbbf24'
TEXT_COLOR = '#e2e8f0'
BRICK_COLORS = {1: '#f87171', 2: '#60a5fa', 3: '#a78bfa'}

POWERUPS = {
    'wide': ('#22c55e', 'W'),
    'slow': ('#f59e0b', 'S'),
    'life': ('#f43f5e', '+'),
}

HIGHSCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              'highscore.txt')
