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
        scaleX, scaleY = self.text.graphic_handler.getWindowScale()
        mouse = pygame.mouse.get_pos()

        if position.x * scaleX <= mouse[0] <= (self.width * scaleX / 2) + (position.x * scaleX) and position.y * scaleY <= mouse[1] <= (self.height * scaleY / 2) + (position.y * scaleY):
            pygame.draw.rect(screen, self.color_hover,
                             [position.x * scaleX, position.y * scaleY, (self.width / 2) * scaleX,
                              (self.height / 2) * scaleY])
        else:
            pygame.draw.rect(screen, self.color_clicked,
                             [position.x * scaleX, position.y * scaleY, (self.width / 2) * scaleX,
                              (self.height / 2) * scaleY])
        self.text.draw_text_rect(screen,
                                 (position.x * scaleX + ((self.width * scaleX) / (self.text.text_settings["size"] * scaleX) / 2),
                                  position.y * scaleY + ((self.height * scaleY) / (self.text.text_settings["size"] * scaleY) / 2)),
                                 Vector2(
                                             ((self.width * scaleX) / (self.text.text_settings["size"] * scaleX) * 7.7),
                                             ((self.height * scaleY) / (self.text.text_settings["size"] * scaleY) * 8)
                                        )
                                 )
