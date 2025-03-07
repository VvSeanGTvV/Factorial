import math

import numpy as np
import opensimplex
import pygame
from pygame import Surface, Vector2

import Graphics


class Player:
    worldx = 0
    worldy = 0

    def __init__(self, x, y, sprite: Surface, size, graphic_handler: Graphics):
        self.x = x
        self.y = y
        self.sprite = sprite
        self.graphic_handler = graphic_handler
        self.size = size

    def update_position(self, x, y):
        self.x = x
        self.y = y

    def update_position_world(self, x, y):
        self.worldx = x
        self.worldy = y

        windowSX, windowSY = self.graphic_handler.getActiveDisplaySize()
        self.update_position(self.worldx + (windowSX // 2), self.worldy + (windowSY // 2))

    def get_position(self):
        return self.worldx, self.worldy

    def render(self, screen, camX, camY, velocity: Vector2):
        self.sprite = pygame.transform.scale(self.sprite, (
            int(self.size * (self.graphic_handler.curr_win.get_display().current_w / self.graphic_handler.curr_win.defX)),
            int(self.size * (self.graphic_handler.curr_win.get_display().current_h / self.graphic_handler.curr_win.defY))))

        ss_sprite = self.graphic_handler.supersample_sprite(self.sprite)
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
    def __init__(self, window, seed, graphic_handler):
        """Creates a Map"""
        self.graphic_handler = graphic_handler
        self.curr_win = window
        self.seed = seed  # Store the seed for deterministic generation
        self.noise_generator = opensimplex.OpenSimplex(seed)  # Initialize Simplex noise generator

    def preload_tiles(self, tile_set):
        """Preloads tile images and stores them in a 1D list."""
        return [pygame.image.load("assets/" + tile) for tile in tile_set]

    def get_tile(self, x, y, tile_set):
        """
        Selects a tile based on Simplex noise values.
        Noise values are mapped to the entire tile_set.
        """
        # Generate a noise value for the (x, y) coordinate
        noise_scale = 0.05  # Adjust this to control the "zoom" of the noise
        noise_value = self.noise_generator.noise2(x * noise_scale, y * noise_scale)

        # Normalize the noise value to the range [0, 1]
        normalized_noise = (noise_value + 1) / 2  # Convert [-1, 1] to [0, 1]

        # Map the normalized noise value to a tile index
        tile_index = int(normalized_noise * len(tile_set))  # Scale to tile_set length
        tile_index = max(0, min(tile_index, len(tile_set) - 1))  # Clamp to valid range

        return tile_set[tile_index]  # Return the selected tile

    def render(self, tile_set, camX, camY, scale_factor):
        # Define the base resolution (logical resolution)
        base_width = self.curr_win.defX
        base_height = self.curr_win.defY

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
                tile_sprite = self.get_tile(x, y, tile_set)  # Assuming getTile uses x, y and seed
                tile_sprite = self.graphic_handler.supersample_sprite(tile_sprite)

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
        scaled_to_display = pygame.transform.scale(self.scaled_surface, (self.curr_win.get_display().current_w, self.curr_win.get_display().current_h))

        # Render the upscaled surface to the display
        self.curr_win.display.blit(scaled_to_display, (0, 0))

class Camera:
    def __init__(self, x, y):
        self.pos = Vector2(x, y)

    def get_world_position(self, tileSize):
        return Vector2(self.pos.x // tileSize, self.pos.y // tileSize)

    def update_position(self, x, y):
        self.pos = Vector2(x, y)
