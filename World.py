import math

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
        self.sprite = pygame.transform.scale(self.sprite, (int(self.size * (self.grahpicHandler.currWin.getDisplay().current_w / self.grahpicHandler.currWin.defX)), int(self.size * (self.grahpicHandler.currWin.getDisplay().current_h / self.grahpicHandler.currWin.defY))))
        if velocity.x != 0 or velocity.y != 0:
            angle = math.degrees(math.atan2(-velocity.y, velocity.x)) + 90
            rotated_sprite = pygame.transform.rotate(self.sprite, angle)
        else:
            rotated_sprite = self.sprite

        screen.blit(rotated_sprite, (self.x - (self.sprite.get_rect().width // 2) + camX, self.y - (self.sprite.get_rect().height // 2) + camY))
        #pygame.draw.rect(screen, self.colour, (self.x, self.y, self.size, self.size))
