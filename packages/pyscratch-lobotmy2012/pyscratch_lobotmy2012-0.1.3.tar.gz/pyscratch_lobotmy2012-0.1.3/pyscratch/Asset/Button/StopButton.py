import pygame, os

class StopButton(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(f"{os.path.dirname(__file__)}\..\Image\StopButton.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (42, 42))
        self.rect = self.image.get_rect(topleft=(50, 4))

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False