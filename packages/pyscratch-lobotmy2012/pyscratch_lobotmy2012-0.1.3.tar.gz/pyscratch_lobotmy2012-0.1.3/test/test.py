from pyscratch import pyscratch

pyscratch.init()

class Sprite1(pyscratch.Sprite):
    def __init__(self, screen):
        super().__init__(screen, (100, 100), "costume2.png", 15)
    
    def a_run(self):
        while self.core.running:
            self.core.move(5)
            self.core.bounce_if_on_edge()

            yield
    
    def run(self):
        yield from self.core.call_def(self.a_run())

code = pyscratch.Code((Sprite1,))
pyscratch.run(code)