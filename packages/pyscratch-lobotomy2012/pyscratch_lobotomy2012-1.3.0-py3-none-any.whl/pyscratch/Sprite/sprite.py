from ..Asset.Core.Sprite.draw import Draw

class Sprite:
    def __init__(self, screen, pos, image_path, angle = 90):
        self.all_sprite = []
        self.as_clone = False
        self.core = Draw(screen, pos, image_path, angle)
    
    def find_sprite(self, name: str):
        for i in self.all_sprite:
            if i.__class__.__name__ == name:
                return i
            yield
        return None