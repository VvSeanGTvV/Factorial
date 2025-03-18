import random

import pygame
import sys
import subprocess

from pygame import Vector2
import ctypes

import Mathf
import World
from Graphics import Handler, Window, TextSprite
from UI import Button
from World import Player, Camera, Map, Block

# Initialize Pygame & fonts module & mixer/audio module
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Load the music file
pygame.mixer.music.load('assets/musics/menu.ogg')

# Set window dimensions (dependent on device)
screen_width, screen_height = 0, 0

if sys.platform == "win32":  # WINDOWS (32-BIT) Resolution
    user32 = ctypes.windll.user32  # Get win32.dll file (in Windows)
    user32.SetProcessDPIAware()  # Calculate DPI (used for high DPI display)
    screen_width, screen_height = (
        user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))  # Get the resolution by System Metrics
if sys.platform == "linux":  # LINUX Resolution
    output = subprocess.Popen('xrandr | grep "\*" | cut -d" " -f4', shell=True, stdout=subprocess.PIPE).communicate()[
        0]  # Communicate with xrandr (subprocess PIPELINE), get resolution by using SHELL
    resolution = output.split()[0].split(b'x')  # Split to two variables (two numbers)
    screen_width, screen_height = int(resolution[0].decode('UTF-8')), int(
        resolution[1].decode('UTF-8'))  # Decode by UTF-8 and use it as its resolution

game_width, game_height = 640, 360
window = Window(game_width, game_height, screen_width, screen_height, pygame.FULLSCREEN, 60, 0)
graphic_handler = Handler(window, 1)

# Set window title
pygame.display.set_caption("Factorial [DEVELOPMENT]")

# Game loop
running = True

velX = 0
velY = 0
speed = 1
maxVel = 10


def close():
    pygame.quit()
    sys.exit()


build = 13  # BUILD VERSION
player = Player(0, 0, pygame.image.load("assets/player/halberd-ship.png"), 24, graphic_handler)
camera = Camera(0, 0)
world = Map(window, 1024, graphic_handler, 8)

options_opened = False
show_stats = False
in_game = False


### SETTINGS BUTTONS TODO new ui
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


def toggle_play_option():
    toggle_play()
    toggle_options()


### SETTINGS BUTTONS TODO new ui
settings_button = Button(TextSprite('raster.ttf', 16,
                                    f"settings", False,
                                    (255, 255, 255), graphic_handler
                                    ), 120, 20, (50, 50, 50), (205, 205, 205), (125, 125, 125), lambda: toggle_options()
                         )

quit_button = Button(TextSprite('raster.ttf', 16,
                                f"exit to menu", False,
                                (255, 255, 255), graphic_handler
                                ), 120, 20, (50, 50, 50), (205, 205, 205), (125, 125, 125), lambda: toggle_play_option()
                     )

desktop_button_settings = Button(TextSprite('raster.ttf', 16,
                                            f"exit to desktop", False,
                                            (255, 255, 255), graphic_handler
                                            ), 120, 20, (50, 50, 50), (205, 205, 205), (125, 125, 125), lambda: close()
                                 )

stat_button = Button(TextSprite('raster.ttf', 16,
                                f"advanced stats", False,
                                (255, 255, 255), graphic_handler
                                ), 120, 20, (50, 50, 50), (205, 205, 205), (125, 125, 125), lambda: toggle_stats()
                     )
option_button = [quit_button, desktop_button_settings, stat_button]

### MENU BUTTONS
play_button = Button(TextSprite('raster.ttf', 16,
                                f"PLAY", False,
                                (255, 255, 255), graphic_handler
                                ), 120 * 2, 20 * 2, (50, 50, 50), (205, 205, 205), (125, 125, 125),
                     lambda: toggle_play()
                     )
desktop_button = Button(TextSprite('raster.ttf', 16,
                                   f"QUIT GAME", False,
                                   (255, 255, 255), graphic_handler
                                   ), 120 * 3, 20 * 2, (50, 50, 50), (205, 205, 205), (125, 125, 125), lambda: close()
                        )
