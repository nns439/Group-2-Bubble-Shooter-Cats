import pygame
import math
import random
import os

pygame.init()
pygame.mixer.init()

# ---------------- НАСТРОЙКИ ----------------
WIDTH, HEIGHT = 420, 640
FPS = 60
RADIUS = 22
ROWS = 5
COLUMNS = 8
HUD_HEIGHT = 50
LOSE_LINE_Y = HEIGHT - 120

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bubble Shooter: cats")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 20)
title_font = pygame.font.SysFont("arial", 32)

# ---------------- ЦВЕТА ----------------
BG_COLOR = (252, 250, 240)
TEXT_COLOR = (0, 0, 0)
LINE_COLOR = (0, 0, 0)
GAME_OVER_COLOR = (200, 0, 0)

# ---------------- ФОНЫ ЭКРАНОВ ----------------
def load_bg(name):
    path = os.path.join("backgrounds", name)
    if not os.path.exists(path):
        return None
    img = pygame.image.load(path).convert()
    return pygame.transform.smoothscale(img, (WIDTH, HEIGHT))

BG_MENU = load_bg("menu.png")        # фон главного меню
BG_GAME = load_bg("game.png")        # фон игры
BG_GAME_OVER = load_bg("game_over.png")  # фон при проигрыше

# ---------------- ЗВУКИ ----------------
pygame.mixer.music.load("sounds/music_loop.mp3")
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1)  # фоновая музыка всегда

pop_sound = pygame.mixer.Sound("sounds/pop_meow.mp3")
pop_sound.set_volume(0.7)

game_over_sound = pygame.mixer.Sound("sounds/game_over.mp3")
game_over_sound.set_volume(0.6)

