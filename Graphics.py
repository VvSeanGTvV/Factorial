import pygame
import time

from pygame import Vector2
from pygame.rect import RectType

class Window:
    def __init__(self, dx, dy, vx, vy, mode, target_fps, vsync):
        """Creates a Window Enviroment"""
        width, height = vx, vy # Set the Window Size
        self.defX, self.defY = dx, dy # Set renderable camera Size
        self.window = pygame.display # get the display
        self.currMode = mode
        self.target_fps = target_fps # Set the target FPS

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

    def get_display(self):
        return self.window.Info() # Get the window


class Handler:
    def __init__(self, window: Window, super_sample): # Initalize func (for class)
        self.curr_win = window
        self.clock = pygame.time.Clock()
        self.super_sample = super_sample

        self.last_fps_update_time = time.time()  # Track the last time FPS was updated
        self.fps_update_interval = 0.5  # Update FPS every 1 second
        self.current_fps = 0  # Store the current FPS value

        self.prev_time = time.time()

    def delta(self):
        """get Delta by time()"""
        now_time = time.time() # Get the Time
        delta = now_time - self.prev_time  # Calculate to get delta
        self.prev_time = now_time # set the previous time to the now time
        return delta # return delta

    def delta_target(self):
        return self.delta() * 60

    def getFPS(self):
        """Calculate and return the FPS, updating at a fixed interval."""
        current_time = time.time()
        time_since_last_update = current_time - self.last_fps_update_time

        # Update FPS only if the interval has passed
        if time_since_last_update >= self.fps_update_interval:
            self.current_fps = 1 / self.delta()  # Recalculate FPS
            self.last_fps_update_time = current_time  # Reset the timer

        return self.current_fps

    def getWindowSize(self):
        return self.curr_win.defX, self.curr_win.defY

    def getActiveDisplaySize(self):
        return self.curr_win.get_display().current_w, self.curr_win.get_display().current_h

    def getWindowScale(self):
        def_x, def_y = self.getWindowSize()
        return (self.curr_win.get_display().current_w / def_x), (self.curr_win.get_display().current_h / def_y)

    def supersample_sprite(self, tile_sprite):
        # Render the tile at a higher resolution
        larger_size = (
        int(tile_sprite.get_width() * self.super_sample), int(tile_sprite.get_height() * self.super_sample))
        larger_surface = pygame.transform.scale(tile_sprite, larger_size)

        # Downscale the tile to the original size with smooth scaling
        return pygame.transform.smoothscale(larger_surface, (tile_sprite.get_width(), tile_sprite.get_height()))


class TextSprite:

    def __init__(self, font, font_size: int, string: str, antialias: bool, color, graphic_handler: Handler):
        """Creates a text sprite"""
        self.text_settings = { # SAVE THE SETTING (used for updating the string), etc.
            "size": font_size,
            "antialias": antialias,
            "color": color,
            "font": "assets/fonts/" + font,
            "text": string
        }

        self.curr_font = pygame.font.Font("assets/fonts/" + font, font_size)
        self.curr_text_surface = self.curr_font.render(string, antialias, color)
        self.graphic_handler = graphic_handler

    def update_text(self, string: str):
        self.curr_font = pygame.font.Font(self.text_settings["font"], self.text_settings["size"])
        self.curr_text_surface = self.curr_font.render(string, self.text_settings["antialias"], self.text_settings["color"])

    def update_self(self):
        self.update_text(self.text_settings["text"])

    def update_size(self, font_size: int):
        self.text_settings["size"] = font_size
        self.update_self()

    def draw_text_rect(self, screen, position, rect: Vector2):
        scaleX, scaleY = self.graphic_handler.getWindowScale()
        text_surface = pygame.transform.scale(self.curr_text_surface, (
            rect.x * scaleX, rect.y * scaleY))
        screen.blit(text_surface, position)

    def draw_text(self, screen, position: Vector2):
        scaleX, scaleY = self.graphic_handler.getWindowScale()
        text_surface = pygame.transform.scale(self.curr_text_surface, (
        self.curr_text_surface.get_rect().width * scaleX, self.curr_text_surface.get_rect().height * scaleY))
        screen.blit(text_surface, (position.x * scaleX, position.y * scaleY))

    def get_text_rect(self):
        return self.curr_text_surface.get_rect()

    def draw_text_center(self, screen, position: Vector2):
        scaleX, scaleY = self.graphic_handler.getWindowScale()
        text_surface = pygame.transform.scale(self.curr_text_surface, (
            self.curr_text_surface.get_rect().width * scaleX, self.curr_text_surface.get_rect().height * scaleY))
        screen.blit(text_surface, ((position.x * scaleX) / text_surface.get_rect().width, (position.y * scaleY) / text_surface.get_rect().height))
