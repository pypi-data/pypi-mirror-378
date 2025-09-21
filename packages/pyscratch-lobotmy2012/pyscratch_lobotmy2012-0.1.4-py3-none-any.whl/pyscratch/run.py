from .Asset.Button.RunButton import RunButton
from .Asset.Button.StopButton import StopButton
import pygame
import sys

def run(code):
    code.screen.fill((255, 255, 255))
    clock = pygame.time.Clock()

    runButton = RunButton()
    stopButton = StopButton()
    button = pygame.sprite.Group(runButton, stopButton)
    print("started")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("closing")
                code.stop()
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                code.mouse_down = [True, event.pos]
            elif event.type == pygame.MOUSEBUTTONUP:
                code.mouse_down = [False, (0, 0)]

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    code.input_text = code.input_text[:-1]
                elif event.key == pygame.K_RETURN:
                    code.input_text += "\n"
                else:
                    code.input_text += event.unicode
                
            elif runButton.is_clicked(event):
                code.restart()
                print("restarted")
            
            elif stopButton.is_clicked(event):
                code.stop()
                print("stopped")

        if code.running:
            code.screen.fill((255, 255, 255))
            button.draw(code.screen)
            code.update()

        pygame.display.set_caption("PyScratch")

        pygame.display.flip()
        clock.tick(60)