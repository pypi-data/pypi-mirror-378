from .looks import Looks
import pygame

class Sound(Looks):
    def __init__(self, screen, pos, image_path, angle):
        super().__init__(screen, pos, image_path, angle)
    
    def play_sound(self, sound_path, until_done = False):
        sound = pygame.mixer.Sound(sound_path)
        sound.set_volume(self.volume / 100)
        channel = sound.play()
        
        if until_done:
            while channel.get_busy() and self.running:
                channel.set_volume(self.pad_left / 100, self.pad_right / 100)
                yield
    
    def stop_all_sound(self):
        pygame.mixer.stop()

    def change_sound_effect_by(self, pitch = None, pad_left = None, pad_right = None):
        if pitch is not None:
            if self.pitch + pitch > 100:
                self.pitch = 100
            elif self.pitch + pitch < 0:
                self.pitch = 0
            else:
                self.pitch += pitch
        if pad_left is not None:
            if self.pad_left + pad_left > 100:
                self.pad_left = 100
            elif self.pad_left + pad_left < 0:
                self.pad_left = 0
            else:
                self.pad_left += pad_left
        if pad_right is not None:
            if self.pad_right + pad_right > 100:
                self.pad_right = 100
            elif self.pad_right + pad_right < 0:
                self.pad_right = 0
            else:
                self.pad_right += pad_right

    def set_sound_effect(self, pitch = None, pad_left = None, pad_right = None):
        if pitch is not None:
            if pitch > 100:
                pitch = 100
            elif pitch < 0:
                pitch = 0
            self.pitch = pitch
        if pad_left is not None:
            if pad_left > 100:
                pad_left = 100
            elif pad_left < 0:
                pad_left = 0
            self.pad_left = pad_left
        elif pad_right is not None:
            if pad_right > 100:
                pad_right = 100
            elif pad_right < 0:
                pad_right = 0
            self.pad_right = pad_right

    def clear_all_sound_effect(self):
        self.pitch = 100
        self.pad_right = 100
        self.pad_left = 100

    def change_volume_by(self, volume):
        if self.volume + volume > 100:
            self.volume = 100
        elif self.volume + volume < 0:
            self.volume = 0
        else:
            self.volume += volume

    def set_volume(self, volume):
        if volume > 100:
            volume = 100
        elif volume < 0:
            volume = 0
        self.volume = volume