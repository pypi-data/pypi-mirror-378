from .motion import Motion
import pygame

class Looks(Motion):
    def __init__(self, screen, pos, image_path, angle):
        super().__init__(screen, pos, image_path, angle)
        
    def say(self, msg, sec=None):
        self.object_text.update_text(msg)
        if sec is not None:
            start = pygame.time.get_ticks()
            while pygame.time.get_ticks() - start < sec * 1000 and self.running:
                self.clock.tick(60)
            self.object_text.update_text("")
    
    def think(self, msg, sec=None):
        self.object_text.update_text("Think: " + msg)
        if sec is not None:
            start = pygame.time.get_ticks()
            while pygame.time.get_ticks() - start < sec * 1000 and self.running:
                self.clock.tick(60)
            self.object_text.update_text("")
        
    def change_costume(self, image_path):
        """There is no next costume, use\"\n
        \tcostume = [costume1.png, costume2.png]\n
        \ti = 0\n\"
        \tIn the \"while self.core.running:\" add\"\n
        \tself.core.change_costume(costume[int(i%2)])\n
        \ti += 0.25"""
        self.object.update(image_path=image_path)
    
    def change_size_by(self, size):
        self.size *= (size / 100) % 100
        self.object.update(size=self.size)
    
    def set_size(self, size):
        self.size = (size / 100)
        self.object.update(size=self.size)
    
    def show(self):
        if not self.sprites.has(self.object):
            self.sprites.add(self.object)

    def hide(self):
        if self.sprites.has(self.object):
            self.sprites.remove(self.object)
    
    def go_layer(self, font = False, back = False, layer = None):
        if font:
            self.sprites.remove(self.object)
            self.sprites.add(self.object)
        elif back:
            self.sprites.remove(self.object)
            self.sprites.add_internal(self.object, 0)
        elif layer:
            self.sprites.remove(self.object)
            self.sprites.add_internal(self.object, layer)