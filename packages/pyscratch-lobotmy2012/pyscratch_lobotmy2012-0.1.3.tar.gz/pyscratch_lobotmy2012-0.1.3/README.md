# PyScratch
Scratch but python?

PyScratch bridges the gap between Scratch and Python, maybe. This module implements all code blocks in scratch, but not includes extentions.

# Demo
```python
from Lib.PyScratch import pyscratch

pyscratch.init()

class Sprite1(pyscratch.Sprite):
    def __init__(self, screen):
        super().__init__(screen, (100, 100), "costume1.png", 15)

    def run(self):
        self.core.go_to(100, 100)
        self.core.say("Hello, PyScratch!")
        self.core.say(str(self.core.current_date("year")))
        costume = ["costume1.png", "costume2.png"]
        i = 0

        while self.core.running:
            self.core.change_costume(costume[int(i%2)])
            self.core.move(5)
            self.core.bounce_if_on_edge()

            i += 0.25
            yield

code = pyscratch.Code((Sprite1,))
pyscratch.run(code)
```
<img width="1003" height="789" alt="image" src="https://github.com/user-attachments/assets/2500bd2a-c988-4d12-8848-5919438c4e81" />
