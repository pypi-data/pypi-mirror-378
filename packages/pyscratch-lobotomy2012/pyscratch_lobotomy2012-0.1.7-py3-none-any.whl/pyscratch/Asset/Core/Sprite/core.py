from ..text import Text
from ..object import Object
import pygame

class Core:
    def __init__(self, screen, pos, image_path, angle):
        font = pygame.font.Font(None, 26)

        self.screen = screen
        self.pos = list(pos)
        self.running = True

        self.object_text = Text(font, pos)
        self.inputing_text = Text(font, (10, screen.get_height()+70-20))
        self.object = Object(pos, image_path)

        self.clones = []
        self.input_key = ""
        self.click_sprite = False
        self.broadcast_list = []
        self.mouse_down = False
        self.draggable = False
        self.dragging = False
        self.size = self.object.size
        self.angle = angle % 360
        self.object.update(angle=self.angle - 90)
        self.asking = False
        self.input_text = ""
        self.volume = 100
        self.pitch = 100
        self.pad_left = 100
        self.pad_right = 100
        self.show_text = []
        
        self.sprites = pygame.sprite.Group()
        self.sprites.add(self.object, self.object_text, self.inputing_text)