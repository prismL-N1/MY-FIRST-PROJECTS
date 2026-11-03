import pygame
import sys
import math
import random

pygame.init()

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 960, 640
FPS = 60

# Hollow Knight-ish palette: deep blues/blacks, pale accent, bone white
BG_DARK = (12, 14, 20)
BG_PANEL = (20, 23, 32)
BORDER = (90, 100, 120)
BORDER_LIT = (170, 200, 220)
TEXT_MAIN = (210, 215, 225)
TEXT_DIM = (120, 128, 145)
ACCENT = (140, 190, 210)
GOLD = (200, 175, 110)
RED = (190, 70, 70)
DARK_RED = (90, 30, 30)
GREEN = (90, 170, 120)
DARK_GREEN = (35, 60, 45)

FONT = pygame.font.SysFont("georgia", 20)
FONT_BIG = pygame.font.SysFont("georgia", 36, bold=True)
FONT_SMALL = pygame.font.SysFont("georgia", 16)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini RPG")
clock = pygame.time.Clock()


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def draw_text(surface, text, font, color, x, y, center=False):
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(img, rect)
    return rect


def draw_bar(surface, x, y, w, h, value, max_value, fg_color, bg_color):
    pygame.draw.rect(surface, bg_color, (x, y, w, h), border_radius=4)
    ratio = max(0, value) / max_value if max_value else 0
    pygame.draw.rect(surface, fg_color,
                     (x, y, int(w * ratio), h), border_radius=4)
    pygame.draw.rect(surface, BORDER_LIT, (x, y, w, h), 2, border_radius=4)


def draw_panel(surface, rect, glow=False):
    """Hollow Knight style dark panel with a thin lit border."""
    pygame.draw.rect(surface, BG_PANEL, rect, border_radius=10)
    pygame.draw.rect(surface, BORDER_LIT if glow else BORDER,
                     rect, 2, border_radius=10)


