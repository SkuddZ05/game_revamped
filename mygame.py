import pygame
import random
import sys
import os
import json
import time

pygame.init()

WIDTH, HEIGHT = 600, 920
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game")
clock = pygame.time.Clock()
FPS = 60

FONT_BIG = pygame.font.SysFont("arial", 48, bold=True)
FONT_MED = pygame.font.SysFont("arial", 30, bold=True)
FONT_SMALL = pygame.font.SysFont("arial", 20)

WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
GRAY = (60, 60, 60)
ROAD = (40, 40, 45)
LINE_COLOR = (230, 200, 60)
BLUE = (70, 130, 220)
RED = (210, 70, 70)
GREEN = (70, 200, 120)
YELLOW = (240, 210, 90)

RECORD_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "best_time.json")

ROAD_LEFT = 90
ROAD_RIGHT = WIDTH - 90
CAR_W, CAR_H = 40, 70

RACE_DISTANCE = 3000   # "finish line" distance for Race vs Opponent
TRIAL_DISTANCE = 2000  # distance for one Time Trial lap

#function for times
def load_best_time():
    if os.path.exists(RECORD_FILE):
        try:
            with open(RECORD_FILE, "r") as f:
                return json.load(f).get("best_time")
        except Exception:
            return None
    return None
#function for best time

def save_best_time(t):
    with open(RECORD_FILE, "w") as f:
        json.dump({"best_time": t}, f)


#draw text
def draw_text_center(text, font, color, cx, cy):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(cx, cy))
    screen.blit(surf, rect)
    return rect

#draw button
def draw_button(text, cx, cy, w=280, h=60, base_color=BLUE, hover=False):
    rect = pygame.Rect(0, 0, w, h)
    rect.center = (cx, cy)
    color = tuple(min(255, c + 30) for c in base_color) if hover else base_color
    pygame.draw.rect(screen, color, rect, border_radius=14)
    pygame.draw.rect(screen, WHITE, rect, width=2, border_radius=14)
    draw_text_center(text, FONT_MED, WHITE, cx, cy)
    return rect