import pygame
import asyncio
import math

pygame.init()

WIDTH, HEIGHT = 999, 452
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Little Guy, Big Picture")
clock = pygame.time.Clock()
world = pygame.Surface((WIDTH, HEIGHT))

M1 = pygame.Rect(570, 280, 100, 14)
M2 = pygame.Rect(420, 215, 100, 14)
M3 = pygame.Rect(570, 150, 100, 14)

LEVELS = [
    {
        "bg": (20, 20, 30),
        "platforms": [
            pygame.Rect(0, HEIGHT - 40, WIDTH, 40),
            pygame.Rect(300, 340, 120, 14),
            pygame.Rect(500, 280, 120, 14),
        ],
        "key": pygame.Rect(540, 264, 10, 10),
        "door": pygame.Rect(900, HEIGHT - 80, 24, 40),
        "start": (100, 100),
    },
    {
        "bg": (60, 20, 80),
        "platforms": [
            pygame.Rect(0, HEIGHT - 40, WIDTH, 40),
            pygame.Rect(180, 340, 110, 14),
            pygame.Rect(330, 270, 110, 14),
            pygame.Rect(180, 200, 110, 14),
            pygame.Rect(40, 135, 110, 14),
        ],
        "key": pygame.Rect(80, 121, 10, 10),
        "door": pygame.Rect(900, HEIGHT - 80, 24, 40),
        "start": (150, HEIGHT - 40 - 27),
        "speck": pygame.Rect(40, HEIGHT - 40 - 45, 100, 45),
        "cursor": (700, 60),
    },
    {
        "bg": (15, 40, 80),
        "platforms": [
            pygame.Rect(0, HEIGHT - 40, WIDTH, 40),
            pygame.Rect(720, 345, 100, 14),
            M1,
            M2,
            M3,
            pygame.Rect(720, 90, 100, 14),
        ],
        "movers": [
            {"rect": M1, "min": 480, "max": 740, "speed": 2},
            {"rect": M2, "min": 380, "max": 580, "speed": 2},
            {"rect": M3, "min": 520, "max": 720, "speed": 3},
        ],
        "key": pygame.Rect(765, 74, 10, 10),
        "door": pygame.Rect(40, HEIGHT - 80, 24, 40),
        "start": (835, HEIGHT - 40 - 27),
        "speck": pygame.Rect(WIDTH - 140, HEIGHT - 40 - 45, 100, 45),
        "cursor": (120, 60),
    },
]

font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 28)

CURSOR_SPEED = 1.4
CLICK_RANGE = 120
CLICK_FRAMES = 40
RING_END_R = 45
ARROW = [(0,0), (0,40), (10,31), (18,48), (25,45), (17,28), (30, 28)]

MON_SCREEN = pygame.Rect(300, 120, 400, 180)
MON_FRAME = pygame.Rect(270, 90, 460, 250)

def draw_outside(surface):
    surface.fill((110, 75, 45))
    pygame.draw.rect(surface, (25, 25, 30), MON_FRAME, border_radius=8)
    pygame.draw.rect(surface, (10, 10, 14), MON_SCREEN)
    pygame.draw.rect(surface, (35, 35, 40), (480, 330, 40, 40))
    pygame.draw.rect(surface, (35, 35, 40), (420, 370, 160, 14))
    pygame.draw.rect(surface, (60, 60, 68), (330, 395, 340, 40), border_radius = 4)
    for row in range(3):
        for col in range(15):
            pygame.draw.rect(surface, (90, 90, 100), (338 + col * 21, 401 + row * 11, 17, 7))
    pygame.draw.rect(surface, (230, 230, 235), (790, 385, 36, 44 ))
    pygame.draw.rect(surface, (230, 230, 235), (822, 395, 14, 22), 4)

def solids(level, speck_on):
    s = list(level["platforms"])
    if speck_on and "speck" in level:
        s.append(level["speck"])
    return s

def draw_cursor(surface, x, y, scale=2.5):
    pts = [(x + px * scale,y + py * scale) for px, py in ARROW]
    pygame.draw.polygon(surface, (255, 255, 255), pts)
    pygame.draw.polygon(surface, (0, 0, 0), pts, 3)

def draw_level(surface, platforms, key, door, has_key, bg):
    surface.fill((bg))
    for p in platforms:
        pygame.draw.rect(surface, (90, 90, 120), p)
    if not has_key:
        pygame.draw.rect(surface, (255, 215, 0), key)
    door_color = (200, 140, 40) if has_key else (70, 50, 25)
    pygame.draw.rect(surface, door_color, door)