class Button:
    def __init__(self, x, y, w, h, text, enabled=True):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.enabled = enabled

    def draw(self, surface, mouse_pos):
        hovered = self.rect.collidepoint(mouse_pos) and self.enabled
        border_color = ACCENT if hovered else (
            BORDER if self.enabled else (50, 50, 55))
        text_color = TEXT_MAIN if self.enabled else TEXT_DIM
        pygame.draw.rect(surface, BG_PANEL, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=8)
        draw_text(surface, self.text, FONT, text_color,
                  self.rect.centerx, self.rect.centery, center=True)

    def clicked(self, event):
        return (
            self.enabled
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


# ---------------------------------------------------------------------------
# GAME DATA
# ---------------------------------------------------------------------------
ENEMIES = {
    "Goblin":   {"hp": 30,  "atk": 5,  "xp": 20,  "gold": 50,  "speed": 1.6, "color": (110, 150, 90)},
    "Skeleton": {"hp": 50,  "atk": 10, "xp": 40,  "gold": 100, "speed": 2.0, "color": (200, 200, 190)},
    "Dragon":   {"hp": 100, "atk": 20, "xp": 100, "gold": 500, "speed": 1.2, "color": (190, 90, 70)},
}

# Simple overworld map: rooms laid out on a grid, Hollow Knight style room-to-room.
# Each room has an id, a list of enemy names to spawn, and exits (direction -> room id).
ROOMS = {
    "start":    {"enemies": [],                 "exits": {"E": "goblin_room", "S": "shop_room"}},
    "goblin_room": {"enemies": ["Goblin"],       "exits": {"W": "start", "E": "skeleton_room"}},
    "skeleton_room": {"enemies": ["Skeleton"],   "exits": {"W": "goblin_room", "E": "dragon_room"}},
    "dragon_room": {"enemies": ["Dragon"],       "exits": {"W": "skeleton_room"}},
    "shop_room": {"enemies": [], "exits": {"N": "start"}, "shop": True},
}


class Player:
    def __init__(self, name):
        self.name = name
        self.hp = 100
        self.max_hp = 100
        self.xp = 0
        self.level = 1
        self.potions = 3
        self.gold = 50
        self.atk = 1

        # Isaac-style movement
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.radius = 16
        self.speed = 4.2
        self.facing = (0, -1)
        self.invuln_timer = 0  # frames of invulnerability after hit

    def level_up_check(self, log):
        if self.xp >= self.level * 100:
            self.level += 1
            self.max_hp += 20
            self.hp = self.max_hp
            self.atk += 1
            log.append(
                f"LEVEL UP! you are now {self.level} level (+20 HP, +1 ATK)")


class Enemy:
    def __init__(self, name, x, y):
        data = ENEMIES[name]
        self.name = name
        self.hp = data["hp"]
        self.max_hp = data["hp"]
        self.atk = data["atk"]
        self.xp_reward = data["xp"]
        self.gold_reward = data["gold"]
        self.speed = data["speed"]
        self.color = data["color"]
        self.x = x
        self.y = y
        self.radius = 18
        self.hit_cooldown = 0  # cooldown before it can hit player again


class Bullet:
    """Isaac-style projectile fired by the player."""

    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.radius = 6
        self.speed = 9
        self.alive = True


# ---------------------------------------------------------------------------
# GLOBAL GAME STATE
# ---------------------------------------------------------------------------
STATE_NAME_INPUT = "name_input"
STATE_MAP = "map"        # Hollow Knight style map screen
STATE_EXPLORE = "explore"    # Isaac style top-down room
STATE_SHOP = "shop"
STATE_GAME_OVER = "game_over"
STATE_PAUSE_MENU = "pause_menu"

state = STATE_NAME_INPUT
name_input_text = ""
player = None
enemies = []
bullets = []
log = []
MAX_LOG = 6

current_room = "start"
cleared_rooms = set()
room_transition_flash = 0

WALL_MARGIN = 60


def add_log(msg):
    log.append(msg)
    while len(log) > MAX_LOG:
        log.pop(0)


def enter_room(room_id):
    """Load a room: place player near center, spawn enemies if not cleared."""
    global current_room, enemies, bullets, state, room_transition_flash
    current_room = room_id
    bullets = []
    room_transition_flash = 10
    player.x, player.y = WIDTH // 2, HEIGHT // 2

    room = ROOMS[room_id]
    if room.get("shop"):
        state = STATE_SHOP
        log.clear()
        add_log("you are in shop how can i help you?")
        return

    state = STATE_EXPLORE
    enemies = []
    if room_id not in cleared_rooms:
        for i, ename in enumerate(room["enemies"]):
            angle = (i / max(1, len(room["enemies"]))) * math.tau
            ex = WIDTH // 2 + math.cos(angle) * 220
            ey = HEIGHT // 2 + math.sin(angle) * 160
            enemies.append(Enemy(ename, ex, ey))
        if room["enemies"]:
            add_log(f"{', '.join(room['enemies'])} here it is!")
    else:
        add_log("this room is already clear.")


def buy_potion():
    if player.gold >= 10:
        player.gold -= 10
        player.potions += 1
        add_log("buy Health Potion!")
    else:
        add_log("not enough gold!")


def buy_upgrade():
    if player.gold >= 20:
        player.gold -= 20
        player.atk += 1
        add_log(f"sword upgraded! ATK: {player.atk}")
    else:
        add_log("not enough gold!")


# ---------------------------------------------------------------------------
# BUTTON LAYOUTS
# ---------------------------------------------------------------------------
shop_buttons = [
    Button(WIDTH // 2 - 150, 300, 300, 55, "Health Potion - 10g"),
    Button(WIDTH // 2 - 150, 370, 300, 55, "Sword Upgrade - 20g"),
    Button(WIDTH // 2 - 150, 440, 300, 55, "leaved shop"),
]
game_over_buttons = [Button(WIDTH // 2 - 100, 420, 200, 55, "EXIT")]
pause_buttons = [
    Button(WIDTH // 2 - 130, 260, 260, 55, "map"),
    Button(WIDTH // 2 - 130, 330, 260, 55, "character"),
    Button(WIDTH // 2 - 130, 400, 260, 55, "return"),
    Button(WIDTH // 2 - 130, 470, 260, 55, "EXIT"),
]
map_back_btn = Button(WIDTH // 2 - 110, 560, 220, 50, "return")


# ---------------------------------------------------------------------------
# EXPLORE (ISAAC-STYLE) LOGIC
# ---------------------------------------------------------------------------
def update_explore(keys):
    global state

    # --- movement: 8-directional, normalized, Isaac-style ---
    dx = dy = 0
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        dx -= 1
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        dx += 1
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        dy -= 1
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        dy += 1

    if dx != 0 or dy != 0:
        length = math.hypot(dx, dy)
        dx, dy = dx / length, dy / length
        player.facing = (dx, dy)
        player.x += dx * player.speed
        player.y += dy * player.speed

    player.x = max(WALL_MARGIN, min(WIDTH - WALL_MARGIN, player.x))
    player.y = max(WALL_MARGIN + 40, min(HEIGHT - WALL_MARGIN, player.y))

    if player.invuln_timer > 0:
        player.invuln_timer -= 1

    # --- bullets update ---
    for b in bullets[:]:
        b.x += b.dx * b.speed
        b.y += b.dy * b.speed
        if b.x < 0 or b.x > WIDTH or b.y < 0 or b.y > HEIGHT:
            bullets.remove(b)

    # --- enemies chase player ---
    for e in enemies:
        ex_dx = player.x - e.x
        ex_dy = player.y - e.y
        dist = math.hypot(ex_dx, ex_dy)
        if dist > 1:
            e.x += (ex_dx / dist) * e.speed
            e.y += (ex_dy / dist) * e.speed
        if e.hit_cooldown > 0:
            e.hit_cooldown -= 1

        # contact damage
        if dist < player.radius + e.radius and player.invuln_timer == 0:
            player.hp -= e.atk
            player.invuln_timer = 45
            add_log(f"{e.name}-hit you! -{e.atk} HP")
            if player.hp <= 0:
                player.hp = 0
                state = STATE_GAME_OVER

    # --- bullet vs enemy collision ---
    for b in bullets[:]:
        for e in enemies[:]:
            if math.hypot(b.x - e.x, b.y - e.y) < b.radius + e.radius:
                e.hp -= player.atk * 10
                if b in bullets:
                    bullets.remove(b)
                if e.hp <= 0:
                    enemies.remove(e)
                    player.xp += e.xp_reward
                    player.gold += e.gold_reward
                    add_log(
                        f"{e.name} lost! +{e.xp_reward} XP +{e.gold_reward} Gold")
                    player.level_up_check(log)
                break

    # room cleared?
    if not enemies and ROOMS[current_room]["enemies"]:
        cleared_rooms.add(current_room)

    # --- room exits: walk to the edge to transition ---
    room = ROOMS[current_room]
    if not enemies:
        if player.y <= WALL_MARGIN + 45 and "N" in room["exits"]:
            enter_room(room["exits"]["N"])
        elif player.y >= HEIGHT - WALL_MARGIN - 5 and "S" in room["exits"]:
            enter_room(room["exits"]["S"])
        elif player.x <= WALL_MARGIN + 5 and "W" in room["exits"]:
            enter_room(room["exits"]["W"])
        elif player.x >= WIDTH - WALL_MARGIN - 5 and "E" in room["exits"]:
            enter_room(room["exits"]["E"])


def fire_bullet_towards(mx, my):
    dx = mx - player.x
    dy = my - player.y
    dist = math.hypot(dx, dy)
    if dist == 0:
        return
    bullets.append(Bullet(player.x, player.y, dx / dist, dy / dist))


# ---------------------------------------------------------------------------
# DRAW: NAME INPUT
# ---------------------------------------------------------------------------
def draw_name_input():
    screen.fill(BG_DARK)
    draw_text(screen, "MINI RPG", FONT_BIG, GOLD, WIDTH // 2, 160, center=True)
    draw_text(screen, "enter name:", FONT,
              TEXT_MAIN, WIDTH // 2, 240, center=True)
    box = pygame.Rect(WIDTH // 2 - 150, 270, 300, 45)
    draw_panel(screen, box, glow=True)
    draw_text(screen, name_input_text + "|", FONT,
              TEXT_MAIN, box.x + 10, box.y + 10)
    draw_text(screen, "press ENTER for confirmation",
              FONT_SMALL, TEXT_DIM, WIDTH // 2, 340, center=True)


# ---------------------------------------------------------------------------
# DRAW: HUD (used in explore/shop)
# ---------------------------------------------------------------------------
def draw_hud():
    hud_rect = pygame.Rect(10, 10, 300, 34)
    draw_panel(screen, hud_rect)
    draw_bar(screen, 18, 16, 180, 20, player.hp,
             player.max_hp, GREEN, DARK_GREEN)
    draw_text(screen, f"{player.hp}/{player.max_hp}",
              FONT_SMALL, TEXT_MAIN, 205, 18)
    draw_text(screen, f"Lv.{player.level}", FONT_SMALL, ACCENT, 250, 18)

    gold_rect = pygame.Rect(WIDTH - 190, 10, 180, 34)
    draw_panel(screen, gold_rect)
    draw_text(screen, f"Gold: {player.gold}   Pot: {player.potions}", FONT_SMALL, GOLD,
              gold_rect.centerx, gold_rect.centery, center=True)


# ---------------------------------------------------------------------------
# DRAW: EXPLORE (ISAAC-STYLE ROOM)
# ---------------------------------------------------------------------------
def draw_explore():
    screen.fill(BG_DARK)

    # room floor
    floor_rect = pygame.Rect(WALL_MARGIN, WALL_MARGIN + 40,
                             WIDTH - 2 * WALL_MARGIN, HEIGHT - 2 * WALL_MARGIN - 40)
    pygame.draw.rect(screen, (22, 25, 34), floor_rect, border_radius=14)
    pygame.draw.rect(screen, BORDER, floor_rect, 3, border_radius=14)

    room = ROOMS[current_room]
    door_color = ACCENT if not enemies else (60, 65, 75)
    if "N" in room["exits"]:
        pygame.draw.rect(screen, door_color, (WIDTH // 2 - 40,
                         WALL_MARGIN + 30, 80, 20), border_radius=6)
    if "S" in room["exits"]:
        pygame.draw.rect(screen, door_color, (WIDTH // 2 - 40,
                         HEIGHT - WALL_MARGIN - 10, 80, 20), border_radius=6)
    if "W" in room["exits"]:
        pygame.draw.rect(screen, door_color, (WALL_MARGIN - 20,
                         HEIGHT // 2 - 40, 20, 80), border_radius=6)
    if "E" in room["exits"]:
        pygame.draw.rect(screen, door_color, (WIDTH - WALL_MARGIN,
                         HEIGHT // 2 - 40, 20, 80), border_radius=6)

    # bullets
    for b in bullets:
        pygame.draw.circle(screen, ACCENT, (int(b.x), int(b.y)), b.radius)

    # enemies
    for e in enemies:
        pygame.draw.circle(screen, e.color, (int(e.x), int(e.y)), e.radius)
        pygame.draw.circle(screen, (0, 0, 0),
                           (int(e.x), int(e.y)), e.radius, 2)
        bar_w = 44
        draw_bar(screen, int(e.x - bar_w / 2), int(e.y - e.radius - 14),
                 bar_w, 6, e.hp, e.max_hp, RED, DARK_RED)

    # player (flicker while invulnerable)
    if player.invuln_timer == 0 or (player.invuln_timer // 4) % 2 == 0:
        pygame.draw.circle(screen, ACCENT, (int(player.x),
                           int(player.y)), player.radius)
        pygame.draw.circle(screen, (0, 0, 0), (int(
            player.x), int(player.y)), player.radius, 2)
        # small facing indicator
        fx = player.x + player.facing[0] * (player.radius + 6)
        fy = player.y + player.facing[1] * (player.radius + 6)
        pygame.draw.circle(screen, GOLD, (int(fx), int(fy)), 4)

    draw_hud()

    if not enemies and ROOMS[current_room]["enemies"]:
        draw_text(screen, "room is clear go on",
                  FONT_SMALL, TEXT_DIM, WIDTH // 2, 60, center=True)

    draw_text(screen, "WASD movement · mouse left button · ESC menu", FONT_SMALL, TEXT_DIM,
              WIDTH // 2, HEIGHT - 14, center=True)


# ---------------------------------------------------------------------------
# DRAW: MAP (HOLLOW KNIGHT STYLE)
# ---------------------------------------------------------------------------
ROOM_POSITIONS = {
    "start":         (0, 0),
    "goblin_room":   (1, 0),
    "skeleton_room": (2, 0),
    "dragon_room":   (3, 0),
    "shop_room":     (0, 1),
}
ROOM_LABELS = {
    "start": "start",
    "goblin_room": "goblin room",
    "skeleton_room": "skeleton room",
    "dragon_room": "dragon nest",
    "shop_room": "shop",
}


def draw_map():
    screen.fill(BG_DARK)
    draw_text(screen, "map", FONT_BIG, GOLD, WIDTH // 2, 70, center=True)

    cell_w, cell_h = 150, 110
    origin_x, origin_y = 200, 180

    for room_id, (gx, gy) in ROOM_POSITIONS.items():
        rx = origin_x + gx * cell_w
        ry = origin_y + gy * cell_h
        rect = pygame.Rect(rx, ry, 120, 80)

        is_current = room_id == current_room
        is_cleared = room_id in cleared_rooms

        if is_current:
            fill = (40, 55, 65)
            border = ACCENT
        elif is_cleared:
            fill = BG_PANEL
            border = GREEN
        else:
            fill = BG_PANEL
            border = BORDER

        pygame.draw.rect(screen, fill, rect, border_radius=10)
        pygame.draw.rect(screen, border, rect, 3, border_radius=10)
        draw_text(screen, ROOM_LABELS[room_id], FONT_SMALL,
                  TEXT_MAIN, rect.centerx, rect.centery, center=True)

        if is_current:
            draw_text(screen, "★", FONT_SMALL, GOLD,
                      rect.centerx, rect.top - 12, center=True)

        # draw connecting lines
        for direction, target in ROOMS[room_id]["exits"].items():
            if target in ROOM_POSITIONS:
                tgx, tgy = ROOM_POSITIONS[target]
                tx = origin_x + tgx * cell_w + 60
                ty = origin_y + tgy * cell_h + 40
                pygame.draw.line(screen, BORDER, rect.center, (tx, ty), 2)

    draw_text(screen, "green line = room clear",
              FONT_SMALL, TEXT_DIM, WIDTH // 2, 500, center=True)
    map_back_btn.draw(screen, pygame.mouse.get_pos())


# ---------------------------------------------------------------------------
# DRAW: SHOP
# ---------------------------------------------------------------------------
def draw_shop():
    screen.fill(BG_DARK)
    draw_hud()
    draw_text(screen, "shop", FONT_BIG,
              GOLD, WIDTH // 2, 160, center=True)
    mouse_pos = pygame.mouse.get_pos()
    for b in shop_buttons:
        b.draw(screen, mouse_pos)

    log_rect = pygame.Rect(WIDTH // 2 - 250, 500, 500, 100)
    draw_panel(screen, log_rect)
    for i, msg in enumerate(log[-4:]):
        draw_text(screen, msg, FONT_SMALL, TEXT_MAIN,
                  log_rect.x + 12, log_rect.y + 10 + i * 22)


# ---------------------------------------------------------------------------
# DRAW: PAUSE MENU
# ---------------------------------------------------------------------------
def draw_pause_menu():
    draw_explore()  # frozen background
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    draw_text(screen, player.name, FONT_BIG,
              GOLD, WIDTH // 2, 160, center=True)
    mouse_pos = pygame.mouse.get_pos()
    for b in pause_buttons:
        b.draw(screen, mouse_pos)


# ---------------------------------------------------------------------------
# DRAW: GAME OVER
# ---------------------------------------------------------------------------
def draw_game_over():
    screen.fill((0, 0, 0))
    draw_text(screen, "you died", FONT_BIG, RED, WIDTH // 2, 240, center=True)
    draw_text(screen, "Game Over", FONT, TEXT_MAIN,
              WIDTH // 2, 290, center=True)
    draw_text(screen, f"level: {player.level}   gold: {player.gold}", FONT_SMALL, TEXT_DIM,
              WIDTH // 2, 340, center=True)
    mouse_pos = pygame.mouse.get_pos()
    for b in game_over_buttons:
        b.draw(screen, mouse_pos)


# ---------------------------------------------------------------------------
# EVENT HANDLING
# ---------------------------------------------------------------------------
def handle_event(event):
    global state, name_input_text, player, current_room

    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

    if state == STATE_NAME_INPUT:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and name_input_text.strip():
                player = Player(name_input_text.strip())
                enter_room("start")
            elif event.key == pygame.K_BACKSPACE:
                name_input_text = name_input_text[:-1]
            elif len(name_input_text) < 16 and event.unicode.isprintable():
                name_input_text += event.unicode

    elif state == STATE_EXPLORE:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            state = STATE_PAUSE_MENU
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            fire_bullet_towards(*event.pos)

    elif state == STATE_MAP:
        if map_back_btn.clicked(event):
            state = STATE_EXPLORE
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            state = STATE_EXPLORE

    elif state == STATE_SHOP:
        for b in shop_buttons:
            if b.clicked(event):
                if b.text.startswith("Health"):
                    buy_potion()
                elif b.text.startswith("Sword"):
                    buy_upgrade()
                elif b.text.startswith("left"):
                    enter_room(ROOMS[current_room]
                               ["exits"].get("N", current_room))

    elif state == STATE_PAUSE_MENU:
        for b in pause_buttons:
            if b.clicked(event):
                if b.text == "map":
                    state = STATE_MAP
                elif b.text == "character":
                    pass  # could open a character panel later
                elif b.text == "return":
                    state = STATE_EXPLORE
                elif b.text == "EXIT":
                    pygame.quit()
                    sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            state = STATE_EXPLORE

    elif state == STATE_GAME_OVER:
        for b in game_over_buttons:
            if b.clicked(event):
                pygame.quit()
                sys.exit()


# ---------------------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------------------
def main():
    while True:
        for event in pygame.event.get():
            handle_event(event)

        keys = pygame.key.get_pressed()
        if state == STATE_EXPLORE:
            update_explore(keys)

        if state == STATE_NAME_INPUT:
            draw_name_input()
        elif state == STATE_EXPLORE:
            draw_explore()
        elif state == STATE_MAP:
            draw_map()
        elif state == STATE_SHOP:
            draw_shop()
        elif state == STATE_PAUSE_MENU:
            draw_pause_menu()
        elif state == STATE_GAME_OVER:
            draw_game_over()

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
