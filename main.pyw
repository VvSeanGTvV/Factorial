import random

import pygame
import sys

from pygame import Vector2
import ctypes

import Mathf
from Graphics import Handler, Window, TextSprite
from UI import Button
from World import Player, Camera, Map

# Initialize Pygame
pygame.init()

# Set window dimensions
user32 = ctypes.windll.user32 # Get win32 file
user32.SetProcessDPIAware() # Calculate DPI (used for high DPI display)
screen_width, screen_height = (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
window = Window(640, 360, screen_width, screen_height, pygame.FULLSCREEN, 60, 0)
graphic_handler = Handler(window, 1)

# Set window title
pygame.display.set_caption("Factorial [DEV-01]")

# Game loop
running = True

velX = 0
velY = 0
speed = 1
maxVel = 10
pygame.font.init()

player = Player(0, 0, pygame.image.load("assets/player/halberd-ship.png"), 24, graphic_handler)
camera = Camera(0, 0)
world = Map(window, 256, graphic_handler, 8)
button_test = Button(TextSprite('Arial', 16,
                               f"welcome", False,
                               (255, 255, 255), graphic_handler
                               ), 120, 40, (0,0,0), (255,255,255), (125,125,125))

testText = TextSprite('Arial', 16,
                      f"X: {int(camera.get_world_position(16).x)} | Y: {int(camera.get_world_position(16).y)} | "
                      f"FPS: {int(graphic_handler.getFPS())}", False,
                      (255, 255, 255), graphic_handler
                      )
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # HANDLER FPS
    delta = graphic_handler.delta_target()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        velX += speed * delta
    if keys[pygame.K_d]:
        velX -= speed * delta

    if keys[pygame.K_w]:
        velY += speed * delta
    if keys[pygame.K_s]:
        velY -= speed * delta

    if keys[pygame.K_x]:
        # Quit Pygame
        pygame.quit()
        sys.exit()

    if keys[pygame.K_m]:
        player.update_position_world(-sys.maxsize // 100, -sys.maxsize // 100)

    camera.update_position(
        Mathf.lerp(camera.pos.x, -player.worldx, delta / 25),
        Mathf.lerp(camera.pos.y, -player.worldy, delta / 25)
    )

    px, py = player.get_position()
    player.update_position_world(player.worldx - velX, player.worldy - velY)


    if (velX > maxVel * delta):
        velX -= velX / maxVel

    if (velX < -maxVel * delta):
        velX += -velX / maxVel

    if (velX < 0):
        velX += -velX / maxVel
    if (velX > 0):
        velX -= velX / maxVel

    if (velY > maxVel * delta):
        velY -= velY / maxVel
    if (velY < -maxVel * delta):
        velY += -velY / maxVel

    if (velY < 0):
        velY += -velY / maxVel
    if (velY > 0):
        velY -= velY / maxVel
    window.display.fill((0, 0, 0))

    world.update_animation()
    world.render(camera.pos.x, camera.pos.y)

    testText.draw_text(window.display, (16, 16))
    testText.update_text(
        f"X: {int(camera.get_world_position(16).x)} | Y: {int(camera.get_world_position(16).y)} | "
        f"FPS: {int(graphic_handler.getFPS())}"
    )

    player.render(window.display, -camera.pos.x, -camera.pos.y, Vector2(velX, velY))
    button_test.render(window.display, Vector2(25, 25))

    # Update the display
    pygame.display.update()  # Efficient refresh

# Quit Pygame
pygame.quit()
sys.exit()
