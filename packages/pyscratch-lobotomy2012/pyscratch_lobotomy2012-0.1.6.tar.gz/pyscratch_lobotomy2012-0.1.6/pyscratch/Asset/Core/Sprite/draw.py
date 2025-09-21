from .variable import Variable
from ..text import Text
import pygame

class Draw(Variable):
    def __init__(self, screen, pos, image_path, angle):
        super().__init__(screen, pos, image_path, angle)
    
    def draw_text(self, text, layer: int, size: int, pos: list):
        """Drawing text without a variable"""
        self.remove_text(layer)
        self.show_text.insert(-layer, Text(pygame.font.Font(None, size), pos))
        self.sprites.add(self.show_text[-layer])
        self.show_text[-layer].update_text(text)
    
    def remove_text(self, layer: int):
        try:
            self.sprites.remove(self.show_text[-layer])
            self.show_text[-layer] == None
        except IndexError:
            pass