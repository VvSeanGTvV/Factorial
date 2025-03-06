import random
import pygame
import sys

from pygame import Vector2

from Graphics import Graphics, Window, text_sprite
from World import Player, Camera, Map

# Initialize Pygame
pygame.init()

# Set window dimensions
Display = Window(640, 360, 1920, 1080, pygame.FULLSCREEN, 120, 0)
Graphic = Graphics(Display)

# Set the frame rate
clock = pygame.time.Clock()

# Set window title
pygame.display.set_caption("Factorial [DEVELOPMENT]")

# Game loop
running = True

velX = 0
velY = 0
speed = 10
maxVel = 50
pygame.font.init()

player = Player(0, 0, pygame.image.load("assets/player/halberd-ship.png"), 24, Graphic)
camera = Camera(0, 0)
world = Map(Display, 512, Graphic)


def lerp(a, b, t):
    return a + (b - a) * t


while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # HANDLER FPS
    gameSpeed = Graphic.delta()
    scalarX, scalarY = Graphic.getWindowScale()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        velX += speed * gameSpeed
    if keys[pygame.K_d]:
        velX -= speed * gameSpeed

    if keys[pygame.K_w]:
        velY += speed * gameSpeed
    if keys[pygame.K_s]:
        velY -= speed * gameSpeed

    if keys[pygame.K_x]:
        # Quit Pygame
        pygame.quit()
        sys.exit()

    if keys[pygame.K_m]:
        player.updatePositionWorld(-sys.maxsize // 10, -sys.maxsize // 10)

    windowSX, windowSY = Graphic.getActiveDisplaySize()

    camera.updatePosition(
        lerp(camera.pos.x, -player.worldx, speed * gameSpeed / scalarX),
        lerp(camera.pos.y, -player.worldy, speed * gameSpeed / scalarY)
    )

    px, py = player.getPosition()
    player.updatePositionWorld(player.worldx - velX, player.worldy - velY)
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
    world.render(
        world.preloadTiles(["gold-sand1.png", "gold-sand2.png", "gold-sand3.png", "silver-plating.png", "basalt1.png"]),
        camera.pos.x * scalarX, camera.pos.y * scalarY)

    testText = text_sprite('Arial', 16,
                           f"X: {int(camera.getWorldPosition(16).x)} | Y: {int(camera.getWorldPosition(16).y)}", False,
                           (255, 255, 255), Graphic)
    text_sprite.draw_text(testText, Display.display, (16, 16))
    player.render(Display.display, -camera.pos.x, -camera.pos.y, Vector2(velX, velY))

    # Update the display
    pygame.display.update()  # Efficient refresh
    # print(Graphic.getFPS())

# Quit Pygame
pygame.quit()
sys.exit()
