import pygame

from Graphics import TextSprite


class Button:
    def __init__(self, text: TextSprite, width, height, color, color_hover, color_clicked):
        self.text = text
        self.width = width
        self.height = height
        self.color = color
        self.color_hover = color_hover
        self.color_clicked = color_clicked

    def render(self):
        mouse = pygame.mouse.get_pos()
        if width/2 <= mouse[0] <= width/2+140 and height/2 <= mouse[1] <= height/2+40:
            pygame.draw.rect(screen, color_light,[width/2,height/2,140,40])
        else:
            pygame.draw.rect(screen,color_dark,[width/2,height/2,140,40])