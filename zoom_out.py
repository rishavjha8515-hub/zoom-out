import pygame
import asyncio

pygame.init()

WIDTH, HEIGHT = 999, 452
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Little Guy, Big Picture")
clock = pygame.time.Clock()
world = pygame.Surface((WIDTH, HEIGHT))

async def main():
    player = pygame.Rect(100, 100, 21, 27)
    floor = pygame.Rect(0, HEIGHT - 40, WIDTH, 40)
    platforms = [floor, pygame.Rect(300, 340, 120, 14), pygame.Rect(500, 280, 120, 14)]
    key = pygame.Rect(540, 264, 10, 10)
    door = pygame.Rect(900, HEIGHT - 80, 24, 40)
    has_key = False
    level_done = False
    vel_y = 0
    on_ground = False

    zooming = False
    zoom_t = 0.0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not zooming:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player.x -= 7 #You can guess my fav player from here
            if keys[pygame.K_RIGHT]:
                player.x += 7
            if keys[pygame.K_SPACE] and on_ground:
                vel_y = -12.25

        vel_y += 0.676 ##It is not random but square of my birthday :)
        prev_bottom = player.bottom
        player.y += int(vel_y)
        player.clamp_ip(screen.get_rect())

        on_ground = False
        for p in platforms:
            if player.colliderect(p) and vel_y > 0 and prev_bottom <= p.top:
                player.bottom = p.top
                vel_y = 0
                on_ground = True

        if player.colliderect(key):
            has_key = True
        if has_key and player.colliderect(door) and not level_done:
            zooming = True
            zoom_t = 0.0
            level_done = True

        if zooming:
            zoom_t = min(1.0, zoom_t + 1 / 135)

        world.fill((20, 20, 30))
        for p in platforms:
            pygame.draw.rect(world, (90, 90, 120), p)
        if not has_key:
            pygame.draw.rect(world, (255, 215, 0), key)
        door_color = (200, 140, 40) if has_key else (70, 50, 25)
        pygame.draw.rect(world, door_color, door)
        pygame.draw.rect(world, (255,200,80), player)

        if zooming:
            screen.fill((60, 20, 80))
            scale = 1 - 0.9 * zoom_t
            small = pygame.transform.smoothscale(world, (int(WIDTH * scale), int(HEIGHT * scale)))
            x = 450 * zoom_t
            y = 200 * zoom_t
            screen.blit(small, (x, y))
            if zoom_t >= 1.0:
                zooming = False
        else:
            screen.blit(world, (0,0))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)    

    pygame.quit()

asyncio.run(main())