async def main():
    level_idx = 0
    level = LEVELS[level_idx]

    player = pygame.Rect(0, 0, 21, 27)
    player.topleft = level["start"]
    has_key = False
    level_done = False
    vel_y = 0
    on_ground = False

    zooming = False
    zoom_t = 0.0
    old_room = None
    speck_img = None

    final_room = None
    ending = False
    end_t = 0.0

    deaths = 0
    cur = {"x": 0.0, "y": 0.0, "state": "chase", "timer": 0,
           "cool": 0, "lock": (0, 0)}

    def place_cursor():
        if "cursor" in level:
            cur["x"], cur["y"] = level["cursor"]
            cur["state"] = "chase"
            cur["timer"] = 0
            cur["cool"] = 90

    def reset_level():
        nonlocal has_key, vel_y, deaths
        player.topleft = level["start"]
        has_key = False
        vel_y = 0
        deaths += 1
        place_cursor()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        walls = solids(level, speck_img is not None)
        prev_x = player.x
        for mv in level.get("movers", []):
            r = mv["rect"]
            on_top = (player.bottom == r.top and player.right > r.left and player.left < r.right)
            old_x = r.x
            r.x += mv["speed"]
            if r.left < mv["min"] or r.right > mv["max"]:
                mv["speed"] *= -1
                r.x = old_x + mv["speed"]
            moved = r.x - old_x
            if on_top:
                player.x += moved
            elif player.colliderect(r):
                if moved > 0:
                    player.left = r.right
                else:
                    player.right = r.left
        if not (zooming or ending):
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player.x -= 7 #You can guess my fav player from here
            if keys[pygame.K_RIGHT]:
                player.x += 7
            if keys[pygame.K_SPACE] and on_ground:
                vel_y = -12.25
        dx = player.x - prev_x

        for p in walls:
            if player.colliderect(p):
                if dx > 0:
                    player.right = p.left
                elif dx < 0:
                    player.left = p.right

        vel_y += 0.676 ##It is not random but square of my birthday :)
        player.y += round(vel_y)
        player.clamp_ip(screen.get_rect())

        on_ground = False
        for p in walls:
            if player.colliderect(p):
                if vel_y > 0:
                    player.bottom = p.top
                    vel_y = 0
                    on_ground = True
                elif vel_y < 0:
                    player.top = p.bottom
                    vel_y = 0

        if "cursor" in level and not (zooming or ending or level_done):
            if cur["state"] == "chase":
                tx = player.centerx - cur["x"]
                ty = player.centery - cur["y"]
                dist = math.hypot(tx, ty)
                if cur["cool"] > 0:
                    cur["cool"] -= 1
                if dist < CLICK_RANGE and cur["cool"] == 0:
                    cur["state"] = "click"
                    cur["timer"] = CLICK_FRAMES
                    cur["lock"] = player.center
                elif dist > 1:
                    cur["x"] += tx / dist * CURSOR_SPEED
                    cur["y"] += ty / dist * CURSOR_SPEED
            else:
                cur["timer"] -= 1
                if cur["timer"] <= 0:
                    lx, ly = cur["lock"]
                    hit = math.hypot(player.centerx - lx, player.centery - ly) <= RING_END_R
                    if hit:
                        reset_level()
                    else:
                        cur["state"] = "chase"
                        cur["cool"] = 60

        if player.colliderect(level["key"]):
            has_key = True
        if has_key and player.colliderect(level["door"]) and not level_done:
            level_done = True
            if level_idx + 1 < len(LEVELS):
                old_room = pygame.Surface((WIDTH, HEIGHT))
                draw_level(old_room, level["platforms"], level["key"],
                           level["door"], True, level["bg"]) 
                if "speck" in level and speck_img is not None:
                    old_room.blit(speck_img, level["speck"].topleft)
                zooming = True
                zoom_t = 0.0
            else:
                final_room = pygame.Surface((WIDTH, HEIGHT))
                draw_level(final_room, level["platforms"], level["key"], level["door"], True, level["bg"])
                if "speck" in level and speck_img is not None:
                    final_room.blit(speck_img, level["speck"].topleft)
                ending = True
                end_t = 0.0

        if zooming:
            zoom_t = min(1.0, zoom_t + 1 / 135)

        if ending:
            end_t = min(1.0, end_t + 1 / 180)

        draw_level(world, level["platforms"], level["key"], level["door"], has_key, level["bg"])
        if "speck" in level and speck_img is not None:
            world.blit(speck_img, level["speck"].topleft)
        pygame.draw.rect(world,(255, 200, 80), player)

        if "cursor" in level:
            if cur["state"] == "click":
                frac = cur["timer"] / CLICK_FRAMES
                r = int(RING_END_R + (CLICK_RANGE - RING_END_R) * frac)
                pygame.draw.circle(world, (255, 80, 80), cur["lock"], max(r, 2), 3)
            draw_cursor(world, cur["x"], cur["y"])

        label = small_font.render(f"Clicked: {deaths}", True, (230, 230, 235))
        world.blit(label, (12, 10))

        if ending:
            draw_outside(screen)
            x = int(MON_SCREEN.x * end_t)
            y = int(MON_SCREEN.y * end_t)
            w = max(1, int(WIDTH + (MON_SCREEN.w - WIDTH) * end_t))
            h = max(1, int(HEIGHT + (MON_SCREEN.h - HEIGHT) * end_t))
            screen.blit(pygame.transform.smoothscale(final_room, (w, h)), (x, y))
            if end_t >= 1.0:
                text = font.render("You were never the main character.", True, (245, 235, 215))
                screen.blit(text, text.get_rect(center=(WIDTH // 2, 45)))
                times = "time" if deaths == 1 else "times"
                sub = small_font.render(f"You were clicked {deaths} {times}.", True, (245, 235, 215))
                screen.blit(sub, sub.get_rect(center=(WIDTH // 2, 77)))
        elif zooming:
            nxt = LEVELS[level_idx + 1]
            draw_level(screen, nxt["platforms"], nxt["key"], nxt["door"], False, nxt["bg"])
            sp = nxt["speck"]
            x = int(sp.x * zoom_t)
            y = int(sp.y * zoom_t)
            w = max(1, int(WIDTH + (sp.w - WIDTH) * zoom_t))
            h = max(1, int(HEIGHT + (sp.h - HEIGHT) * zoom_t))
            small = pygame.transform.smoothscale(old_room, (w, h))
            screen.blit(small, (x, y))

            if zoom_t >= 1.0:
                level_idx += 1
                level = LEVELS[level_idx]
                has_key = False
                level_done = False
                vel_y = 0
                player.topleft = level["start"]
                speck_img = pygame.transform.smoothscale(old_room, level["speck"].size)
                zooming = False
                place_cursor()
        else:
            screen.blit(world, (0,0))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)    

    pygame.quit()

asyncio.run(main())

