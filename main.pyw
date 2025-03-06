import pygame
import sys

from pygame import Vector2

import Mathf
from Graphics import Graphics, Window, text_sprite
from World import Player, Camera, Map

# Initialize Pygame
pygame.init()

# Set window dimensions
window = Window(640, 360, 1280, 720, pygame.FULLSCREEN, 60, 0)
graphic_handler = Graphics(window, 1)

# Set window title
pygame.display.set_caption("Factorial [DEVELOPMENT]")

# Game loop
running = True

velX = 0
velY = 0
speed = 10
maxVel = 50
pygame.font.init()

player = Player(0, 0, pygame.image.load("assets/player/halberd-ship.png"), 24, graphic_handler)
camera = Camera(0, 0)
world = Map(window, 512, graphic_handler)


while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # HANDLER FPS
    gameSpeed = graphic_handler.delta()
    scalarX, scalarY = graphic_handler.getWindowScale()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        velX += speed * gameSpeed
    if keys[pygame.K_d]:
        velX -= speed * gameSpeed

    if keys[pygame.K_w]:
        velY += speed * gameSpeed
    if keys[pygame.K_s]:
        velY -= speed * gameSpeed

    if keys[pygame.K_x]:
        # Quit Pygame
        pygame.quit()
        sys.exit()

    if keys[pygame.K_m]:
        player.update_position_world(-sys.maxsize // 10, -sys.maxsize // 10)

    camera.update_position(
        Mathf.lerp(camera.pos.x, -player.worldx, speed * gameSpeed / scalarX),
        Mathf.lerp(camera.pos.y, -player.worldy, speed * gameSpeed / scalarY)
    )

    px, py = player.get_position()
    player.update_position_world(player.worldx - velX, player.worldy - velY)


    if (velX > maxVel / 10):
        velX -= velX / maxVel

    if (velX < -maxVel / 10):
        velX += -velX / maxVel

    if (velX < 0):
        velX += -velX / maxVel
    if (velX > 0):
        velX -= velX / maxVel

    if (velY > maxVel / 10):
        velY -= velY / maxVel
    if (velY < -maxVel / 10):
        velY += -velY / maxVel

    if (velY < 0):
        velY += -velY / maxVel
    if (velY > 0):
        velY -= velY / maxVel
    # print(velX, velY)
    window.display.fill((0, 0, 0))
    world.render(
        world.preload_tiles(["gold-sand1.png", "gold-sand2.png", "gold-sand3.png", "silver-plating.png", "basalt1.png"]),
        camera.pos.x * scalarX, camera.pos.y * scalarY, 1)

    testText = text_sprite('Arial', 16,
                           f"X: {int(camera.get_world_position(16).x)} | Y: {int(camera.get_world_position(16).y)}", False,
                           (255, 255, 255), graphic_handler
                           )

    text_sprite.draw_text(testText, window.display, (16, 16))
    player.render(window.display, -camera.pos.x, -camera.pos.y, Vector2(velX, velY))

    # Update the display
    pygame.display.update()  # Efficient refresh

# Quit Pygame
pygame.quit()
sys.exit()
