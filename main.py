import pygame
import asyncio

pygame.init()

WIDTH, HEIGHT = 999, 452
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Little Guy, Big Picture")
clock = pygame.time.Clock()
world = pygame.Surface((WIDTH, HEIGHT))

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
        "speck": pygame.Rect(40, HEIGHT - 40 - 45, 100, 45)
    },
    {
        "bg": (15, 40, 80),
        "platforms": [
            pygame.Rect(0, HEIGHT - 40, WIDTH, 40),
            pygame.Rect(720, 345, 100, 14),
            pygame.Rect(570, 280, 100, 14),
            pygame.Rect(420, 215, 100, 14),
            pygame.Rect(570, 150, 100, 14),
            pygame.Rect(720, 90, 100, 14),
        ],
        "key": pygame.Rect(765, 74, 10, 10),
        "door": pygame.Rect(40, HEIGHT - 80, 24, 40),
        "start": (835, HEIGHT - 40 - 27),
        "speck": pygame.Rect(WIDTH - 140, HEIGHT - 40 - 45, 100, 45),
    },
]

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

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        prev_x = player.x
        if not zooming:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player.x -= 7 #You can guess my fav player from here
            if keys[pygame.K_RIGHT]:
                player.x += 7
            if keys[pygame.K_SPACE] and on_ground:
                vel_y = -12.25
        dx = player.x - prev_x

        for p in level["platforms"]:
            if player.colliderect(p):
                if dx > 0:
                    player.right = p.left
                elif dx < 0:
                    player.left = p.right

        vel_y += 0.676 ##It is not random but square of my birthday :)
        player.y += round(vel_y)
        player.clamp_ip(screen.get_rect())

        on_ground = False
        for p in level["platforms"]:
            if player.colliderect(p):
                if vel_y > 0:
                    player.bottom = p.top
                    vel_y = 0
                    on_ground = True
                elif vel_y < 0:
                    player.top = p.bottom
                    vel_y = 0

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
                print("all levels complete")


        if zooming:
            zoom_t = min(1.0, zoom_t + 1 / 135)

        draw_level(world, level["platforms"], level["key"], level["door"], has_key, level["bg"])
        if "speck" in level and speck_img is not None:
            world.blit(speck_img, level["speck"].topleft)
        pygame.draw.rect(world,(255, 200, 80), player)

        if zooming:
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
        else:
            screen.blit(world, (0,0))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)    

    pygame.quit()

asyncio.run(main())

