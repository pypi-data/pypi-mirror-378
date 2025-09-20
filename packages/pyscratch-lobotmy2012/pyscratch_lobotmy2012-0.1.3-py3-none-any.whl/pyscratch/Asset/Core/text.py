import pygame

class Text(pygame.sprite.Sprite):
    def __init__(self, font, pos):
        super().__init__()
        self.font = font
        self.pos = (pos[0], pos[1] - 70)
        self.image = self.font.render("", True, (0, 0, 0))
        self.rect = self.image.get_rect(topleft=self.pos)

    def update_text(self, text):
        self.image = self.font.render(text, True, (0, 0, 0))
        self.rect = self.image.get_rect(topleft=self.pos)

    def update(self, pos):
        self.pos = (pos[0], pos[1] - 70)
        self.rect = self.image.get_rect(topleft=self.pos)