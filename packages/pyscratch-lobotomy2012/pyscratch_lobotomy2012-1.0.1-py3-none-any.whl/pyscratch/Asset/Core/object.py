import pygame

class Object(pygame.sprite.Sprite):
    def __init__(self, pos, image_path):
        super().__init__()
        self.pos = pos
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect(center=self.pos)
        self.size = 1
        self.angle = 90

    def update(self, pos = None, angle = None, image_path=None, size=None):
        if pos:
            self.pos = pos
        if angle is not None:
            self.angle = angle
        if image_path is not None:
            self.original_image = pygame.image.load(image_path).convert_alpha()
            self.image = self.original_image
        if size is not None:
            self.size = size
        self.image = pygame.transform.rotozoom(self.original_image, self.angle, self.size)
        self.rect = self.image.get_rect(center=self.pos)