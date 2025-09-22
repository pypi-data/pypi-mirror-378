from ..Asset.Core.Sprite.draw import Draw

class Sprite:
    def __init__(self, screen, pos, image_path, angle = 90):
        self.as_clone = False
        self.core = Draw(screen, pos, image_path, angle)

class Background:
    def __init__(self):
        pass