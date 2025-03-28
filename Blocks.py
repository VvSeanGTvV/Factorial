import math

import pygame
from pygame import Vector2

import Graphics
import World
from World import Block

# Item definitions (could also be in a config file)
ITEM_SPRITES = {
    "copper": pygame.image.load("assets/items/item-copper.png")
}

# Scale item sprites to appropriate size (e.g., 16x16)
for item_type, sprite in ITEM_SPRITES.items():
    ITEM_SPRITES[item_type] = pygame.transform.scale(sprite, (32, 32))


class Drill(Block):
    def __init__(self, size, sprite, build_time, graphic_handler, mining_power=0.01):
        super().__init__(size, sprite, build_time, graphic_handler)
        self.mining_power = mining_power
        self.output_direction = Vector2(1, 0)  # Default right
        self.buffer = []  # Stores mined items temporarily
        self.buffer_limit = 5  # Max items in buffer before stopping mining
        self.connected_tiles = []  # Adjacent mineable tiles
        self.adjacent_blocks = []  # Stores adjacent output blocks

    def update_connections(self, world_map, world_blocks):
        """Update connected tiles and output blocks accounting for drill size"""
        self.connected_tiles = []
        self.adjacent_blocks = []

        # Check all positions around the drill's perimeter
        for dx in range(-1, self.block_size + 1):
            for dy in range(-1, self.block_size + 1):
                # Skip positions inside the drill's area
                if 0 <= dx < self.block_size and 0 <= dy < self.block_size:
                    continue

                # Check for mineable tiles
                tile = world_map.get_tile_at_grid(self.grid_x + dx, self.grid_y + dy)
                if tile and tile.is_ore and tile.remaining_richness > 0:
                    self.connected_tiles.append(tile)

                # Check for adjacent output blocks
                for block in world_blocks:
                    if (block.grid_x == self.grid_x + dx and
                            block.grid_y == self.grid_y + dy and
                            isinstance(block, (Conveyor, Storage))):
                        self.adjacent_blocks.append(block)

    def mine_tick(self, dt):
        if len(self.buffer) >= self.buffer_limit:
            return

        for tile in self.connected_tiles:
            result = tile.mine(dt * self.mining_power)
            if result:
                item_type, amount = result
                self.buffer.append({
                    'type': item_type,
                    'amount': amount,
                    'world_pos': Vector2(self.worldx, self.worldy),
                    'sprite': ITEM_SPRITES.get(item_type),  # Store reference to sprite
                    'progress': 0  # For conveyor movement
                })

    def transfer_items(self):
        """Transfer items to adjacent outputs"""
        if not self.buffer or not self.adjacent_blocks:
            return

        item = self.buffer[0]  # Get oldest item

        for block in self.adjacent_blocks:
            # Check if block is at the output position
            # Try to transfer to conveyor
            if isinstance(block, Conveyor) and len(block.items) < block.item_capacity:
                block.items.append(item)
                self.buffer.pop(0)
                break

            # Try to transfer to storage
            elif isinstance(block, Storage) and block.can_store(item['type']):
                block.store_item(item)
                self.buffer.pop(0)
                break

    def is_adjacent(self, block):
        """Check if a block is adjacent to this drill"""
        return (abs(block.grid_x - self.grid_x) <= 1 and
                (abs(block.grid_y - self.grid_y) <= 1))

    def update(self, dt, cam_pos, world_map):
        super().update(dt, cam_pos)
        if self.is_built:
            self.update_connections(world_map, World.Blocks)
            self.mine_tick(dt)
            self.transfer_items()


