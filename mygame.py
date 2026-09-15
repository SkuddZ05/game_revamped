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


#draw road
def draw_road(scroll_offset):
    screen.fill((25, 100, 40))  # grass
    pygame.draw.rect(screen, ROAD, (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, HEIGHT))
    # lane dashes scrolling
    dash_h = 40
    gap = 30
    total = dash_h + gap
    start = -(scroll_offset % total)
    y = start
    while y < HEIGHT:
        pygame.draw.rect(screen, LINE_COLOR, (WIDTH // 2 - 4, y, 8, dash_h))
        y += total
    # edges
    pygame.draw.rect(screen, WHITE, (ROAD_LEFT - 6, 0, 6, HEIGHT))
    pygame.draw.rect(screen, WHITE, (ROAD_RIGHT, 0, 6, HEIGHT))

#draw car
def draw_car(x, y, color, w=CAR_W, h=CAR_H):
    body = pygame.Rect(0, 0, w, h)
    body.center = (x, y)
    pygame.draw.rect(screen, color, body, border_radius=8)
    # windshield
    ws = pygame.Rect(0, 0, w - 14, h // 3)
    ws.center = (x, y - h // 6)
    pygame.draw.rect(screen, (200, 230, 255), ws, border_radius=4)

#input controls
def wait_for_key_or_click():
    """Blocks (while still handling quit/esc) until a key or click happens."""
    while True:
        for event in pygame.event.get():
            handle_quit(event)
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                return
        clock.tick(FPS)

#quit game
def handle_quit(event):
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        pygame.quit()
        sys.exit()

#loading screen
def loading_screen():
    start = time.time()
    duration = 1.6
    while time.time() - start < duration:
        for event in pygame.event.get():
            handle_quit(event)
        screen.fill(BLACK)
        draw_text_center("RACING GAME", FONT_BIG, WHITE, WIDTH // 2, HEIGHT // 2 - 40)
        progress = (time.time() - start) / duration
        bar_w = 300
        pygame.draw.rect(screen, GRAY, (WIDTH // 2 - bar_w // 2, HEIGHT // 2 + 20, bar_w, 20), border_radius=10)
        pygame.draw.rect(screen, GREEN, (WIDTH // 2 - bar_w // 2, HEIGHT // 2 + 20, int(bar_w * progress), 20), border_radius=10)
        draw_text_center("Loading...", FONT_SMALL, WHITE, WIDTH // 2, HEIGHT // 2 + 70)
        pygame.display.flip()
        clock.tick(FPS)

#gamemode selection
def choose_game_mode():
    best = load_best_time()
    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            handle_quit(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_race.collidepoint(mouse):
                    return "race"
                if btn_trial.collidepoint(mouse):
                    return "trial"
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_r):
                    return "race"
                if event.key in (pygame.K_2, pygame.K_t):
                    return "trial"

        screen.fill(BLACK)
        draw_text_center("CHOOSE GAME MODE", FONT_MED, WHITE, WIDTH // 2, 140)
        btn_race = draw_button("Race vs Opponent", WIDTH // 2, 320, hover=False)
        btn_trial = draw_button("Time Trial", WIDTH // 2, 400, base_color=(150, 90, 200), hover=False)
        # re-draw with hover highlight
        btn_race = draw_button("Race vs Opponent", WIDTH // 2, 320,
                                hover=btn_race.collidepoint(mouse))
        btn_trial = draw_button("Time Trial", WIDTH // 2, 400, base_color=(150, 90, 200),
                                 hover=btn_trial.collidepoint(mouse))
        if best is not None:
            draw_text_center(f"Best Time Trial: {best:.2f}s", FONT_SMALL, YELLOW, WIDTH // 2, 460)
        draw_text_center("Press 1 or click for Race, 2 or click for Time Trial", FONT_SMALL, GRAY, WIDTH // 2, 640)
        pygame.display.flip()
        clock.tick(FPS)

#selection between time trial or opponent
def transition_screen(text, sub, duration=1.2):
    start = time.time()
    while time.time() - start < duration:
        for event in pygame.event.get():
            handle_quit(event)
        screen.fill(BLACK)
        draw_text_center(text, FONT_MED, WHITE, WIDTH // 2, HEIGHT // 2 - 20)
        draw_text_center(sub, FONT_SMALL, GRAY, WIDTH // 2, HEIGHT // 2 + 30)
        pygame.display.flip()
        clock.tick(FPS)

#countdown
def countdown():
    for label, color in [("3", RED), ("2", YELLOW), ("1", GREEN), ("GO!", GREEN)]:
        start = time.time()
        while time.time() - start < 0.7:
            for event in pygame.event.get():
                handle_quit(event)
            screen.fill(BLACK)
            draw_text_center(label, FONT_BIG, color, WIDTH // 2, HEIGHT // 2)
            pygame.display.flip()
            clock.tick(FPS)

#race opponent
def race_against_opponent():
    player_x = WIDTH // 2
    player_progress = 0.0
    opp_progress = 0.0
    speed = 0.0
    max_speed = 9.0
    accel = 0.22
    brake = 0.35
    friction = 0.06
    opp_base_speed = random.uniform(5.6, 6.6)

    scroll = 0.0
    finished_player = False
    finished_opp = False
    result = None  # "1st" or "2nd"

    while result is None:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            handle_quit(event)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x -= 5
        if keys[pygame.K_RIGHT]:
            player_x += 5
        player_x = max(ROAD_LEFT + CAR_W // 2 + 4, min(ROAD_RIGHT - CAR_W // 2 - 4, player_x))

        if keys[pygame.K_UP]:
            speed = min(max_speed, speed + accel)
        elif keys[pygame.K_DOWN]:
            speed = max(0, speed - brake)
        else:
            speed = max(0, speed - friction)

        if not finished_player:
            player_progress += speed
        if not finished_opp:
            opp_progress += opp_base_speed + random.uniform(-1.2, 1.2)
            opp_progress = max(opp_progress, 0)

        scroll += speed

        if player_progress >= RACE_DISTANCE and not finished_player:
            finished_player = True
        if opp_progress >= RACE_DISTANCE and not finished_opp:
            finished_opp = True

        if finished_player and finished_opp:
            result = "1st" if player_progress >= opp_progress and finished_player and (not finished_opp or player_progress >= opp_progress) else "2nd"
            # simpler: whichever crossed distance conceptually first -> compare finish order
        elif finished_player:
            result = "1st"
        elif finished_opp:
            result = "2nd"

        # ---- draw ----
        draw_road(scroll)
        opp_x = WIDTH // 2 + 60
        draw_car(opp_x, 180, RED)
        draw_car(player_x, 560, BLUE)

        # progress bars
        pygame.draw.rect(screen, GRAY, (20, 20, 200, 14), border_radius=6)
        pygame.draw.rect(screen, BLUE, (20, 20, int(200 * min(1, player_progress / RACE_DISTANCE)), 14), border_radius=6)
        draw_text_center("YOU", FONT_SMALL, WHITE, 250, 27)

        pygame.draw.rect(screen, GRAY, (20, 44, 200, 14), border_radius=6)
        pygame.draw.rect(screen, RED, (20, 44, int(200 * min(1, opp_progress / RACE_DISTANCE)), 14), border_radius=6)
        draw_text_center("CPU", FONT_SMALL, WHITE, 250, 51)

        draw_text_center(f"Speed: {speed:.1f}", FONT_SMALL, WHITE, WIDTH - 70, 30)

        pygame.display.flip()

    return result  # "1st" or "2nd"

#win or lose screen
def win_lose_screen(placement):
    if placement == "1st":
        text, color = "YOU WIN!", GREEN
    else:
        text, color = "YOU LOSE", RED

    start = time.time()
    while True:
        for event in pygame.event.get():
            handle_quit(event)
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN) and time.time() - start > 0.4:
                return
        screen.fill(BLACK)
        draw_text_center(text, FONT_BIG, color, WIDTH // 2, HEIGHT // 2 - 40)
        draw_text_center(f"Finish placement: {placement}", FONT_MED, WHITE, WIDTH // 2, HEIGHT // 2 + 20)
        draw_text_center("Press any key to continue", FONT_SMALL, GRAY, WIDTH // 2, HEIGHT // 2 + 80)
        pygame.display.flip()
        clock.tick(FPS)

