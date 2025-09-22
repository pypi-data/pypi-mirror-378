import pygame, os

class RunButton(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(f"{os.path.dirname(__file__)}\\..\\Image\\RunButton.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 0.2)
        self.rect = self.image.get_rect(topleft=(5, 5))

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False