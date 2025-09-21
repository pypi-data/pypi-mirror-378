from .control import Control
import pygame
from datetime import datetime

class Sensing(Control):
    def __init__(self, screen, pos, image_path, angle):
        super().__init__(screen, pos, image_path, angle)
    
    def ask(self, a):
        self.say(a)
        self.input_text = ""
        self.asking = True

        while self.asking:
            if self.input_text == "":
                pass
            elif self.input_text[-1] == "\n":
                self.asking = False

            self.inputing_text.update_text("answer: " + self.input_text)

            yield
            
        self.inputing_text.update_text("")
        return self.input_text[:-1]
    
    def touching(self, arg):
        if type(arg) == str:
            if arg == "edge":
                if self.object.rect.left < 0 or \
                    self.object.rect.right > self.screen.get_width() or \
                        self.object.rect.top < 0 or \
                            self.object.rect.bottom > self.screen.get_height():
                    return True
            elif arg == "mouse":
                if self.object.rect.collidepoint(pygame.mouse.get_pos()):
                    return True
        else:
            try:
                if self.object.rect.collidepoint((arg.core.object.rect.x, arg.core.object.rect.y)):
                    return True
            except:
                print("How do I check that")
                return False
        
        return False
    
    def mouse_is_down(self):
        if self.mouse_down:
            return True
        return False
    
    def set_drag_mode(self, arg: bool):
        self.draggable = arg
    
    def current_date(self, arg: str):
        """Example Uses: \"year\", \"month\", \"day\", \"hour\", \"minute\", \"second\""""
        now = datetime.now()
        if arg == "year":
            return now.strftime("%Y")
        elif arg == "month":
            return now.strftime("%m")
        elif arg == "day":
            return now.strftime("%d")
        elif arg == "hour":
            return now.strftime("%H")
        elif arg == "minute":
            return now.strftime("%M")
        elif arg == "second":
            return now.strftime("%S")
        return now