menu_button = [play_button, desktop_button]

testText = TextSprite('raster.ttf', 16,
                      f"X: {int(camera.get_world_position(16).x)} | Y: {int(camera.get_world_position(16).y)} | "
                      f"FPS: {int(graphic_handler.getFPS())}", False,
                      (255, 255, 255), graphic_handler
                      )

title = TextSprite('bluescreen.ttf', 50,
                   "F A C T O R I A L", False,
                   (0, 255, 255), graphic_handler
                   )
title_shadow = TextSprite('bluescreen.ttf', 50,
                   "F A C T O R I A L", False,
                   (0, 255/8, 255/6), graphic_handler
                          )

version = TextSprite('aeogo.ttf', 12,
                     f"b{build} [{sys.platform} BUILD]", False,
                     (0, 255, 255), graphic_handler
                     )
placing = None
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for block in World.Blocks:  # Assuming `blocks` is a list of all blocks
                block.handle_mouse_click(mouse_pos, camera.pos)

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

        if keys[pygame.K_1]:
            placing = Block(1, pygame.image.load("assets/stone-melter.png"), 3, graphic_handler)

        if keys[pygame.K_2]:
            placing = Block(2, pygame.image.load("assets/command-center.png"), 5, graphic_handler)

        if keys[pygame.K_3]:
            placing = Block(3, pygame.image.load("assets/omega-pad.png"), 8, graphic_handler)

        if pygame.mouse.get_pressed()[2]:
            if isinstance(placing, Block):
                placing = None

        if pygame.mouse.get_pressed()[0]:
            if isinstance(placing, Block):
                placing.place_action(player)
                placing = None
            else:
                placing = None

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

        # FLOOR TILE RENDER
        world.update_animation()
        world.render(camera.pos.x, camera.pos.y)

        string_stats = f"X: {int(camera.get_world_position(16).x)} | Y: {int(camera.get_world_position(16).y)} | FPS: {int(graphic_handler.getFPS())}"
        if show_stats:
            string_stats = string_stats + f" | OS: {sys.platform} | Resolution: {screen_width}x{screen_height}"
        testText.update_text(string_stats)

        # BLOCK RENDER LAYER
        if len(World.Blocks) > 0:
            for block in World.Blocks:
                block.render(window.display, camera.pos)
                block.update(delta, camera.pos)

        if isinstance(placing, Block):
            placing.render(window.display, camera.pos)

        # PLAYER RENDER LAYER
        player.render(window.display, -camera.pos.x, -camera.pos.y, Vector2(velX, velY))

        # UI RENDER LAYER
        testText.draw_text(window.display, Vector2(16, 16))
        if options_opened:
            quit_button.render(window.display, Vector2(game_width - 60, 10))
            desktop_button_settings.render(window.display, Vector2(game_width - 60, 20))
            stat_button.render(window.display, Vector2(game_width - 60, 30))
            for option_but in option_button:
                option_but.update()

        settings_button.render(window.display, Vector2(game_width - 60, 0))
        settings_button.update()
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
    else:
        window.display.fill((0, 0, 0))
        title_shadow.draw_text(window.display, Vector2((game_width - title.get_text_rect().width) / 2 + 4, 36))

        title.draw_text(window.display, Vector2((game_width - title.get_text_rect().width) / 2, 32))
        version.draw_text(window.display, Vector2((game_width - title.get_text_rect().width) / 2, 86))

        play_button.render(window.display, Vector2((game_width - (play_button.get_rect().width / 2)) / 2, 230))
        desktop_button.render(window.display, Vector2((game_width - (desktop_button.get_rect().width / 2)) / 2, 260))
        for menu_but in menu_button:
            menu_but.update()

        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(loops=-1)

    # Update the display
    pygame.display.update()  # Efficient refresh

# Quit Pygame
pygame.quit()
sys.exit()
