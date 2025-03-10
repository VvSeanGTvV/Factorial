import pygame
from pygame import Vector2

from Graphics import TextSprite


class Button:
    def __init__(self, text: TextSprite, width, height, color, color_hover, color_clicked):
        self.text = text
        self.width = width
        self.height = height
        self.color = color
        self.color_hover = color_hover
        self.color_clicked = color_clicked

    def render(self, screen, position: Vector2):
        mouse = pygame.mouse.get_pos()
        self.text.draw_text(screen, (position.x, position.y))
        if self.width/2 <= mouse[0] <= self.width/2+140 and self.height/2 <= mouse[1] <= self.height/2+40:
            pygame.draw.rect(screen, self.color_hover,[self.width/2,self.height/2, position.x,position.y])
        else:
            pygame.draw.rect(screen,self.color_clicked,[self.width/2,self.height/2, position.x,position.y])