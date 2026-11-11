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

class PowerUp(GameObject):
    def __init__(self, canvas, x, y, kind):
        self.kind = kind
        self.speed = 3
        color, symbol = POWERUPS[kind]
        item = canvas.create_oval(x - 11, y - 11, x + 11, y + 11,
                                fill=color, outline='white')
        super().__init__(canvas, item)
        self.label = canvas.create_text(x, y, text=symbol, fill='white',
                                        font=('Helvetica', 11, 'bold'))

    def update(self):
        self.move(0, self.speed)
        self.canvas.move(self.label, 0, self.speed)

    def delete(self):
        self.canvas.delete(self.label)
        super().delete()

class Game(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.width, self.height = WIDTH, HEIGHT
        self.canvas = tk.Canvas(self, bg=BG_COLOR, width=self.width,
                                height=self.height, highlightthickness=0)
        self.canvas.pack()
        self.pack()

        self.draw_background()
        self.highscore = self.load_highscore()
        self.keys = set()
        self.bricks = {}
        self.powerups = []
        self.ball = None
        self.message = None
        self.last_brick = None
        self.state = 'ready'

        self.paddle = Paddle(self.canvas, self.width / 2, self.height - 40,
                             self.width)
        self.hud_score = self.canvas.create_text(
            15, 18, anchor='w', fill=TEXT_COLOR, font=('Helvetica', 13, 'bold'))
        self.hud_level = self.canvas.create_text(
            self.width / 2, 18, fill=TEXT_COLOR, font=('Helvetica', 13, 'bold'))
        self.hud_lives = self.canvas.create_text(
            self.width - 15, 18, anchor='e', fill='#f43f5e',
            font=('Helvetica', 14, 'bold'))
        self.hud_effects = self.canvas.create_text(
            10, self.height - 10, anchor='w', fill='#94a3b8',
            font=('Helvetica', 10))

        self.new_game()

        master.bind('<KeyPress>', self.on_key_press)
        master.bind('<KeyRelease>', self.on_key_release)
        self.canvas.bind('<Motion>', self.on_mouse_move)
        self.tick()

    def draw_background(self):
        for _ in range(70):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            self.canvas.create_oval(x, y, x + 2, y + 2, outline='',
                                    fill=random.choice(['#334155', '#475569',
                                                        '#64748b']))

    def new_game(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.wide_frames = 0
        self.slow_frames = 0
        self.paddle.set_width(self.paddle.base_width)
        self.start_level()

    def start_level(self):
        for brick in self.bricks.values():
            self.canvas.delete(brick.item)
        self.bricks.clear()
        self.clear_powerups()
        self.build_level()
        self.new_ball()
        self.state = 'ready'
        self.update_hud()
        self.show_message('Level %d\nTekan Spasi untuk mulai' % self.level)

    def build_level(self):
        rows = min(3 + self.level, 7)
        for r in range(rows):
            if self.level >= 3 and r == 0:
                hits = 3
            elif r == 0 or (self.level >= 2 and r == 1):
                hits = 2
            else:
                hits = 1
            for c in range(8):
                if self.level >= 2 and random.random() < 0.12:
                    continue
                self.add_brick(5 + c * 75 + 37.5, 60 + r * 24, hits)
        if not self.bricks:
            self.add_brick(self.width / 2, 60, 1)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.bricks[brick.item] = brick

    def new_ball(self):
        if self.ball is not None:
            self.ball.delete()
        self.ball = Ball(self.canvas, 0, 0, self.width)
        self.attach_ball()

    def attach_ball(self):
        p = self.paddle.get_position()
        self.ball.set_center(self.paddle.center_x(),
                             p[1] - self.ball.radius - 1)

    def on_key_press(self, event):
        key = event.keysym.lower()
        self.keys.add(key)
        if key == 'space':
            self.on_space()
        elif key == 'p':
            self.toggle_pause()

    def on_key_release(self, event):
        self.keys.discard(event.keysym.lower())

    def on_mouse_move(self, event):
        if self.state in ('ready', 'playing'):
            self.paddle.move_to(event.x)

    def on_space(self):
        if self.state == 'ready':
            self.clear_message()
            self.ball.launch()
            self.state = 'playing'
        elif self.state == 'level_clear':
            self.level += 1
            self.start_level()
        elif self.state == 'over':
            self.new_game()
