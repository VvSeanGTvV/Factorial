import pygame
from pygame import Surface

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

    def render(self, screen):
        self.sprite = pygame.transform.scale(self.sprite, (int(self.size * (self.grahpicHandler.currWin.getDisplay().current_w / self.grahpicHandler.currWin.defX)), int(self.size * (self.grahpicHandler.currWin.getDisplay().current_h / self.grahpicHandler.currWin.defY))))

        screen.blit(self.sprite, (self.x - (self.sprite.get_rect().width // 2), self.y - (self.sprite.get_rect().height // 2)))
        #pygame.draw.rect(screen, self.colour, (self.x, self.y, self.size, self.size))
