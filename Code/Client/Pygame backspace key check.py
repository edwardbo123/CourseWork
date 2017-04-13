import pygame

pygame.init()
Screen = pygame.display.set_mode((500, 500))
Screen.convert_alpha(Screen)
Screen.fill((190, 190, 190))
while True:
    event = pygame.event.poll()
    if event.type == pygame.KEYDOWN:
        print(event.key)
