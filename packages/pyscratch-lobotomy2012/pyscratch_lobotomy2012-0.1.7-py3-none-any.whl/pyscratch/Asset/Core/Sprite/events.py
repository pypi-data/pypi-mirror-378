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

    def update_broadcast_list(self, previous_broadcast_list):
        """just don't care about this"""
        self.broadcast_list = previous_broadcast_list
    
    def clear_broadcast_list(self):
        """just.. don't care about this"""
        self.broadcast_list = []

    def broadcast(self, name):
        if not (name in self.broadcast_list):
            self.broadcast_list.append(name)
    
    def when_receive_broadcast(self, name):
        if name in self.broadcast_list:
            return True
        return False

    def when_sprite_clicked(self):
        if self.click_sprite:
            return True
        return False