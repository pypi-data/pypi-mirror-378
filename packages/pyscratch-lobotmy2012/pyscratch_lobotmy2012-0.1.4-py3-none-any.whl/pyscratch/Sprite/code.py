import pygame

class Code:
    def __init__(self, Sprite):
        self.screen = pygame.display.set_mode((800, 600))
        self.running = True
        self.input_text = ""
        self.mouse_down = [False, (0, 0)]
        self.timer = pygame.time.get_ticks()

        self.sprite = []
        self.tasks = []
        self.sprites = pygame.sprite.Group()
        for i in range(len(Sprite)):
            self.sprite.append(Sprite[i](self.screen))

            self.start(i)
    
    def start(self, i):
        try:
            self.tasks[i] = self.sprite[i].run()
        except IndexError:
            self.tasks.append(self.sprite[i].run())

        self.sprites.add(self.sprite[i].core.sprites)

    def restart(self):
        self.stop()

        self.sprites.empty()
        self.running = True

        self.more_thread = []
        for i in range(len(self.sprite)):
            self.start(i)

    def update(self):
        if self.running:
            for i in range(len(self.sprite)):
                try:
                    next(self.tasks[i])
                except StopIteration:
                    pass
                except IndexError:
                    self.stop()

                self.sprite[i].core.input_text = self.input_text
                self.sprite[i].core.input_key = pygame.key.get_pressed()
                self.sprite[i].core.update_clones()

                if self.mouse_down[0]:
                    if not self.sprite[i].core.dragging:
                        if self.sprite[i].core.object.rect.collidepoint(self.mouse_down[1]):
                            self.sprite[i].core.click_sprite = True
                            if self.sprite[i].core.draggable:
                                self.sprite[i].core.dragging = True
                        else:
                            self.sprite[i].core.click_sprite = False
                else:
                    self.sprite[i].core.mouse_down = False
                    self.sprite[i].core.dragging = False

                if self.sprite[i].core.dragging:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.sprite[i].core.go_to(mouse_x, mouse_y)

                if not self.sprite[i].core.asking and self.input_text != "":
                    self.input_text = ""

                if not self.sprite[i].core.all_running:
                    self.stop()
                    break

            if self.running == False:
                self.stop()

            self.sprites.draw(self.screen)
    
    def stop(self):
        for i in range(len(self.sprite)):
            self.sprite[i].core.stop_all_sound()

        self.running = False