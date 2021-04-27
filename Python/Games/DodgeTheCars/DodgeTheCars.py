import pygame 
import random

pygame.init()

crash_sound = pygame.mixer.Sound('crash_sound.wav')

display_width = 800
display_height = 600

black = (0,0,0)
white = (255,255,255)
red = (150,0,0)
yellow = (255,255,0)
green = (0,150,0)
gray = (128,128,128)

bright_green = (0,255,0)
bright_red = (255,0,0)

car_width = 60

# Setting up the screen
gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption("DodgeTheCars!")
clock = pygame.time.Clock()

carImg1 = pygame.image.load("racecar1.png")
carImg2 = pygame.image.load("racecar2.png")
carImg3 = pygame.image.load("racecar3.png")

cars = random.choice([carImg1, carImg2, carImg3])

enemy_car = pygame.image.load("enemy_car.png")

carIcon = pygame.image.load("caricon.png")


pygame.display.set_icon(carIcon)

pause = False


def cars_dodged(count):
    font = pygame.font.SysFont("agencyfb", 25)
    text = font.render("Cars Dodged: " + str(count), True, yellow)
    gameDisplay.blit(text, (0,0))


def enemyCar(enemyx, enemyy):
    gameDisplay.blit(enemy_car,(enemyx, enemyy))


def car(x,y):
    gameDisplay.blit(cars,(x,y))


def text_objects(text, font):
    textSurface = font.render(text, True, white)
    return textSurface, textSurface.get_rect()


def crash():

    pygame.mixer.Sound.play(crash_sound)

    largeText = pygame.font.SysFont("agencyfb",115, bold=True)
    TextSurf, TextRect = text_objects("You Crashed!", largeText)
    TextRect.center = ((display_width/2),(display_height/2))
    gameDisplay.blit(TextSurf, TextRect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()


        button("Play Again", 150,450,150,50, green, bright_green, game_loop)
        button("Exit", 550,450,100,50, red, bright_red, quitgame)

        pygame.display.update()
        clock.tick(15)



def button(msg, x, y, w, h, ic, ac, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(gameDisplay, ac, (x,y,w,h))
        if click[0] == 1 and action != None:
            action()
    else:
        pygame.draw.rect(gameDisplay, ic, (x,y,w,h))
    smallText = pygame.font.SysFont("agencyfb", 35, bold=True)
    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ( (x+(w/2)), (y+(h/2)) )
    gameDisplay.blit(textSurf, textRect)


def quitgame():
    pygame.quit()
    quit()


def unpause():
    global pause
    pause = False


def paused():

    largeText = pygame.font.SysFont("agencyfb",115, bold=True)
    TextSurf, TextRect = text_objects("Game Paused", largeText)
    TextRect.center = ((display_width/2),(display_height/2))
    gameDisplay.blit(TextSurf, TextRect)

    while pause:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()



        button("Resume", 150,450,110,50, green, bright_green, unpause)
        button("Exit", 550,450,100,50, red, bright_red, quitgame)

        pygame.display.update()
        clock.tick(15)


def main_menu():
    intro = True

    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        gameDisplay.fill(black)
        largeText = pygame.font.SysFont("agencyfb",115, bold=True)
        TextSurf, TextRect = text_objects("DodgeTheCars!", largeText)
        TextRect.center = ((display_width/2),(display_height/2))
        gameDisplay.blit(TextSurf, TextRect)

        button("Play", 150,450,100,50, green, bright_green, game_loop)
        button("Exit", 550,450,100,50, red, bright_red, quitgame)

        pygame.display.update()
        clock.tick(15)


# Main Game Loop
def game_loop():
    global pause
    
    x = (display_width * 0.45)
    y = (display_height * 0.8)

    x_change = 0

    enemyCar_startx = random.randrange(0, display_width)
    enemyCar_starty = -600
    enemyCar_speed = 9
    
    dodged = 0

    # Game Logic
    gameExit = False

    while not gameExit:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x_change = - 13
                if event.key == pygame.K_RIGHT:
                    x_change = 13
                if event.key == pygame.K_p:
                    pause = True
                    paused()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    x_change = 0

        x += x_change

        gameDisplay.fill(black)         


        #enemyx, enemyy
        enemyCar(enemyCar_startx, enemyCar_starty)
        enemyCar_starty += enemyCar_speed
        car(x,y)
        cars_dodged(dodged)

        if x > display_width - car_width or x < 0:
            crash()
        
        if enemyCar_starty > display_height:
            enemyCar_starty = 0 - 100
            enemyCar_startx = random.randrange(0,display_width)
            dodged += 1
            enemyCar_speed += 1


        if y < enemyCar_starty + 100:
            
            if x > enemyCar_startx and x < enemyCar_startx + 60  or x + car_width > enemyCar_startx and x + car_width < enemyCar_startx + 60:
                crash()

        pygame.display.update()
        clock.tick(60)

main_menu()
game_loop()
pygame.quit()
quit()


print("Hello world")