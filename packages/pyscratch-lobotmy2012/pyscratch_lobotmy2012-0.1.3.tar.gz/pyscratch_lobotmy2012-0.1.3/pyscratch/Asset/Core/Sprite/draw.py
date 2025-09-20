from .variable import Variable
from ..text import Text
import pygame

class Draw(Variable):
    def __init__(self, screen, pos, image_path, angle):
        super().__init__(screen, pos, image_path, angle)
    
    def draw_text(self, text, layer, size, pos: list):
        """Drawing text without a variable"""
        try:
            self.show_text[layer] = layer, Text(pygame.font.Font(None, size), pos)
        except IndexError:
            self.show_text.append(layer, Text(pygame.font.Font(None, size), pos))
        self.sprites.add(self.show_text[layer])
        self.show_text[layer].update_text(text)
    
    def remove_text(self, layer):
        for i in range(len(self.show_text)):
            if i == layer:
                self.sprites.remove(self.show_text[i])
                self.show_text[i] == None
                break