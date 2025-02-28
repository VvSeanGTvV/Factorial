import random
import pygame
import sys

from Graphics import Graphics

# Initialize Pygame
pygame.init()

# Set window dimensions
width, height = 640, 480
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

# Set the frame rate
clock = pygame.time.Clock()

# Set window title
pygame.display.set_caption("Factorial")

# Game loop
running = True
camX = 0
camY = 0

getTicksLastFrame = 0
Graphic = Graphics()

velcoity = 0
speed = 1
maxVel = 10

Map = []
def createMap(mapSize):
    rand = random.Random()
    tileSelect = ["basalt1.png", "arkycite-floor.png"]
    for y in range(mapSize):
        for x in range(mapSize):
            p = rand.randint(0, 2) + rand.randint(-2, 2)
            c = rand.randint(0, len(tileSelect) - 1)
            if (p >= 1):
                c = rand.randint(0, len(tileSelect) - 1)
            Map.append(pygame.image.load(tileSelect[c]))


createMap(10)
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # HANDLER FPS
    delta = Graphic.delta()
    fps = 1 / delta
    gameSpeed = 120 / fps

    clock.tick(120)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        velcoity += speed * gameSpeed
        camX += velcoity
    if keys[pygame.K_d]:
        velcoity += speed * gameSpeed
        camX += -velcoity
    if keys[pygame.K_w]:
        velcoity += speed * gameSpeed
        camY += velcoity
    if keys[pygame.K_s]:
        velcoity += speed * gameSpeed
        camY += -velcoity

    velcoity -= velcoity / 10
    if (velcoity > maxVel):
        velcoity = maxVel
    if (velcoity < 0):
        velcoity = 0
    print(camX, camY)
    Graphic.displayTable(Map, screen, camX, camY)
    # Draw a circle
    # pygame.draw.circle(screen, (255, 255, 255), (width // 2, height // 2), 50)  # White circle in the center




# Quit Pygame
pygame.quit()
sys.exit()
