from .core import Core
import math
import random

class Motion(Core):
    def __init__(self, screen, pos, image_path, angle):
        super().__init__(screen, pos, image_path, angle)

    def point_in_direction(self, angle):
        self.angle = angle % 360
        self.object.update(angle=self.angle - 90)
    
    def turn(self, angle):
        self.angle = (self.angle + angle) % 360
        self.object.update(angle=self.angle - 90)
        
    def move(self, step):
        self.pos[0] += step * math.sin(math.radians(self.angle))
        self.pos[1] += step * math.cos(math.radians(self.angle))

        self.object.update(self.pos)
        self.object_text.update(self.pos)

    def go_to(self, x, y, go_random = False):
        if go_random:
            x = random.randint(0, 800)
            y = random.randint(0, 600)

        self.pos[0] = x
        self.pos[1] = y

        self.object.update(self.pos)
        self.object_text.update(self.pos)

    def glide(self, x, y, sec, go_random = False):
        if go_random:
            x = random.randint(0, 800)
            y = random.randint(0, 600)

        steps = int(sec * 60)
        step_x = (x - self.pos[0]) / steps
        step_y = (y - self.pos[1]) / steps
        for _ in range(steps):
            self.pos[0] += step_x
            self.pos[1] += step_y
            self.object.update(self.pos)
            self.object_text.update(self.pos)
            yield

    def bounce_if_on_edge(self):
        bounced = False

        if self.object.rect.left < 0:
            self.pos[0] = self.object.rect.width // 2
            self.point_in_direction(-self.angle)
            bounced = True
        elif self.object.rect.right > self.screen.get_width():
            self.pos[0] = self.screen.get_width() - self.object.rect.width // 2
            self.point_in_direction(-self.angle)
            bounced = True

        if self.object.rect.top < 0:
            self.pos[1] = self.object.rect.height // 2
            self.point_in_direction(180 - self.angle)
            bounced = True
        elif self.object.rect.bottom > self.screen.get_height():
            self.pos[1] = self.screen.get_height() - self.object.rect.height // 2
            self.point_in_direction(180 - self.angle)
            bounced = True

        if bounced:
            self.object.update(self.pos)
            self.object_text.update(self.pos)