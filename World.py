import math
import time

import opensimplex
import pygame
from pygame import Surface, Vector2
from Graphics import Handler

Blocks = []


class Block:
    worldx = 0
    worldy = 0

    grid_x = 0
    grid_y = 0

    placing = True
    def __init__(self, size, sprite: Surface, graphic_handler: Handler):
        self.size = size * 16
        self.block_size = size
        self.sprite = sprite
        self.graphic_handler = graphic_handler

        # Load sound effects
        self.place_sound = pygame.mixer.Sound("assets/sounds/place.ogg")  # Replace with your sound file

        self.hitboxes = []

    def is_within_hitbox(self, Build):
        """
        Check if the current block overlaps with another block's hitboxes.
        """
        if not isinstance(Build, Block):
            return False  # Not a Block, no overlap

        # Use set for faster lookups
        self_hitbox_set = {(h.x, h.y) for h in self.hitboxes if isinstance(h, Vector2)}
        build_hitbox_set = {(h.x, h.y) for h in Build.hitboxes if isinstance(h, Vector2)}

        # Check for intersection
        return not self_hitbox_set.isdisjoint(build_hitbox_set)

    def check_placement(self):
        for Build in Blocks:
            if isinstance(Build, Block):
                if self.is_within_hitbox(Build):
                    return False
        return True

    def get_world_position(self):
        return Vector2(self.worldx, self.worldy)

    def auto_hitbox(self):
        coordinates = self.generate_spiral_coordinates(self.block_size)
        # self.hitboxes.append(Vector2(self.worldx, self.worldy))
        for coord in coordinates:
            tile_x, tile_y = (coord * (self.graphic_handler.curr_win.get_display().current_w / self.graphic_handler.curr_win.defX)) * 16
            self.hitboxes.append(Vector2(math.floor(self.worldx + tile_x), math.floor(self.worldy + tile_y)))

    def place_action(self):
        if self.placing:
            self.placing = False
            self.auto_hitbox()

        if self.check_placement():
            Blocks.append(self)
            self.place_sound.play()  # Play the place sound effect

    def generate_spiral_coordinates(self, n):
        # Initialize the starting position and direction
        x, y = 0, 0
        dx, dy = 0, 1  # Start moving right

        # List to store the coordinates
        coordinates = []

        # Iterate through the spiral
        for _ in range(n * n):
            coordinates.append(Vector2(x, y))  # Add the current position to the list

            # Calculate the next position
            next_x, next_y = x + dx, y + dy

            # Check if the next position is out of bounds or already visited
            if (abs(next_x) > n // 2 or abs(next_y) > n // 2 or (next_x, next_y) in coordinates):
                # Change direction: right -> down -> left -> up -> right ...
                dx, dy = dy, -dx

            # Update the current position
            x, y = x + dx, y + dy

        return coordinates

    def render(self, screen, cam_pos: Vector2, scale_factor=1):
        # Calculate the scaled camera position
        camX = cam_pos.x * (self.graphic_handler.curr_win.get_display().current_w / self.graphic_handler.curr_win.defX)
        camY = cam_pos.y * (self.graphic_handler.curr_win.get_display().current_h / self.graphic_handler.curr_win.defY)

        # Calculate the base tile size for X and Y axes independently
        base_tile_size_x = 16 * (self.graphic_handler.curr_win.get_display().current_w / self.graphic_handler.curr_win.defX)
        base_tile_size_y = 16 * (self.graphic_handler.curr_win.get_display().current_h / self.graphic_handler.curr_win.defY)

        # Scale the sprite based on the current window size
        self.sprite = pygame.transform.scale(self.sprite, (
            int(self.size * (self.graphic_handler.curr_win.get_display().current_w / self.graphic_handler.curr_win.defX)),
            int(self.size * (self.graphic_handler.curr_win.get_display().current_h / self.graphic_handler.curr_win.defY))))

        # Supersample the sprite for better quality
        ss_sprite = self.graphic_handler.supersample_sprite(self.sprite)

        if self.placing:
            # Snapping logic for placing blocks
            mouse = pygame.mouse.get_pos()

            # Convert mouse position to world space
            world_mouse_x = (mouse[0] / scale_factor) - camX + ss_sprite.get_rect().width
            world_mouse_y = (mouse[1] / scale_factor) - camY + ss_sprite.get_rect().height

            # Snap to the grid in world space, using the scaled base_tile_size for X and Y
            snapped_world_x = (world_mouse_x // base_tile_size_x) * base_tile_size_x - ss_sprite.get_rect().width
            snapped_world_y = (world_mouse_y // base_tile_size_y) * base_tile_size_y - ss_sprite.get_rect().height

            # Store the snapped position in grid coordinates
            self.grid_x = snapped_world_x // base_tile_size_x
            self.grid_y = snapped_world_y // base_tile_size_y

            # Create a copy of the sprite for transparency and tinting
            placing_sprite = ss_sprite.copy()

            # Set transparency (alpha value)
            placing_sprite.set_alpha(128)  # 50% transparency (0 = fully transparent, 255 = fully opaque)

            # Tint the sprite with an aqua color (R=0, G=255, B=255)
            tint_color = (0, 255, 255)  # Aqua color
            placing_sprite.fill(tint_color, special_flags=pygame.BLEND_RGBA_MULT)  # Apply tint

            # Render the snapped sprite with transparency and tint
            screen.blit(placing_sprite, (snapped_world_x + camX, snapped_world_y + camY))
            self.worldx, self.worldy = snapped_world_x, snapped_world_y
        else:

            # Recalculate world position based on current resolution
            self.worldx = self.grid_x * base_tile_size_x
            self.worldy = self.grid_y * base_tile_size_y

            # Render the sprite at its current world position
            screen.blit(ss_sprite, ((self.worldx + camX),
                                    ((self.worldy + camY))
                                    ))


class Player:
    worldx = 0
    worldy = 0

    def __init__(self, x, y, sprite: Surface, size, graphic_handler: Handler):
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
            int(self.size * (
                    self.graphic_handler.curr_win.get_display().current_w / self.graphic_handler.curr_win.defX)),
            int(self.size * (
                    self.graphic_handler.curr_win.get_display().current_h / self.graphic_handler.curr_win.defY))))

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
    def __init__(self, window, seed, graphic_handler, chunk_size):
        """Creates a Map"""
        self.graphic_handler = graphic_handler
        self.curr_win = window
        self.seed = seed  # Store the seed for deterministic generation
        self.noise_generator = opensimplex.OpenSimplex(seed)  # Initialize Simplex noise generator
        self.tile_cache = {}  # Cache for scaled and supersampled tiles
        self.loaded_chunks = {}  # Dictionary to store loaded chunks
        self.chunk_size = chunk_size  # Size of each chunk (e.g., 16x16 tiles)
        self.animation_timer = 0

        # Noise generators for temperature and humidity
        self.temperature_noise = opensimplex.OpenSimplex(seed=seed + 1)
        self.humidity_noise = opensimplex.OpenSimplex(seed=seed + 2)

        self.blended_tiles = {}  # Cache for blended tiles

        # Biome definitions
        self.biome_rules = [
            {
                "name": "desert",
                "temperature_range": (0.0, 0.33),
                "humidity_range": (0.0, 0.5),
                "tiles": self.preload_tiles(["gold-sand1.png", "gold-sand2.png", "gold-sand3.png"]),
            },
            {
                "name": "mountain",
                "temperature_range": (0.0, 0.77),
                "humidity_range": (0.0, 0.2),
                "tiles": self.preload_tiles(["basalt1.png"]),
            },
            {
                "name": "grassland",
                "temperature_range": (0.33, 0.66),
                "humidity_range": (0.0, 0.5),
                "tiles": self.preload_tiles(["grass1.png", "grass2.png"]),
            },
            {
                "name": "ocean",
                "temperature_range": (0.33, 0.66),
                "humidity_range": (0.5, 1.0),
                "tiles": self.preload_tiles(["water1.png", "water2.png", "water3.png"]),
            }
        ]

        # Animation state
        self.water_animation_frames = self.get_biome_rules("ocean")["tiles"]  # Ocean biome tiles
        self.current_animation_frame = 0
        self.last_animation_update = time.time()
        self.animation_frame_duration = 0.2  # Time between frames in seconds

        # Minimap settings
        self.minimap_size = (200, 200)  # Size of the minimap (width, height)
        self.minimap_surface = pygame.Surface(self.minimap_size)  # Surface for the minimap

    def is_chunk_visible(self, chunk_x, chunk_y, camX, camY, base_tile_size=16):
        """
        Check if a chunk is visible within the camera's view.

        Args:
            chunk_x (int): The chunk's x-coordinate.
            chunk_y (int): The chunk's y-coordinate.
            camX (int): The camera's x-coordinate.
            camY (int): The camera's y-coordinate.

        Returns:
            bool: True if the chunk is visible, False otherwise.
        """
        # Calculate the visible chunk range based on the camera's position
        camera_left = -camX
        camera_top = -camY
        camera_right = -camX + self.curr_win.defX  # Use base width for camera calculations
        camera_bottom = -camY + self.curr_win.defY  # Use base height for camera calculations

        # Calculate the range of chunks visible to the camera's view
        start_chunk_x = int(camera_left // (self.chunk_size * base_tile_size))
        start_chunk_y = int(camera_top // (self.chunk_size * base_tile_size))
        end_chunk_x = int(camera_right // (self.chunk_size * base_tile_size)) + 1
        end_chunk_y = int(camera_bottom // (self.chunk_size * base_tile_size)) + 1

        # Check if the chunk is within the visible range
        return (start_chunk_x <= chunk_x < end_chunk_x and
                start_chunk_y <= chunk_y < end_chunk_y)

    def get_biome_rules(self, name: str):
        for biome in self.biome_rules:
            if biome["name"] == name:
                return biome
        return None

    def preload_tiles(self, tile_set):
        """Preloads tile images and stores them in a 1D list."""
        return [pygame.image.load("assets/" + tile) for tile in tile_set]

    def get_biome(self, x, y):
        """Determine the biome for a given (x, y) coordinate."""
        # Generate noise values for temperature and humidity
        temperature = self.temperature_noise.noise2(x * 0.01, y * 0.01)  # Scale for smoother transitions
        humidity = self.humidity_noise.noise2(x * 0.01, y * 0.01)  # Scale for smoother transitions

        # Normalize noise values to [0, 1]
        temperature = (temperature + 1) / 2
        humidity = (humidity + 1) / 2

        # Find the biome that matches the temperature and humidity
        for biome in self.biome_rules:
            temp_min, temp_max = biome["temperature_range"]
            hum_min, hum_max = biome["humidity_range"]
            if temp_min <= temperature <= temp_max and hum_min <= humidity <= hum_max:
                return biome

        # Default biome if no match is found
        return self.biome_rules[0]

    def get_tile(self, x, y):
        """Selects a tile based on biome and noise values."""
        # Get the biome for the current tile
        biome = self.get_biome(x, y)

        # Get the list of tiles for the biome
        biome_tiles = biome["tiles"]

        # If it's the ocean biome, return the current animation frame
        if biome["name"] == "ocean":
            return biome_tiles[self.current_animation_frame]

        # For other biomes, use noise to select a tile
        noise_scale = 0.05  # Adjust this to control the "zoom" of the noise
        noise_value = self.noise_generator.noise2(x * noise_scale, y * noise_scale)

        # Normalize the noise value to the range [0, 1]
        normalized_noise = (noise_value + 1) / 2  # Convert [-1, 1] to [0, 1]

        # Map the normalized noise value to a tile index
        tile_index = int(normalized_noise * len(biome_tiles))  # Scale to biome_tiles length
        tile_index = max(0, min(tile_index, len(biome_tiles) - 1))  # Clamp to valid range

        return biome_tiles[tile_index]  # Return the selected tile

    def update_animation(self):
        """Updates the animation frame for water tiles."""
        self.animation_timer = self.animation_timer + self.graphic_handler.delta_target()
        self.current_animation_frame = (math.floor(self.animation_timer * 2)) % len(self.water_animation_frames)

    def load_chunk(self, chunk_x, chunk_y, tile_size):
        """Loads a chunk of tiles and caches them."""
        chunk_tiles = []
        for y in range(chunk_y * self.chunk_size, (chunk_y + 1) * self.chunk_size):
            for x in range(chunk_x * self.chunk_size, (chunk_x + 1) * self.chunk_size):
                # Get the biome for the current tile
                biome = self.get_biome(x, y)

                # If it's the ocean biome, preload all animation frames
                if biome["name"] == "ocean":
                    tile_frames = []
                    for frame in biome["tiles"]:
                        tile_sprite = pygame.transform.scale(frame, (tile_size, tile_size))
                        tile_sprite = self.graphic_handler.supersample_sprite(tile_sprite)
                        tile_frames.append(tile_sprite)
                    chunk_tiles.append(tile_frames)
                else:
                    # For non-ocean tiles, preload a single frame
                    tile_sprite = self.get_tile(x, y)
                    tile_sprite = pygame.transform.scale(tile_sprite, (tile_size, tile_size))
                    tile_sprite = self.graphic_handler.supersample_sprite(tile_sprite)
                    chunk_tiles.append([tile_sprite])  # Store as a list for consistency

        self.loaded_chunks[(chunk_x, chunk_y)] = chunk_tiles

    def unload_chunk(self, chunk_x, chunk_y):
        """Unloads a chunk of tiles to free up memory."""
        if (chunk_x, chunk_y) in self.loaded_chunks:
            del self.loaded_chunks[(chunk_x, chunk_y)]

    def render(self, camX, camY, scale_factor=1):
        # Update the animation frame

        # Define the base resolution (logical resolution)
        base_width = self.curr_win.defX
        base_height = self.curr_win.defY

        # Calculate the scaled resolution
        scaled_width = int(base_width * scale_factor)
        scaled_height = int(base_height * scale_factor)

        # Create or reuse the scaled surface
        if not hasattr(self, 'scaled_surface'):
            self.scaled_surface = pygame.Surface((scaled_width, scaled_height))

        # Precompute tile size and screen dimensions for the scaled resolution
        base_tile_size = 16  # Base size of a tile in pixels
        tile_size = int(base_tile_size * scale_factor)  # Scale the tile size
        screen_width = scaled_width
        screen_height = scaled_height

        # Calculate the visible area of the camera in world coordinates
        camera_left = -camX
        camera_top = -camY
        camera_right = -camX + base_width  # Use base width for camera calculations
        camera_bottom = -camY + base_height  # Use base height for camera calculations

        # Calculate the range of chunks visible to camera's view
        start_chunk_x = int(camera_left // (self.chunk_size * base_tile_size))
        start_chunk_y = int(camera_top // (self.chunk_size * base_tile_size))
        end_chunk_x = int(camera_right // (self.chunk_size * base_tile_size)) + 1
        end_chunk_y = int(camera_bottom // (self.chunk_size * base_tile_size)) + 1

        # Load newly visible chunks and unload chunks that are no longer visible
        for chunk_x in range(start_chunk_x, end_chunk_x):
            for chunk_y in range(start_chunk_y, end_chunk_y):
                if (chunk_x, chunk_y) not in self.loaded_chunks:
                    self.load_chunk(chunk_x, chunk_y, tile_size)  # Load the new chunks that are not yet loaded

        chunks_to_unload = []  # List for chunks that are considered to be unloaded or not viewed to the camera.
        for chunk_coords in self.loaded_chunks:
            if not (start_chunk_x <= chunk_coords[0] < end_chunk_x and
                    start_chunk_y <= chunk_coords[1] < end_chunk_y):
                chunks_to_unload.append(chunk_coords)  # If not in visible range put to chunks to unload list
        for chunk_coords in chunks_to_unload:
            self.unload_chunk(*chunk_coords)  # If on list, unload the chunk make it not render to the camera.

        # List to store tiles and their positions for batch rendering
        batch_tiles = []  # Cache all tiles and their positions for batch rendering

        # Collect visible tiles for batch rendering
        for chunk_coords in self.loaded_chunks:
            chunk_x, chunk_y = chunk_coords
            for y in range(chunk_y * self.chunk_size, (chunk_y + 1) * self.chunk_size):
                for x in range(chunk_x * self.chunk_size, (chunk_x + 1) * self.chunk_size):
                    # Calculate the position of the tile on the screen
                    render_x = (x * tile_size - -camX) * scale_factor
                    render_y = (y * tile_size - -camY) * scale_factor

                    # Add the tile and its position to the batch list if the tile is within the camera's viewable area
                    if (
                            render_x + tile_size > 0 and render_x < screen_width and
                            render_y + tile_size > 0 and render_y < screen_height
                    ):
                        # Get the tile from the chunk
                        tile_index = (y - chunk_y * self.chunk_size) * self.chunk_size + (x - chunk_x * self.chunk_size)
                        tile_frames = self.loaded_chunks[chunk_coords][tile_index]

                        # For ocean tiles, use the current animation frame
                        if len(tile_frames) > 1:
                            tile_sprite = tile_frames[self.current_animation_frame]
                        else:
                            tile_sprite = tile_frames[0]

                        batch_tiles.append((tile_sprite, (render_x, render_y)))

        # Clear the scaled surface
        self.scaled_surface.fill((0, 0, 0))  # Fill with background color

        # Render all tiles in the batch to the scaled surface
        self.scaled_surface.blits(batch_tiles)

        # Upscale the scaled surface to the display resolution
        scaled_to_display = pygame.transform.scale(self.scaled_surface, (
            self.curr_win.get_display().current_w, self.curr_win.get_display().current_h))

        # Render the upscaled surface to the display
        self.curr_win.display.blit(scaled_to_display, (0, 0))


class Camera:
    def __init__(self, x, y):  # Creates a Camera
        self.pos = Vector2(x, y)

    def get_world_position(self, tileSize):  # Get the world position (divided by Tile Size)
        return Vector2(self.pos.x // tileSize, self.pos.y // tileSize)

    def update_position(self, x, y):  # Update a Camera's Position
        self.pos = Vector2(x, y)
