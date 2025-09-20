from .events import Events
import pygame

class Control(Events):
    def __init__(self, screen, pos, image_path, angle):
        super().__init__(screen, pos,  image_path, angle)

    def wait(self, sec):
        """Remember to add \"yield from\" like \"yield from self.core.wait(1)\""""
        start = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start < sec * 1000 and self.running:
            yield
    
    def wait_until(self, arg: bool):
        """Remember to add \"yield from\" like \"yield from self.core.wait_until(True)\""""
        while self.running and arg:
            yield
        
    def call_def(self, one):
        """To call a \"def\", it's just like \"my block\""""
        while self.running:
            try:
                next(one)
            except StopIteration:
                break

            yield

    def create_clone(self, One):
        """This is not like scratch, remember to add a variable like this:\n
        \t\"clone = self.core.create_clone(Sprite1)\""""
        clone = One(self.screen)
        clone.as_clone = True
        self.sprites.add(clone.core.sprites)
        return clone

    def update_clones(self):
        """nevermind this is not for you"""
        for clone in self.clones:
            clone.running = self.running
            clone.core.input_text = self.input_text
            clone.core.input_key = self.input_key

    def delete_clone(self, clone):
        if clone in self.clones:
            self.sprites.remove(clone.core.sprites)
            self.clones.remove(clone)
    
    def stop_all(self):
        """If u want t stop only 1 script, use \"return\""""
        self.all_running = False