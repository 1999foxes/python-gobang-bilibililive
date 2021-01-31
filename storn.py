import pygame
import math


pygame.init()

x = []
y = []
for i in range(0, 15):
    x.append(28 + i * 40)
    y.append(28 + i * 40)


class Storn_Black(pygame.sprite.Sprite):
    
    def __init__(self,pos):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load('image/storn_black.png')\
                    .convert_alpha()
        self.rect = self.image.get_rect()
        self.pos = pos

    def location(self):
        return self.pos

    def image_rect(self):
        return self.pos[0] - self.rect.width//2, self.pos[1] - self.rect.height//2



class Storn_White(pygame.sprite.Sprite):
    def __init__(self,pos):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load('image/storn_white.png')\
                    .convert_alpha()
        self.rect = self.image.get_rect()
        self.pos = pos

    def location(self):
        return self.pos

    def image_rect(self):
        return self.pos[0] - self.rect.width//2, self.pos[1] - self.rect.height//2

