import random

import pygame
import sys
import subprocess

from pygame import Vector2
import ctypes

import Mathf
from Graphics import Handler, Window, TextSprite
from UI import Button
from World import Player, Camera, Map

# Initialize Pygame
pygame.init()

# Set window dimensions (dependent on device)
screen_width, screen_height = 0, 0

if sys.platform == "linux":
    output = subprocess.Popen('xrandr | grep "\*" | cut -d" " -f4',shell=True, stdout=subprocess.PIPE).communicate()[0] # Communicate with xrandr (subprocess PIPELINE), get resolution by using SHELL
    resolution = output.split()[0].split(b'x') # Split to two variables (two numbers)
    screen_width, screen_height = int(resolution[0].decode('UTF-8')), int(resolution[1].decode('UTF-8')) # Decode by UTF-8 and use it as its resolution
if sys.platform == "win32":
    user32 = ctypes.windll.user32  # Get win32 file (in Windows)
    user32.SetProcessDPIAware()  # Calculate DPI (used for high DPI display)
    screen_width, screen_height = (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)) # Get the resolution by System Metrics

game_width, game_height = 640, 360
window = Window(game_width, game_height, screen_width, screen_height, pygame.FULLSCREEN, 60, 0)
graphic_handler = Handler(window, 1)

# Set window title
pygame.display.set_caption("Factorial [DEV-02]")

# Game loop
running = True

velX = 0
velY = 0
speed = 1
maxVel = 10
pygame.font.init()


def close():
    pygame.quit()
    sys.exit()




player = Player(0, 0, pygame.image.load("assets/player/halberd-ship.png"), 24, graphic_handler)
camera = Camera(0, 0)
world = Map(window, 256, graphic_handler, 8)

options_opened = False
show_stats = True
in_game = False
def toggle_options():
    global options_opened
    options_opened = not options_opened

def toggle_stats():
    global show_stats
    show_stats = not show_stats
    toggle_options()

def toggle_play():
    global in_game
    in_game = not in_game
    toggle_options()

options_button = Button(TextSprite('raster.ttf', 16,
                                f"options", True,
                                (255, 255, 255), graphic_handler
                                ), 120, 20, (50, 50, 50), (205, 205, 205), (125, 125, 125), lambda: toggle_options()
                     )

quit_button = Button(TextSprite('raster.ttf', 16,
                                f"quit game", True,
                                (255, 255, 255), graphic_handler
                                ), 120, 20, (0, 0, 0), (205, 205 , 205), (125, 125, 125), lambda: close()
                     )

stat_button = Button(TextSprite('raster.ttf', 16,
                                f"advanced stats", True,
                                (255, 255, 255), graphic_handler
                                ), 120, 20, (0, 0, 0), (205, 205 , 205), (125, 125, 125), lambda: toggle_stats()
                     )

play_button = Button(TextSprite('raster.ttf', 16,
                                f"play game", True,
                                (255, 255, 255), graphic_handler
                                ), 120, 20, (0, 0, 0), (205, 205 , 205), (125, 125, 125), lambda: toggle_play()
                     )

testText = TextSprite('raster.ttf', 16,
                      f"X: {int(camera.get_world_position(16).x)} | Y: {int(camera.get_world_position(16).y)} | "
                      f"FPS: {int(graphic_handler.getFPS())}", False,
                      (255, 255, 255), graphic_handler
                      )

title = TextSprite('bluescreen.ttf', 50,
                      "FACTORIAL", False,
                      (128, 128, 255), graphic_handler
                      )

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # HANDLER FPS
    delta = graphic_handler.delta_target()

    if in_game:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            velX += speed * delta
        if keys[pygame.K_d]:
            velX -= speed * delta

        if keys[pygame.K_w]:
            velY += speed * delta
        if keys[pygame.K_s]:
            velY -= speed * delta

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

        testText.draw_text(window.display, Vector2(16, 16))
        string_stats = f"X: {int(camera.get_world_position(16).x)} | Y: {int(camera.get_world_position(16).y)} | FPS: {int(graphic_handler.getFPS())}"
        if show_stats:
            string_stats = string_stats + f" | OS: {sys.platform} | Resolution: {screen_width}x{screen_height}"
        testText.update_text(string_stats)

        player.render(window.display, -camera.pos.x, -camera.pos.y, Vector2(velX, velY))

        if options_opened:
            quit_button.render(window.display, Vector2(game_width - 60, 10))
            quit_button.update()

            stat_button.render(window.display, Vector2(game_width - 60, 20))
            stat_button.update()

        options_button.render(window.display, Vector2(game_width - 60, 0))
        options_button.update()
    else:
        window.display.fill((0,0,0))
        title.draw_text(window.display, Vector2((game_width / 3), 32))
        if options_opened:
            quit_button.render(window.display, Vector2(game_width - 60, 10))
            quit_button.update()

            play_button.render(window.display, Vector2(game_width - 60, 20))
            play_button.update()

        options_button.render(window.display, Vector2(game_width - 60, 0))
        options_button.update()

    # Update the display
    pygame.display.update()  # Efficient refresh

# Quit Pygame
pygame.quit()
sys.exit()
