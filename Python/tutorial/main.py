import pygame

pygame.init()

width = 800
height = 600

win = pygame.display.set_mode((width, height)) # win is a surface since it is the window that we will draw stuff on.
pygame.display.set_caption("First game in pygame")


game_running = True

# surfaces - canvas that we draw on. 
# fill - fill the screen with something ( color, image, etc.)

white = (255,255,255)
# in pygame, to make colors, you will have to use rgb color format.
# RGB- Red, Green, Blue
# there are 256 values in rgb
# 0 - 255

while game_running:

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()

	win.fill(white)
	# each time we make a change to the display, we will have to update it.
	pygame.display.update()
	