import random
import pygame
import sys

from Graphics import Graphics, Window, text_sprite

# Initialize Pygame
pygame.init()

# Set window dimensions
Display = Window(640, 360, 1920, 1080, pygame.FULLSCREEN, 0)
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


mapSize = 64
Map = generateTileMap(1024, mapSize, mapSize, ["basalt1.png", "basalt1.png", "arkycite-floor.png", "gold-sand1.png"])
pygame.font.init()  # you have to call this at the start,

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # HANDLER FPS
    gameSpeed = 120 / Graphic.getFPS()
    scalarX, scalarY = (Display.getDisplay().current_w / Display.defX), (Display.getDisplay().current_h / Display.defY)

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

    camX += velX
    camY += velY


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


    testText = text_sprite('Arial', 36, f"X: {int(camX // 16)} | Y: {int(camY // 16)}", True, (255, 255, 255))
    text_sprite.draw_text(testText, Display.display, (30, 30))
    # Draw a circle
    # pygame.draw.circle(screen, (255, 255, 255), (width // 2, height // 2), 50)  # White circle in the center

# Quit Pygame
pygame.quit()
sys.exit()
