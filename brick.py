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


class GameObject:
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)

class Ball(GameObject):
    def __init__(self, canvas, x, y, bounds_width):
        self.radius = 8
        self.width = bounds_width
        self.dx = 0.0
        self.dy = -1.0
        self.speed = 5.0
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill=BALL_COLOR, outline='white')
        super().__init__(canvas, item)

    def set_center(self, cx, cy):
        r = self.radius
        self.canvas.coords(self.item, cx - r, cy - r, cx + r, cy + r)

    def launch(self):
        angle = math.radians(random.uniform(-30, 30))
        self.dx = math.sin(angle)
        self.dy = -math.cos(angle)

    def update(self):
        self.move(self.dx * self.speed, self.dy * self.speed)
        x1, y1, x2, y2 = self.get_position()
        if x1 <= 0:
            self.move(-x1, 0)
            self.dx = abs(self.dx)
        elif x2 >= self.width:
            self.move(self.width - x2, 0)
            self.dx = -abs(self.dx)
        if y1 <= 0:
            self.move(0, -y1)
            self.dy = abs(self.dy)
            
def bounce_off_paddle(self, paddle):
        x1, _, x2, _ = self.get_position()
        cx = (x1 + x2) / 2
        p = paddle.get_position()
        pcx = (p[0] + p[2]) / 2
        half = (p[2] - p[0]) / 2
        offset = max(-1.0, min(1.0, (cx - pcx) / half))
        angle = math.radians(offset * 60)
        self.dx = math.sin(angle)
        self.dy = -math.cos(angle)
        self.move(0, p[1] - self.get_position()[3])

def deflect_from_brick(self, brick_coords, multiple):
        x1, y1, x2, y2 = self.get_position()
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        bcx = (brick_coords[0] + brick_coords[2]) / 2
        bcy = (brick_coords[1] + brick_coords[3]) / 2
        if not multiple and (cx < brick_coords[0] or cx > brick_coords[2]):
            self.dx = -abs(self.dx) if cx < bcx else abs(self.dx)
        else:
            self.dy = -abs(self.dy) if cy < bcy else abs(self.dy)

class Paddle(GameObject):
    def __init__(self, canvas, x, y, bounds_width):
        self.base_width = 100
        self.width = self.base_width
        self.height = 12
        self.y = y
        self.bounds = bounds_width
        item = canvas.create_rectangle(x - self.width / 2, y - self.height / 2,
                                       x + self.width / 2, y + self.height / 2,
                                       fill=PADDLE_COLOR, outline='white')
        super().__init__(canvas, item)

    def center_x(self):
        c = self.get_position()
        return (c[0] + c[2]) / 2

    def move_to(self, cx):
        half = self.width / 2
        cx = max(half, min(self.bounds - half, cx))
        self.canvas.coords(self.item, cx - half, self.y - self.height / 2,
                           cx + half, self.y + self.height / 2)

    def move_by(self, dx):
        self.move_to(self.center_x() + dx)

    def set_width(self, new_width):
        cx = self.center_x()
        self.width = new_width
        self.move_to(cx)

class Brick(GameObject):
    def __init__(self, canvas, x, y, hits):
        self.width = 71
        self.height = 20
        self.hits = hits
        item = canvas.create_rectangle(x - self.width / 2, y - self.height / 2,
                                       x + self.width / 2, y + self.height / 2,
                                       fill=BRICK_COLORS[hits],
                                       outline=BG_COLOR, width=2)
        super().__init__(canvas, item)

    def hit(self):
        self.hits -= 1
        if self.hits <= 0:
            self.delete()
            return True
        self.canvas.itemconfig(self.item, fill=BRICK_COLORS[self.hits])
        return False
