import math
import random

import pygame
from pygame import Surface, Vector2

import Graphics


class Player:
    worldx = 0
    worldy = 0

    def __init__(self, x, y, sprite: Surface, size, grahpicHandler: Graphics):
        self.x = x
        self.y = y
        self.sprite = sprite
        self.grahpicHandler = grahpicHandler
        self.size = size

    def updatePosition(self, x, y):
        self.x = x
        self.y = y

    def updatePositionWorld(self, x, y):
        self.worldx = x
        self.worldy = y

    def getPosition(self):
        return self.worldx, self.worldy

    def render(self, screen, camX, camY, velocity: Vector2):
        self.sprite = pygame.transform.scale(self.sprite, (
            int(self.size * (self.grahpicHandler.currWin.getDisplay().current_w / self.grahpicHandler.currWin.defX)),
            int(self.size * (self.grahpicHandler.currWin.getDisplay().current_h / self.grahpicHandler.currWin.defY))))

        ss_sprite = self.grahpicHandler.supersample_tile(self.sprite, 2)  # Supersample at 2x resolution
        if velocity.x != 0 or velocity.y != 0:
            angle = math.degrees(math.atan2(-velocity.y, velocity.x)) + 90
            rotated_sprite = pygame.transform.rotate(ss_sprite, angle)
        else:
            rotated_sprite = ss_sprite

        screen.blit(rotated_sprite, (
            self.x - camX - (rotated_sprite.get_rect().width // 2),
            self.y - camY - (rotated_sprite.get_rect().height // 2)
        ))


class Map:
    def __init__(self, Window, Seed, grahpicHandler):
        """Creates a Map"""
        self.grahpicHandler = grahpicHandler
        self.currWin = Window
        self.seed = Seed

    def preloadTiles(self, tile_set):
        """Preloads tile images and stores them in a 1D list."""
        return [pygame.image.load("assets/" + tile) for tile in tile_set]

    def getTile(self, x, y, tile_set):
        """Deterministically selects a tile based on coordinates using a seed."""
        random.seed(x * self.seed + y)  # Unique seed for each (x, y)
        return random.choice(tile_set)

    def render(self, tile_set, camX, camY):
        # Define the base resolution (logical resolution)
        base_width = self.currWin.defX
        base_height = self.currWin.defY
        scale_factor = 1

        # Calculate the scaled resolution
        scaled_width = int(base_width * scale_factor)
        scaled_height = int(base_height * scale_factor)

        # Create a surface for rendering at the scaled resolution
        if not hasattr(self, 'scaled_surface'):
            self.scaled_surface = pygame.Surface((scaled_width, scaled_height))

        # Precompute tile size and screen dimensions for the scaled resolution
        tile_size = int(16 * scale_factor)  # Scale the tile size
        screen_width = scaled_width
        screen_height = scaled_height

        # Calculate the visible area of the camera in world coordinates
        camera_left = -camX
        camera_top = -camY
        camera_right = -camX + base_width  # Use base width for camera calculations
        camera_bottom = -camY + base_height  # Use base height for camera calculations

        # Calculate the range of tiles that are visible within the camera's view
        start_tile_x = int(camera_left // tile_size)  # Starting tile X index
        start_tile_y = int(camera_top // tile_size)   # Starting tile Y index
        end_tile_x = int(camera_right // tile_size) + 1  # Ending tile X index
        end_tile_y = int(camera_bottom // tile_size) + 1  # Ending tile Y index

        # Precompute camera offsets for smooth scrolling
        camX_offset = -camX % tile_size  # Fractional offset within a tile
        camY_offset = -camY % tile_size  # Fractional offset within a tile

        # Cache scaled tiles to avoid redundant transformations
        tile_cache = {}

        # List to store tiles and their positions for batch rendering
        batch_tiles = []

        # Collect visible tiles for batch rendering
        for y in range(start_tile_y, end_tile_y):
            for x in range(start_tile_x, end_tile_x):
                # Generate or retrieve the tile using the seed-based system
                tile_sprite = self.getTile(x, y, tile_set)  # Assuming getTile uses x, y and seed
                tile_sprite = self.grahpicHandler.supersample_tile(tile_sprite, 2)  # Supersample at 2x resolution

                # Scale the tile if it's not already cached
                if (x, y) not in tile_cache:
                    tile_sprite = pygame.transform.scale(tile_sprite, (tile_size, tile_size))
                    tile_cache[(x, y)] = tile_sprite
                else:
                    tile_sprite = tile_cache[(x, y)]

                # Calculate the position of the tile on the screen
                render_x = (x - start_tile_x) * tile_size - camX_offset
                render_y = (y - start_tile_y) * tile_size - camY_offset

                # Add the tile and its position to the batch list
                if (
                        render_x + tile_size > 0 and render_x < screen_width and
                        render_y + tile_size > 0 and render_y < screen_height
                ):
                    batch_tiles.append((tile_sprite, (render_x, render_y)))

        # Clear the scaled surface
        self.scaled_surface.fill((0, 0, 0))  # Fill with background color

        # Render all tiles in the batch to the scaled surface
        self.scaled_surface.blits(batch_tiles)

        # Upscale the scaled surface to the display resolution
        scaled_to_display = pygame.transform.scale(self.scaled_surface, (self.currWin.getDisplay().current_w, self.currWin.getDisplay().current_h))

        # Render the upscaled surface to the display
        self.currWin.display.blit(scaled_to_display, (0, 0))

class Camera:
    def __init__(self, x, y):
        self.pos = Vector2(x, y)

    def getWorldPosition(self, tileSize):
        return Vector2(self.pos.x // tileSize, self.pos.y // tileSize)

    def updatePosition(self, x, y):
        self.pos = Vector2(x, y)
