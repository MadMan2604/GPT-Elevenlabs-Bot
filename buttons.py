import pygame

# Create the class for the button 
class Button(pygame.sprite.Sprite):
    def __init__(self, image, pos):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

    def draw(self, surface):
        surface.blit(self.image, self.rect) 

    