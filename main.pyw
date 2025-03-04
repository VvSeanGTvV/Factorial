import random
import pygame
import sys

from pygame import Vector2

from Graphics import Graphics, Window, text_sprite
from World import Player

# Initialize Pygame
pygame.init()

# Set window dimensions
Display = Window(640, 360, 640, 360, pygame.RESIZABLE, 0)
Graphic = Graphics(Display)

# Set the frame rate
clock = pygame.time.Clock()

# Set window title
pygame.display.set_caption("Factorial [DEVELOPMENT]")

# Game loop
running = True
camX = 0
camY = 0

getTicksLastFrame = 0

velX = 0
velY = 0
speed = 0.1
maxVel = 50


def generateTileMap(seed, dx, dy, tileSet):
    """Generate a tilemap using a seed for repeatable randomization."""
    random.seed(seed)  # Set seed for consistency
    tilemap = [[pygame.image.load("assets/" + random.choice(tileSet)) for _ in range(dx)] for _ in range(dy)]
    return tilemap


mapSize = 50
Map = generateTileMap(512, mapSize, mapSize, ["gold-sand1.png", "gold-sand2.png", "gold-sand3.png", "silver-plating.png", "basalt1.png"])
pygame.font.init()
player = Player(0, 0, pygame.image.load("assets/player/halberd-ship.png"), 32, Graphic)

def lerp(a, b, t):
    return a + (b - a) * t

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # HANDLER FPS
    gameSpeed = 120 / Graphic.getFPS()
    scalarX, scalarY = Graphic.getWindowScale()

    clock.tick(120)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        velX += speed * gameSpeed * scalarX
    if keys[pygame.K_d]:
        velX -= speed * gameSpeed * scalarX

    if keys[pygame.K_w]:
        velY += speed * gameSpeed * scalarY
    if keys[pygame.K_s]:
        velY -= speed * gameSpeed * scalarY

    if keys[pygame.K_x]:
        # Quit Pygame
        pygame.quit()
        sys.exit()

    #camX += velX
    #camY += velY

    windowSX, windowSY = Graphic.getActiveDisplaySize()

    camX = lerp(camX, player.worldx + velX, 0.1)
    camY = lerp(camY, player.worldy + velY, 0.1)

    px, py = player.getPosition()
    player.updatePositionWorld(player.worldx + velX, player.worldy + velY)
    player.updatePosition(player.worldx + (windowSX // 2), player.worldy + (windowSY // 2))




    if (velX > maxVel / 10):
        velX -= velX / maxVel

    if (velX < -maxVel / 10):
        velX += -velX / maxVel

    if (velX < 0):
        velX += -velX / maxVel
    if (velX > 0):
        velX -= velX / maxVel

    if (velY > maxVel / 10):
        velY -= velY / maxVel
    if (velY < -maxVel / 10):
        velY += -velY / maxVel

    if (velY < 0):
        velY += -velY / maxVel
    if (velY > 0):
        velY -= velY / maxVel
    # print(velX, velY)
    Display.display.fill((0, 0, 0))
    Graphic.displayTable(Map, 40, 23, Display.display, camX * scalarX, camY * scalarY)


    testText = text_sprite('Arial', 16, f"X: {int(camX // 16)} | Y: {int(camY // 16)}", False, (255, 255, 255), Graphic)
    text_sprite.draw_text(testText, Display.display, (16, 16))
    player.render(Display.display, -camX, -camY, Vector2(velX, velY))


    # Update the display
    pygame.display.update()  # Efficient refresh
    #print(Graphic.getFPS())

# Quit Pygame
pygame.quit()
sys.exit()
