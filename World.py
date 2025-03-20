import math
import time

import opensimplex
import pygame
from pygame import Surface, Vector2

import World
from Graphics import Handler

Blocks = []


class Block:
    worldx = 0
    worldy = 0

    grid_x = 0
    grid_y = 0

    pos = Vector2(0, 0)

    def __init__(self, size, sprite: Surface, build_time, graphic_handler: Handler, outline_color=(255, 255, 0),
                 outline_thickness=1, stripe_width=17, stripe_speed=1):
        self.size = size * 16
        self.block_size = size
        self.sprite = sprite
        self.graphic_handler = graphic_handler
        self.build_time = 60 * build_time  # Total time required to build the block

        self.build_progress = 0  # Current progress in building the block
        self.is_built = False  # Whether the block is fully built
        self.build_playing = False  # Whether is the build_sound is still playing
        self.placing = True
        self.selected = False

        self.who = None  # who built the block

        # Load sound effects
        self.place_sound = pygame.mixer.Sound("assets/sounds/place.ogg")
        self.break_sound = pygame.mixer.Sound("assets/sounds/break.ogg")
        self.build_sound = pygame.mixer.Sound("assets/sounds/build.ogg")
        self.build_sound.set_volume(0.25)

        self.hitboxes = []

        # Scale the sprite based on the current window size
        self.sprite = pygame.transform.scale(self.sprite, (
            int(self.size * (
                    self.graphic_handler.curr_win.get_display().current_w / self.graphic_handler.curr_win.defX)),
            int(self.size * (
                    self.graphic_handler.curr_win.get_display().current_h / self.graphic_handler.curr_win.defY))))

        # Warning strip configuration
        self.stripe_width = stripe_width  # Width of each stripe
        self.stripe_speed = stripe_speed  # Speed of the animation (pixels per second)
        self.stripes_texture = self.create_diagonal_stripes_texture()

        self.mask_surface = pygame.Surface(self.sprite.get_size(), pygame.SRCALPHA)
        self.mask_surface.fill((0, 0, 0, 0))  # Transparent surface

        # Precompute the outline surface
        # Outline configuration
        self.outline_color = outline_color  # Yellow by default
        self.outline_thickness = outline_thickness  # Thickness of the outline
        self.outline_surface = self.precompute_outline()

        # Animation properties
        self.animation_offset = 0  # Tracks the diagonal offset of the stripes

    def create_diagonal_stripes_texture(self):
        """
        Create a texture with diagonal alternating yellow and transparent stripes.
        """
        # Create a surface for the stripes texture
        texture_size = max(self.sprite.get_width(),
                           self.sprite.get_height()) * 2  # Large enough to cover diagonal movement
        stripes_texture = pygame.Surface((texture_size, texture_size), pygame.SRCALPHA)
        stripes_texture.fill((0, 0, 0, 0))  # Transparent surface

        # Draw diagonal yellow stripes
        stripe_angle = 45  # Angle of the stripes (45 degrees for diagonal)
        stripe_spacing = self.stripe_width * 2  # Space between stripes
        for i in range(-texture_size, texture_size * 2, stripe_spacing):
            # Calculate the start and end points of the stripe
            start_x = i
            start_y = 0
            end_x = i + texture_size * math.tan(math.radians(stripe_angle))
            end_y = texture_size

            # Draw the stripe
            pygame.draw.line(stripes_texture, (255, 255, 0), (start_x, start_y), (end_x, end_y), self.stripe_width)

        return stripes_texture

    def is_within_hitbox(self, Build):
        """
        Check if the current block overlaps with another block's hitboxes.

        via by RECTTYPE
        """
        if not isinstance(Build, Block):
            return False  # Not a Block, no overlap

        # Iterate through all hitboxes of the current block
        for self_hitbox in self.hitboxes:
            self_pos, self_size = self_hitbox
            self_rect = pygame.Rect(self_pos.x, self_pos.y, self_size[0], self_size[1])

            # Iterate through all hitboxes of the other block
            for build_hitbox in Build.hitboxes:
                build_pos, build_size = build_hitbox
                build_rect = pygame.Rect(build_pos.x, build_pos.y, build_size[0], build_size[1])

                # Check for intersection between the two rectangles
                if self_rect.colliderect(build_rect):
                    return True  # Overlap detected

        return False  # No overlap detected

    def check_placement(self):
        for Build in Blocks:
            if isinstance(Build, Block):
                if self.is_within_hitbox(Build):
                    return False
        return True

    def get_world_position(self):
        return Vector2(self.worldx, self.worldy)

    def auto_hitbox(self):
        """
        Automatically generate hitboxes for the object based on spiral coordinates.
        Ensures blocks cannot be built on top of it.
        """
        # Calculate the base tile size for X and Y axes independently
        base_tile_size_x = 16 * (
                self.graphic_handler.curr_win.get_display().current_w / self.graphic_handler.curr_win.defX)
        base_tile_size_y = 16 * (
                self.graphic_handler.curr_win.get_display().current_h / self.graphic_handler.curr_win.defY)

        self.hitboxes.append(
            (
                Vector2(self.worldx,
                        self.worldy),

                ((self.block_size * base_tile_size_x) - 2,
                 (self.block_size * base_tile_size_y) - 2)
            )
        )

    def place_action(self, player):
        if self.placing:
            self.placing = False
            self.auto_hitbox()

        if self.check_placement():
            Blocks.append(self)
            self.who = player

    def destroy_action(self):
        World.Blocks.remove(self)  # Remove the block from the list

        # Stop the sound effect
        self.build_playing = False
        self.build_sound.stop()

        self.break_sound.play()  # Play the place sound effect

    def generate_spiral_coordinates(self, n):
        """
        Generate spiral coordinates for a block of size n x n.
        """
        # Initialize the starting position and direction
        x, y = 0, 0
        dx, dy = 0, 1  # Start moving right

        # List to store the coordinates
        coordinates = []

        # Iterate through the spiral
        for _ in range(n * n):
            # Add the current position to the list
            coordinates.append(Vector2(x, y))

            # Calculate the next position
            next_x, next_y = x + dx, y + dy

            # Check if the next position is out of bounds or already visited
            if (abs(next_x) >= n // 2 + 1 or abs(next_y) >= n // 2 + 1 or (next_x, next_y) in coordinates):
                # Change direction: right -> down -> left -> up -> right ...
                dx, dy = dy, -dx

            # Update the current position
            x, y = x + dx, y + dy

        return coordinates

    def handle_mouse_click(self, mouse_pos, cam_pos):
        """
        Handle mouse clicks to interact with the block.
        :param mouse_pos: Tuple (x, y) of the mouse position in screen coordinates.
        :param cam_pos: Vector2 of the camera position.
        """
        # Calculate the scaled camera position
        camX = cam_pos.x * (self.graphic_handler.curr_win.get_display().current_w / self.graphic_handler.curr_win.defX)
        camY = cam_pos.y * (self.graphic_handler.curr_win.get_display().current_h / self.graphic_handler.curr_win.defY)

        # Calculate the base tile size for X and Y axes independently
        base_tile_size_x = 16 * (
                self.graphic_handler.curr_win.get_display().current_w / self.graphic_handler.curr_win.defX)
        base_tile_size_y = 16 * (
                self.graphic_handler.curr_win.get_display().current_h / self.graphic_handler.curr_win.defY)

        # Recalculate the block's screen position
        screen_x = self.worldx + camX
        screen_y = self.worldy + camY

        # Create a Rect for the block
        block_rect = pygame.Rect(
            screen_x,
            screen_y,
            self.block_size * base_tile_size_x,
            self.block_size * base_tile_size_y
        )

        # Check if the mouse click is within the block's Rect
        if block_rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0]:  # Left mouse button
                self.selected = not self.selected  # Toggle selection
                if self.selected:
                    print("Block selected!")
                else:
                    print("Block deselected!")  # TODO do something

            # Right-click: Destroy the block
            elif pygame.mouse.get_pressed()[2]:  # Right mouse button
                self.destroy_action()

    def update(self, dt, cam_pos):
        """
        Update the block's build progress.
        :param dt: Time elapsed since the last update (in seconds).
        """

        # Calculate the scaled camera position
        camX = cam_pos.x * (self.graphic_handler.curr_win.get_display().current_w / self.graphic_handler.curr_win.defX)
        camY = cam_pos.y * (self.graphic_handler.curr_win.get_display().current_h / self.graphic_handler.curr_win.defY)

        if not self.is_built:
            self.build_progress += dt  # Increase build progress by the elapsed time

            # Start playing the sound effect if it's not already playing
            if not self.build_playing:
                self.build_sound.play(-1)  # Loop indefinitely
                self.build_playing = True

            if self.build_progress >= self.build_time:
                self.who.angle_to = 0
                self.is_built = True  # Mark the block as fully built

                # Stop the sound effect
                self.build_playing = False
                self.build_sound.stop()

                self.place_sound.play()  # Play the place sound effect

        # Update the animation offset
        self.animation_offset += self.stripe_speed * dt
        self.animation_offset %= self.stripe_width * 2  # Wrap around to create a seamless loop

    def precompute_outline(self):
        """
        Precompute the outline of the sprite and save it to a surface.
        """
        # Create a surface for the outline
        outline_surface = pygame.Surface(self.sprite.get_size(), pygame.SRCALPHA)
        outline_surface.fill((0, 0, 0, 0))  # Transparent surface

        # Get the sprite's pixels as a 2D array of colors
        sprite_pixels = pygame.surfarray.array3d(self.sprite)
        sprite_width, sprite_height = self.sprite.get_size()

        # Create a visited mask to track processed pixels
        visited = [[False for _ in range(sprite_height)] for _ in range(sprite_width)]

        # Define directions for checking adjacent pixels
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        # Iterate through each pixel in the sprite
        for x in range(sprite_width):
            for y in range(sprite_height):
                if not visited[x][y]:  # If the pixel hasn't been processed
                    # Get the current pixel's color
                    current_color = tuple(sprite_pixels[x][y])

                    # Skip transparent pixels (assuming transparency is black or (0, 0, 0))
                    if current_color == (0, 0, 0):
                        continue

                    # Perform flood-fill to find all adjacent pixels of the same color
                    region = []
                    stack = [(x, y)]
                    while stack:
                        cx, cy = stack.pop()
                        if not visited[cx][cy]:
                            visited[cx][cy] = True
                            region.append((cx, cy))

                            # Check adjacent pixels
                            for dx, dy in directions:
                                adj_x = cx + dx
                                adj_y = cy + dy
                                if 0 <= adj_x < sprite_width and 0 <= adj_y < sprite_height:
                                    if tuple(sprite_pixels[adj_x][adj_y]) == current_color:
                                        stack.append((adj_x, adj_y))

                    # Draw an outline around the region with the configured color and thickness
                    for px, py in region:
                        for dx, dy in directions:
                            adj_x = px + dx
                            adj_y = py + dy
                            if 0 <= adj_x < sprite_width and 0 <= adj_y < sprite_height:
                                if tuple(sprite_pixels[adj_x][adj_y]) != current_color:
                                    # Draw the outline with the configured thickness
                                    for i in range(self.outline_thickness):
                                        pygame.draw.rect(outline_surface, self.outline_color,
                                                         (px - i, py - i, 1 + 2 * i, 1 + 2 * i), 1)
                            else:
                                # Draw the outline with the configured thickness
                                for i in range(self.outline_thickness):
                                    pygame.draw.rect(outline_surface, self.outline_color,
                                                     (px - i, py - i, 1 + 2 * i, 1 + 2 * i), 1)

        return outline_surface

    def render_diagonal_warning_stripes(self, screen, camX, camY):
        """
        Render the moving diagonal warning stripes, masked onto the outline.
        """
        # Create a surface for the stripes
        stripes_surface = pygame.Surface(self.sprite.get_size(), pygame.SRCALPHA)
        stripes_surface.fill((0, 0, 0, 0))  # Transparent surface

        # Calculate the diagonal offset for the animation
        offset = int(self.animation_offset)

        # Draw the stripes texture repeatedly to cover the entire surface
        for i in range(-offset, self.sprite.get_width() + self.sprite.get_height(), self.stripe_width * 2):
            # Calculate the position of the stripe
            stripe_x = i
            stripe_y = 0

            # Draw the stripe
            stripes_surface.blit(self.stripes_texture, (stripe_x, stripe_y), special_flags=pygame.BLEND_RGBA_ADD)

        # Apply the outline as a mask to the stripes
        masked_stripes = pygame.Surface(self.sprite.get_size(), pygame.SRCALPHA)
        masked_stripes.fill((0, 0, 0, 0))  # Transparent surface
        masked_stripes.blit(self.outline_surface, (0, 0))  # Draw the outline
        masked_stripes.blit(stripes_surface, (0, 0),
                            special_flags=pygame.BLEND_RGBA_MIN)  # Clip the stripes to the outline

        # Render the masked stripes
        screen.blit(masked_stripes, ((self.worldx + camX),
                                     ((self.worldy + camY))))

    def render_diamond_outline(self, screen, camX, camY, diamond_points):
        """
        Render the diamond outline, clipped to the sprite's bounds.
        """
        # Create a surface for the outline
        outline_surface = pygame.Surface(self.sprite.get_size(), pygame.SRCALPHA)
        outline_surface.fill((0, 0, 0, 0))  # Transparent surface

        # Draw the diamond outline on the outline surface
        pygame.draw.polygon(outline_surface, (255, 255, 0), diamond_points, 3)  # Yellow outline

        # Create a mask from the sprite's alpha channel
        mask = pygame.mask.from_surface(self.sprite)
        mask_surface = mask.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))

        # Apply the mask to the outline surface
        clipped_outline = pygame.Surface(self.sprite.get_size(), pygame.SRCALPHA)
        clipped_outline.fill((0, 0, 0, 0))  # Transparent surface
        clipped_outline.blit(outline_surface, (0, 0))
        clipped_outline.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Render the clipped outline
        screen.blit(clipped_outline, (self.worldx + camX, self.worldy + camY))

    def render(self, screen, cam_pos: Vector2, scale_factor=1):
        # Calculate the scaled camera position
        camX = cam_pos.x * (self.graphic_handler.curr_win.get_display().current_w / self.graphic_handler.curr_win.defX)
        camY = cam_pos.y * (self.graphic_handler.curr_win.get_display().current_h / self.graphic_handler.curr_win.defY)

        # Calculate the base tile size for X and Y axes independently
        base_tile_size_x = 16 * (
                self.graphic_handler.curr_win.get_display().current_w / self.graphic_handler.curr_win.defX)
        base_tile_size_y = 16 * (
                self.graphic_handler.curr_win.get_display().current_h / self.graphic_handler.curr_win.defY)

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
            if not self.is_built:
                # Calculate the progress ratio (0 to 1)
                progress_ratio = self.build_progress / self.build_time

                # Clear the mask surface
                self.mask_surface.fill((0, 0, 0, 0))

                # Draw the diamond shape on the mask surface
                diamond_size = int((1 - progress_ratio) * self.sprite.get_width())
                diamond_points = [
                    (self.sprite.get_width() // 2, self.sprite.get_height() // 2 - diamond_size),  # Top
                    (self.sprite.get_width() // 2 + diamond_size, self.sprite.get_height() // 2),  # Right
                    (self.sprite.get_width() // 2, self.sprite.get_height() // 2 + diamond_size),  # Bottom
                    (self.sprite.get_width() // 2 - diamond_size, self.sprite.get_height() // 2)  # Left
                ]
                pygame.draw.polygon(self.mask_surface, (255, 255, 255, 255), diamond_points)  # White diamond

                # Create an inverted mask surface
                inverted_mask = pygame.Surface(self.sprite.get_size(), pygame.SRCALPHA)
                inverted_mask.fill((255, 255, 255, 255))  # Fully opaque
                inverted_mask.blit(self.mask_surface, (0, 0),
                                   special_flags=pygame.BLEND_RGBA_SUB)  # Subtract the diamond

                # Create a copy of the sprite
                masked_sprite = self.sprite.copy()

                # Apply the inverted mask to the sprite
                masked_sprite.blit(inverted_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                # Render the masked sprite
                screen.blit(masked_sprite, ((self.worldx + camX),
                                            ((self.worldy + camY))))
                # Draw the diamond outline directly on the screen
                screen_diamond_points = [
                    (self.worldx + camX + self.sprite.get_width() // 2,
                     self.worldy + camY + self.sprite.get_height() // 2 - diamond_size),  # Top
                    (self.worldx + camX + self.sprite.get_width() // 2 + diamond_size,
                     self.worldy + camY + self.sprite.get_height() // 2),  # Right
                    (self.worldx + camX + self.sprite.get_width() // 2,
                     self.worldy + camY + self.sprite.get_height() // 2 + diamond_size),  # Bottom
                    (self.worldx + camX + self.sprite.get_width() // 2 - diamond_size,
                     self.worldy + camY + self.sprite.get_height() // 2)  # Left
                ]
                # Render the diamond outline, clipped to the sprite's bounds
                self.render_diamond_outline(screen, camX, camY, diamond_points)

                # Render the moving diagonal warning stripes, masked onto the outline
                self.render_diagonal_warning_stripes(screen, camX, camY)
            else:
                # Render the fully built sprite
                screen.blit(self.sprite, ((self.worldx + camX),
                                          ((self.worldy + camY))))

            # Highlight the block if selected
            if self.selected:
                highlight_rect = pygame.Rect(
                    self.worldx + camX,
                    self.worldy + camY,
                    self.block_size * base_tile_size_x,
                    self.block_size * base_tile_size_y
                )
                pygame.draw.rect(screen, (255, 255, 0), highlight_rect, 3)  # Yellow border


class Player:
    worldx = 0
    worldy = 0

    def __init__(self, x, y, sprite: Surface, size, graphic_handler: Handler):
        self.worldx = x
        self.worldy = y
        self.sprite = sprite
        self.graphic_handler = graphic_handler
        self.size = size

        self.angle = 0
        self.angle_to = 0

        self.defpos = (Vector2(graphic_handler.getActiveDisplaySize()) / 2) - (
                    Vector2(graphic_handler.getWindowSize()) / 2)

    def update_position_world(self, x, y):
        self.worldx = x
        self.worldy = y

    def get_position(self):
        return self.worldx, self.worldy

    def face_towards(self, target: Vector2):
        """
        Force the player to face towards a specific target position or direction vector.
        :param target: A Vector2 representing the target position or direction.
        """
        # Calculate the direction vector from the player's position to the target
        scale = Vector2(self.graphic_handler.getWindowScale())
        direction = target - self.get_position()

        # Calculate the angle in radians and convert it to degrees
        angle_radians = math.atan2(-direction.y, direction.x)  # Negative y because pygame's y-axis is flipped
        self.angle_to = math.degrees(angle_radians) - 90  # Add 90 to align with sprite's default orientation

    def render(self, screen, camX, camY, velocity: Vector2):
        self.sprite = pygame.transform.scale(self.sprite, (
            int(self.size * (
                    self.graphic_handler.curr_win.get_display().current_w / self.graphic_handler.curr_win.defX)),
            int(self.size * (
                    self.graphic_handler.curr_win.get_display().current_h / self.graphic_handler.curr_win.defY))))

        ss_sprite = self.graphic_handler.supersample_sprite(self.sprite)

        if velocity.x != 0 or velocity.y != 0:
            self.angle = math.degrees(math.atan2(-velocity.y, velocity.x)) + 90
        else:
            rotated_sprite = ss_sprite
        if self.angle_to != 0:
            self.angle = self.angle_to

        rotated_sprite = pygame.transform.rotate(ss_sprite, self.angle)

        screen.blit(rotated_sprite, (
            self.worldx - camX - (rotated_sprite.get_rect().width // 2),
            self.worldy - camY - (rotated_sprite.get_rect().height // 2)
        ))

        self.cam_pos = Vector2(camX, camY)


class Tile:

    def preload_tiles(self, tile_set):
        """Preloads tile images and stores them in a 1D list."""
        return [pygame.image.load("assets/" + tile) for tile in tile_set]

    def __init__(self, sprite_list: list[str], item=None, animated=False):
        """
        Tile, a class that has item drop and variantions sprite.
        :param sprite_list: Creates a preloaded_tiles (more primarily in "assets/")
        :param animated: if this Tile is animated (uses sprite_list as animation)
        """

        self.sprite_list = self.preload_tiles(sprite_list)
        self.item = item
        self.has_drop = item is not None
        self.animation_frames = self.variants = len(self.sprite_list)

        # USED FOR ANIMATED TILE
        self.animated = animated
        self.current_frame = 0

    def get_sprite(self, variant):
        return self.sprite_list[variant % self.variants]




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
                "tile": Tile(["gold-sand1.png", "gold-sand2.png", "gold-sand3.png"]),
            },
            {
                "name": "mountain",
                "temperature_range": (0.0, 0.77),
                "humidity_range": (0.0, 0.2),
                "tile": Tile(["basalt1.png"]),
            },
            {
                "name": "grassland",
                "temperature_range": (0.33, 0.66),
                "humidity_range": (0.0, 0.5),
                "tile": Tile(["grass1.png", "grass2.png"]),
            },
            {
                "name": "ocean",
                "temperature_range": (0.33, 0.66),
                "humidity_range": (0.5, 1.0),
                "tile": Tile(["water1.png", "water2.png", "water3.png"], animated=True),
            }
        ]

        self.animated_tile_list = []
        for biome in self.biome_rules:
            biome_tile = biome["tile"]
            if biome_tile.animated:
                self.animated_tile_list.append({
                    "name": biome["name"],
                    "current_animation": 0,
                    "total_frame": biome_tile.animation_frames
                })

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
        biome_tile = biome["tile"]

        # If it's the ocean biome, return the current animation frame
        if biome_tile.animated:
            animated_tile = self.animated_tile_list[biome["name"]]
            return biome_tile.get_sprite(animated_tile["current_frame"])

        # For other biomes, use noise to select a tile
        noise_scale = 0.05  # Adjust this to control the "zoom" of the noise
        noise_value = self.noise_generator.noise2(x * noise_scale, y * noise_scale)

        # Normalize the noise value to the range [0, 1]
        normalized_noise = (noise_value + 1) / 2  # Convert [-1, 1] to [0, 1]

        # Map the normalized noise value to a tile index
        tile_index = int(normalized_noise * biome_tile.variants)  # Scale to biome_tiles length
        tile_index = max(0, min(tile_index, biome_tile.variants - 1))  # Clamp to valid range

        return biome_tile.get_sprite(tile_index) # Return the selected tile

    def update_animation(self):
        """Updates the animation frame for water tiles."""
        self.animation_timer = self.animation_timer + self.graphic_handler.delta_target()
        for chunk_coords in self.loaded_chunks:
            chunk_tiles = self.loaded_chunks[chunk_coords]
            for tile_data in chunk_tiles:
                if len(tile_data["frames"]) > 1:  # Check if the tile is animated
                    # Update the animation frame if enough time has passed
                    current_frame = int(self.animation_timer * 1) % len(tile_data["frames"])
                    tile_data["current_frame"] = current_frame
                    tile_data["last_update"] = self.animation_timer

    def load_chunk(self, chunk_x, chunk_y, tile_size):
        """Loads a chunk of tiles and caches them."""
        chunk_tiles = []
        for y in range(chunk_y * self.chunk_size, (chunk_y + 1) * self.chunk_size):
            for x in range(chunk_x * self.chunk_size, (chunk_x + 1) * self.chunk_size):
                # Get the biome for the current tile
                biome = self.get_biome(x, y)
                biome_tile = biome["tile"]

                # If the tile is animated, preload all animation frames and initialize animation state
                if biome_tile.animated:
                    tile_frames = []
                    for frame in biome_tile.sprite_list:
                        tile_sprite = pygame.transform.scale(frame, (tile_size, tile_size))
                        tile_sprite = self.graphic_handler.supersample_sprite(tile_sprite)
                        tile_frames.append(tile_sprite)
                    # Store the frames and the current animation state for this tile
                    chunk_tiles.append({
                        "frames": tile_frames,
                        "current_frame": 0,  # Initialize animation state
                        "last_update": self.animation_timer
                    })
                else:
                    # For non-animated tiles, preload a single frame
                    tile_sprite = self.get_tile(x, y)
                    tile_sprite = pygame.transform.scale(tile_sprite, (tile_size, tile_size))
                    tile_sprite = self.graphic_handler.supersample_sprite(tile_sprite)
                    chunk_tiles.append({
                        "frames": [tile_sprite],  # Store as a list for consistency
                        "current_frame": 0,  # Non-animated tiles only have one frame
                        "last_update": None  # No animation state needed
                    })

        self.loaded_chunks[(chunk_x, chunk_y)] = chunk_tiles

    def unload_chunk(self, chunk_x, chunk_y):
        """Unloads a chunk of tiles to free up memory."""
        if (chunk_x, chunk_y) in self.loaded_chunks:
            del self.loaded_chunks[(chunk_x, chunk_y)]

    def render(self, camX, camY, scale_factor=1):
        # Update the animation frame for all animated tiles


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
                        tile_data = self.loaded_chunks[chunk_coords][tile_index]

                        # Use the tile's current animation frame
                        tile_sprite = tile_data["frames"][tile_data["current_frame"]]
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
