import pygame
from pygame import Vector2

from Graphics import TextSprite


class Button:
    pressed = False

    def __init__(self, text: TextSprite, width, height, color, color_hover, color_clicked, click_listener):
        """Creates a button"""
        self.text = text
        self.width = width
        self.height = height
        self.color = color
        self.color_hover = color_hover
        self.color_clicked = color_clicked
        self.click_listener = click_listener
        self.button_position = Vector2(0, 0)

    def update(self):
        scaleX, scaleY = self.text.graphic_handler.getWindowScale()
        mouse = pygame.mouse.get_pos()

        if self.button_position.x * scaleX <= mouse[0] <= (self.width * scaleX / 2) + (self.button_position.x * scaleX) and self.button_position.y * scaleY <= mouse[1] <= (self.height * scaleY / 2) + (self.button_position.y * scaleY):
            if pygame.mouse.get_pressed()[0] and not self.pressed:
                self.pressed = True

        if not pygame.mouse.get_pressed()[0] and self.pressed:
            self.click_listener()
            self.pressed = False

    def render(self, screen, position: Vector2):
        scaleX, scaleY = self.text.graphic_handler.getWindowScale()
        mouse = pygame.mouse.get_pos()

        self.button_position = position
        if (self.pressed):
            pygame.draw.rect(screen, self.color_clicked,
                             [position.x * scaleX, position.y * scaleY, (self.width / 2) * scaleX,
                              (self.height / 2) * scaleY])
        else:
            if position.x * scaleX <= mouse[0] <= (self.width * scaleX / 2) + (position.x * scaleX) and position.y * scaleY <= mouse[1] <= (self.height * scaleY / 2) + (position.y * scaleY):
                pygame.draw.rect(screen, self.color_hover,
                                 [position.x * scaleX, position.y * scaleY, (self.width / 2) * scaleX,
                                  (self.height / 2) * scaleY])
            else:
                pygame.draw.rect(screen, self.color,
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