class Conveyor(Block):
    def __init__(self, size, sprite, build_time, graphic_handler, speed=1.0, can_rotate=True):
        super().__init__(size, sprite, build_time, graphic_handler, can_rotate=can_rotate)
        self.speed = speed
        self.direction = Vector2(0, 0)  # Default right
        self.items = []  # List of items being transported
        self.item_capacity = 3  # Max items on this conveyor segment
        self.next_conveyor = None  # Connected conveyor in direction

        self.rotation_angle = 90
        self.rotate()  # Initialize direction

    def rotate(self):
        if super().rotate():
            # Update direction based on rotation
            if self.rotation_angle == 0:
                self.direction = Vector2(1, 0)  # Right
            elif self.rotation_angle == 90:
                self.direction = Vector2(0, -1)  # Up
            elif self.rotation_angle == 180:
                self.direction = Vector2(-1, 0)  # Left
            else:  # 270
                self.direction = Vector2(0, 1)   # Down
            return True
        return False

    def render(self, screen, cam_pos, scale_factor=1):
        super().render(screen, cam_pos, scale_factor)

        # Calculate the scaled camera position
        camX = cam_pos.x * (self.graphic_handler.curr_win.get_display().current_w / self.graphic_handler.curr_win.defX)
        camY = cam_pos.y * (self.graphic_handler.curr_win.get_display().current_h / self.graphic_handler.curr_win.defY)

        # Calculate base position
        render_x = self.worldx + camX
        render_y = self.worldy + camY

        if not self.is_built:
            return

        # Render conveyor base
        screen.blit(self.sprite, (render_x, render_y))

        # Get item sprite dimensions
        sample_sprite = next(iter(ITEM_SPRITES.values())) if ITEM_SPRITES else None
        item_width = sample_sprite.get_width() if sample_sprite else 16 * scale_factor
        item_height = sample_sprite.get_height() if sample_sprite else 16 * scale_factor

        # Calculate conveyor bounds
        conveyor_length = self.size * scale_factor
        travel_length = conveyor_length - max(item_width, item_height)

        # REVERSED Direction vectors (0°=right, 90°=up, 180°=left, 270°=down)
        dir_x, dir_y = {
            0: (1, 0),   # Now moves left-to-right (reversed from before)
            90: (0, -1),    # Now moves down-to-up
            180: (-1, 0),   # Now moves right-to-left
            270: (0, 1)   # Now moves up-to-down
        }.get(self.rotation_angle, (1, 0))  # Default to left-to-right

        for item in self.items:
            item_sprite = ITEM_SPRITES.get(item['type'])
            if not item_sprite:
                continue

            # Calculate position - note we now start at 1.0 and go to 0.0
            progress = 1.0 - min(max(item['progress'], 0.0), 1.0)  # Inverted progress
            travel_distance = progress * travel_length

            # Base position (conveyor center minus item center)
            pos_x = render_x + ((conveyor_length * (self.graphic_handler.curr_win.get_display().current_w / self.graphic_handler.curr_win.defX)) - item_width) / 2
            pos_y = render_y + ((conveyor_length * (self.graphic_handler.curr_win.get_display().current_h / self.graphic_handler.curr_win.defY)) - item_height) / 2

            # Apply movement
            pos_x += dir_x * travel_distance
            pos_y += dir_y * travel_distance

            # Render item
            screen.blit(item_sprite, (pos_x, pos_y))

    def update_connections(self, world_blocks):
        """Find connected conveyor in output direction"""
        target_x = self.grid_x + int(self.direction.x)
        target_y = self.grid_y + int(self.direction.y)

        for block in world_blocks:
            if (block.grid_x == target_x and
                    block.grid_y == target_y and
                    isinstance(block, Conveyor)):
                self.next_conveyor = block
                return
        self.next_conveyor = None

    def transfer_items(self):
        """Move items along conveyor"""
        for item in self.items[:]:  # Iterate copy for safe removal
            item['progress'] += self.speed * 0.016  # Assuming ~60fps

            if item['progress'] >= 1.0:  # Reached end of conveyor
                if self.next_conveyor and len(
                        self.next_conveyor.items) < self.next_conveyor.item_capacity and self.next_conveyor.is_built:
                    item['progress'] = 0
                    self.next_conveyor.items.append(item)
                    self.items.remove(item)
                else:
                    item['progress'] = 1
                # Else item stays at end of conveyor

    def update(self, dt, cam_pos):
        super().update(dt, cam_pos)
        if self.is_built:
            if not self.next_conveyor:
                self.update_connections(World.Blocks)
            self.transfer_items()


class Storage(Block):
    """Item storage container"""

    def __init__(self, size, sprite, build_time, graphic_handler, capacity=100):
        super().__init__(size, sprite, build_time, graphic_handler)
        self.capacity = capacity
        self.stored_items = {}
        self.inputs = []

    def can_store(self, item_type):
        """Check if storage can accept more items of this type"""
        current_amount = self.stored_items.get(item_type, 0)
        return current_amount < self.capacity

    def store_item(self, item):
        """
        Store an item in this storage
        Returns: True if successful, False if no space
        """
        item_type = item['type']
        if self.can_store(item_type):
            self.stored_items[item_type] = self.stored_items.get(item_type, 0) + item['amount']
            return True
        return False

    def update_connections(self, world_blocks):
        """Find all connected input blocks"""
        self.inputs = []
        # Check all 4 adjacent positions
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            for block in world_blocks:
                if (block.grid_x == self.grid_x + dx and
                        block.grid_y == self.grid_y + dy and
                        isinstance(block, (Conveyor, Drill))):
                    self.inputs.append(block)

    def update(self, dt, cam_pos):
        super().update(dt, cam_pos)
        if self.is_built and not self.inputs:
            self.update_connections(World.Blocks)