# ---------------- ЗАГРУЗКА КАРТИНОК ----------------
def load_cat(name):
    path = os.path.join("cats", name)
    if not os.path.exists(path):
        surf = pygame.Surface((RADIUS*2, RADIUS*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (200, 200, 200), (RADIUS, RADIUS), RADIUS)
        return surf
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.smoothscale(img, (RADIUS*2, RADIUS*2))

CATS = {
    "white": load_cat("white.png"),
    "black": load_cat("black.png"),
    "orange": load_cat("orange.png"),
    "gray": load_cat("gray.png")
}
CAT_TYPES = list(CATS.keys())

# ---------------- КЛАСС КОТА ----------------
class CatBubble:
    def __init__(self, x, y, cat_type):
        self.x = x
        self.y = y
        self.type = cat_type
        self.popping = False
        self.scale = 1.0
        self.marked = False

    def draw(self):
        size = int(RADIUS * 2 * self.scale)
        img = pygame.transform.smoothscale(CATS[self.type], (size, size))
        screen.blit(img, (self.x - size//2, self.y - size//2))

    def pop(self):
        self.popping = True

    def update(self):
        if self.popping:
            self.scale -= 0.1
            return self.scale <= 0
        return False

# ---------------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ----------------
def create_initial_bubbles(rows=ROWS):
    bubbles = []
    for row in range(rows):
        for col in range(COLUMNS):
            bubbles.append(
                CatBubble(
                    col * 48 + 36,
                    row * 42 + 36 + HUD_HEIGHT,
                    random.choice(CAT_TYPES)
                )
            )
    return bubbles

def get_neighbors(cat, bubbles):
    return [
        b for b in bubbles
        if b != cat and not b.popping and
        math.hypot(cat.x - b.x, cat.y - b.y) < RADIUS*2 + 5 and
        b.type == cat.type
    ]

def find_cluster(cat, bubbles):
    for b in bubbles:
        b.marked = False
    cluster = [cat]
    stack = [cat]
    cat.marked = True
    while stack:
        current = stack.pop()
        for n in get_neighbors(current, bubbles):
            if not n.marked:
                n.marked = True
                cluster.append(n)
                stack.append(n)
    return cluster

def attach_shooter(shooter, bubbles):
    min_dist = float("inf")
    best_x, best_y = shooter.x, shooter.y
    for b in bubbles:
        for dx in (-RADIUS*2, 0, RADIUS*2):
            for dy in (-RADIUS*2, 0, RADIUS*2):
                x, y = b.x + dx, b.y + dy
                if x < RADIUS or x > WIDTH - RADIUS or y < HUD_HEIGHT + RADIUS:
                    continue
                if any(math.hypot(x - bb.x, y - bb.y) < RADIUS*2 for bb in bubbles):
                    continue
                d = math.hypot(x - shooter.x, y - shooter.y)
                if d < min_dist:
                    min_dist, best_x, best_y = d, x, y
    shooter.x, shooter.y = best_x, best_y
    bubbles.append(shooter)

# ---------------- MAIN MENU ----------------
def main_menu():
    player_name = ""
    input_active = False
    cursor_timer = 0
    show_cursor = True
    name_button = pygame.Rect(110, 240, 200, 45)
    start_button = pygame.Rect(110, 420, 200, 45)

    while True:
        clock.tick(FPS)
        if BG_MENU:
            screen.blit(BG_MENU, (0, 0))
        else:
            screen.fill(BG_COLOR)

        title = title_font.render("Bubble shooter: cats", True, TEXT_COLOR)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))

        mx, my = pygame.mouse.get_pos()

        pygame.draw.rect(screen, BG_COLOR, name_button)
        pygame.draw.rect(screen, LINE_COLOR, name_button, 2)
        txt = font.render("Ввести имя", True, TEXT_COLOR)
        screen.blit(txt, (name_button.centerx - txt.get_width()//2,
                          name_button.centery - txt.get_height()//2))

        input_y = name_button.bottom + 60
        pygame.draw.line(screen, LINE_COLOR, (110, input_y), (310, input_y), 2)

        name_surface = font.render(player_name, True, TEXT_COLOR)
        screen.blit(name_surface, (115, input_y - 28))

        cursor_timer += 1
        if cursor_timer % 30 == 0:
            show_cursor = not show_cursor
        if input_active and show_cursor:
            cursor_x = 115 + name_surface.get_width() + 2
            pygame.draw.line(screen, TEXT_COLOR,
                             (cursor_x, input_y - 28),
                             (cursor_x, input_y - 6), 2)

        if player_name.strip():
            pygame.draw.rect(screen, BG_COLOR, start_button)
            pygame.draw.rect(screen, LINE_COLOR, start_button, 2)
            txt = font.render("Начать игру", True, TEXT_COLOR)
            screen.blit(txt, (start_button.centerx - txt.get_width()//2,
                              start_button.centery - txt.get_height()//2))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if name_button.collidepoint(mx, my):
                    input_active = True
                elif player_name.strip() and start_button.collidepoint(mx, my):
                    return player_name
            if e.type == pygame.KEYDOWN and input_active:
                if e.key == pygame.K_RETURN:
                    input_active = False
                elif e.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif len(player_name) < 12:
                    player_name += e.unicode

# ---------------- ИГРА ----------------
def game(player_name):
    bubbles = create_initial_bubbles()
    shooter = CatBubble(WIDTH//2, HEIGHT-40, random.choice(CAT_TYPES))
    dx = dy = 0
    shot = False
    score = 0
    game_over = False
    game_over_played = False

    while True:
        clock.tick(FPS)
        screen.fill(BG_COLOR)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                exit()
            if e.type == pygame.MOUSEBUTTONDOWN and not shot and not game_over:
                mx, my = pygame.mouse.get_pos()
                angle = math.atan2(my - shooter.y, mx - shooter.x)
                dx, dy = math.cos(angle)*7, math.sin(angle)*7
                shot = True
            if e.type == pygame.MOUSEBUTTONDOWN and game_over:
                 game_over_sound.stop()          # ⬅ остановка звука проигрыша
                 pygame.mixer.music.play(-1)     # ⬅ возврат фоновой музыки
                 return

        if shot and not game_over:
            shooter.x += dx
            shooter.y += dy
            if shooter.x <= RADIUS or shooter.x >= WIDTH - RADIUS:
                dx *= -1

            for b in bubbles:
                if math.hypot(shooter.x - b.x, shooter.y - b.y) < RADIUS*2:
                    cluster = find_cluster(b, bubbles)
                    if len(cluster) >= 2 and shooter.type == b.type:
                        pop_sound.play()
                        for c in cluster:
                            c.pop()
                        score += len(cluster) * 10
                    else:
                        attach_shooter(shooter, bubbles)
                    shot = False
                    shooter = CatBubble(WIDTH//2, HEIGHT-40, random.choice(CAT_TYPES))
                    break

            if shooter.y <= HUD_HEIGHT + RADIUS:
                attach_shooter(shooter, bubbles)
                shot = False
                shooter = CatBubble(WIDTH//2, HEIGHT-40, random.choice(CAT_TYPES))

        for b in bubbles[:]:
            if b.update():
                bubbles.remove(b)

        for b in bubbles:
            if b.y + RADIUS >= LOSE_LINE_Y:
                game_over = True

        pygame.draw.rect(screen, BG_COLOR, (0, 0, WIDTH, HUD_HEIGHT))
        screen.blit(font.render(f"{player_name} | Очки: {score}", True, TEXT_COLOR), (10, 15))

        for b in bubbles:
            b.draw()
        shooter.draw()

        pygame.draw.line(screen, LINE_COLOR, (0, LOSE_LINE_Y), (WIDTH, LOSE_LINE_Y), 2)

        if game_over:
            if BG_GAME_OVER:
                screen.blit(BG_GAME_OVER, (0, 0))
            if not game_over_played:
                pygame.mixer.music.stop()
                game_over_sound.play(-1)
                game_over_played = True

            text = font.render("ИГРА ОКОНЧЕНА", True, GAME_OVER_COLOR)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))

        pygame.display.flip()

# ---------------- ЗАПУСК ----------------
while True:
    name = main_menu()
    game(name)
