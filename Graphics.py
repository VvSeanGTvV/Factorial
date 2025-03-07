import pygame
import time


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

    def get_display(self):
        return self.window.Info()


class Graphics:

    def __init__(self, window: Window, super_sample):
        self.curr_win = window
        self.clock = pygame.time.Clock()
        self.super_sample = super_sample

        self.last_fps_update_time = time.time()  # Track the last time FPS was updated
        self.fps_update_interval = 0.5  # Update FPS every 1 second
        self.current_fps = 0  # Store the current FPS value

    # DELTA SYSTEM
    def delta(self):
        # Calculate delta time
        pygame.time.Clock()
        delta_time = self.clock.tick(self.curr_win.lockFPS) / 1000  # Convert milliseconds to seconds
        delta_time = min(delta_time, 0.1)
        return delta_time

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

    def __init__(self, system_font, font_size, string: str, antialias: bool, color, graphic_handler: Graphics):
        self.curr_font = pygame.font.SysFont(system_font, font_size, True)
        self.curr_text_surface = self.curr_font.render(string, antialias, color)
        self.graphic_handler = graphic_handler

    def draw_text(self, screen, position):
        scaleX, scaleY = self.graphic_handler.getWindowScale()
        self.curr_text_surface = pygame.transform.scale(self.curr_text_surface, (
        self.curr_text_surface.get_rect().width * scaleX, self.curr_text_surface.get_rect().height * scaleY))
        screen.blit(self.curr_text_surface, position)
