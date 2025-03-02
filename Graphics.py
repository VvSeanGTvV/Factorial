import random

import pygame
from pygame import Vector2


def getDisplay():
    return pygame.display.Info()


class Window:
    defX, defY = 0, 0
    display = None
    window = None

    currMode = None

    def __init__(self, dx, dy, vx, vy, mode, vsync):
        width, height = vx, vy
        self.defX, self.defY = dx, dy
        self.window = pygame.display
        self.currMode = mode

        # OPENGL CONFIGURATION
        self.window.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        self.window.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        self.window.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        self.window.gl_set_attribute(pygame.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)
        self.window.gl_set_attribute(pygame.GL_ACCELERATED_VISUAL, 1)

        # RETURNS WINDOW
        self.display = self.window.set_mode((width, height), mode, vsync=vsync)

    def changeResolutionMode(self, dx, dy):
        self.window.set_mode((dx, dy))

    def getDisplay(self):
        return self.window.Info()


class text_sprite:
    curr_font = None
    curr_text_surface = None

    def __init__(self, system_font, font_size, string: str, antialias: bool, color):
        self.curr_font = pygame.font.SysFont(system_font, font_size, True)
        self.curr_text_surface = self.curr_font.render(string, antialias, color)
        # self.curr_text_surface = self.curr_font.render("", 0, (0, 0, 0))

    def draw_text(self, screen, position):
        screen.blit(self.curr_text_surface, position)

        pygame.display.update()  # Efficient refresh


class Graphics:
    getTicksLastFrame = 0
    currWin = None

    def __init__(self, newWindow: Window):
        self.currWin = newWindow
        self.getTicksLastFrame = 0

    # DELTA SYSTEM
    def delta(self):
        t = pygame.time.get_ticks()
        # deltaTime in seconds.
        deltaTime = (t - self.getTicksLastFrame) / 1000.0
        self.getTicksLastFrame = t
        return deltaTime

    def getFPS(self):
        delta = self.delta()
        return 1 / delta

    def loopX(self, tileX, IDX, camX, tileSize):
        newX = tileX
        newIDX = IDX
        if (tileX < -(tileSize * 3)):
            newX = (self.currWin.defX * (self.currWin.getDisplay().current_w / self.currWin.defX) - (
                    tileX + tileSize)) + camX
            newIDX += 40
        return newX, newIDX

    def displayTable(self, map, dx, dy, screen, camX, camY):

        tile_size = int(16 * (self.currWin.getDisplay().current_w / self.currWin.defX))

        screen_width = self.currWin.defX * (self.currWin.getDisplay().current_w / self.currWin.defX)
        screen_height = self.currWin.defY * (self.currWin.getDisplay().current_h / self.currWin.defY)
        tiles_x = (screen_width // tile_size) + 2  # Extra columns for smooth looping
        tiles_y = (screen_height // tile_size) + 2  # Extra rows

        for y in range(int(tiles_y)):
            for x in range(int(tiles_x)):
                seed_x = (x + (-camX // tile_size))
                seed_y = (y + (-camY // tile_size))
                random.seed(seed_x * 1000 + seed_y)  # Unique seed per position

                # **Select a tile from the 2D map randomly based on seed**
                tile_x_index = random.randint(0, dx + 1)
                tile_y_index = random.randint(0, dy + 1)
                tileSprite = map[tile_y_index][tile_x_index]
                tileSprite = pygame.transform.scale(tileSprite, (tile_size, tile_size))

                # **Position the tile relative to camera movement**
                tileX = (x * tile_size) - (-camX % tile_size)
                tileY = (y * tile_size) - (-camY % tile_size)

                screen.blit(tileSprite, (tileX, tileY))

        # Update the display
        pygame.display.update()  # Efficient refresh
