import random
from tkinter import Image

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

velX = 0
velY = 0
speed = 0.1
maxVel = 50

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

            Map.append(pygame.image.load("assets/" + tileSelect[c]))


createMap(16)
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # HANDLER FPS
    gameSpeed = 120 / Graphic.getFPS()

    clock.tick(120)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        velX += speed * gameSpeed
    if keys[pygame.K_d]:
        velX -= speed * gameSpeed

    if keys[pygame.K_w]:
        velY += speed * gameSpeed
    if keys[pygame.K_s]:
        velY -= speed * gameSpeed

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
    Graphic.displayTable(Map, screen, camX, camY)
    # Draw a circle
    # pygame.draw.circle(screen, (255, 255, 255), (width // 2, height // 2), 50)  # White circle in the center




# Quit Pygame
pygame.quit()
sys.exit()
