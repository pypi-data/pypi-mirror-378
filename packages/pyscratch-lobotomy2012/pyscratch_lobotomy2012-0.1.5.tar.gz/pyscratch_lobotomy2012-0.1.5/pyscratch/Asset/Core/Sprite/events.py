from .sound import Sound
import pygame

class Events(Sound):
    def __init__(self, screen, pos, image_path, angle):
        super().__init__(screen, pos, image_path, angle)
    
    def when_key_pressed(self, key = "", any = False):
        keys = self.input_key

        if any:
            for pressed in keys:
                if pressed:
                    return True
            return False
        
        for keycode in range(len(keys)):
            if keys[keycode]:
                if pygame.key.name(keycode) == key:
                    return True
        
        return False

    def when_sprite_clicked(self):
        if self.click_sprite:
            return True
        return False