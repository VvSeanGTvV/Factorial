import random

import pygame
from pygame import Vector2

def getDisplay():
    return pygame.display.Info()


class Window:
    def __init__(self, dx, dy, vx, vy, mode, fpsLock, vsync):
        width, height = vx, vy
        self.defX, self.defY = dx, dy
        self.window = pygame.display
        self.currMode = mode
        self.lockFPS = fpsLock

        # OPENGL CONFIGURATION
        flags = pygame.HWSURFACE | pygame.DOUBLEBUF | mode
        self.window.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        self.window.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        self.window.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        self.window.gl_set_attribute(pygame.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)
        self.window.gl_set_attribute(pygame.GL_ACCELERATED_VISUAL, 1)

        # RETURNS WINDOW
        self.display = self.window.set_mode((width, height), flags, mode, vsync=vsync)

    def changeResolutionMode(self, dx, dy):
        self.window.set_mode((dx, dy))

    def getDisplay(self):
        return self.window.Info()


class Graphics:

    def __init__(self, window: Window, super_sample):
        self.curr_win = window
        self.clock = pygame.time.Clock()
        self.super_sample = super_sample

    # DELTA SYSTEM
    def delta(self):
        # Calculate delta time
        pygame.time.Clock()
        delta_time = self.clock.tick(self.curr_win.lockFPS) / 1000  # Convert milliseconds to seconds
        delta_time = min(delta_time, 0.1)
        return delta_time

    def getFPS(self):
        return 1 / self.delta()

    def getWindowSize(self):
        return self.curr_win.defX, self.curr_win.defY

    def getActiveDisplaySize(self):
        return self.curr_win.getDisplay().current_w, self.curr_win.getDisplay().current_h

    def getWindowScale(self):
        def_x, def_y = self.getWindowSize()
        return (self.curr_win.getDisplay().current_w / def_x), (self.curr_win.getDisplay().current_h / def_y)

    def supersample_sprite(self, tile_sprite):
        # Render the tile at a higher resolution
        larger_size = (int(tile_sprite.get_width() * self.super_sample), int(tile_sprite.get_height() * self.super_sample))
        larger_surface = pygame.transform.scale(tile_sprite, larger_size)

        # Downscale the tile to the original size with smooth scaling
        return pygame.transform.smoothscale(larger_surface, (tile_sprite.get_width(), tile_sprite.get_height()))

class text_sprite:
    curr_font = None
    curr_text_surface = None

    def __init__(self, system_font, font_size, string: str, antialias: bool, color, graphicHandler: Graphics):
        self.curr_font = pygame.font.SysFont(system_font, font_size, True)
        self.curr_text_surface = self.curr_font.render(string, antialias, color)
        self.graphicHandler = graphicHandler

    def draw_text(self, screen, position):
        scaleX, scaleY = self.graphicHandler.getWindowScale()
        self.curr_text_surface = pygame.transform.scale(self.curr_text_surface, (self.curr_text_surface.get_rect().width * scaleX, self.curr_text_surface.get_rect().height * scaleY))
        screen.blit(self.curr_text_surface, position)
