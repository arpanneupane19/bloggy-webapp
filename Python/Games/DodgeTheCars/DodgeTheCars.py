import pygame 
import random
import sys

pygame.init()

crash_sound = pygame.mixer.Sound('crash_sound.wav')

display_width = 800
display_height = 600

black = (0,0,0)
white = (255,255,255)
red = (150,0,0)
yellow = (128,128,0)
green = (0,150,0)
gray = (128,128,128)
blue = (0,0,128)

bright_green = (0,230,0)
bright_red = (255,0,0)
bright_yellow = (230,230,0)
bright_blue = (0,0,255)

car_width = 60

# Setting up the screen
gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption("DodgeTheCars!")
clock = pygame.time.Clock()

carImg1 = pygame.image.load("racecar1.png")
carImg2 = pygame.image.load("racecar2.png")
carImg3 = pygame.image.load("racecar3.png")

car_display = random.choice([carImg1, carImg2, carImg3])

enemy_car = pygame.image.load("enemy_car.png")

carIcon = pygame.image.load("caricon.png")


pygame.display.set_icon(carIcon)

pause = False


def cars_dodged(count):
    font = pygame.font.SysFont("agencyfb", 25)
    text = font.render("Cars Dodged: " + str(count), True, bright_yellow)
    gameDisplay.blit(text, (0,0))

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
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    sys.exit()


        button("Play Again", 150,350,150,50, green, bright_green, game_loop)
        button("Menu", 350,350,150,50, green, bright_green, main_menu)
        button("Exit", 550,350,100,50, red, bright_red, quitgame)

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
    sys.exit()


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
                sys.exit()
            if event.key == pygame.K_q:
                sys.exit()



        button("Resume", 150,450,110,50, green, bright_green, unpause)
        button("Exit", 550,450,100,50, red, bright_red, quitgame)

        pygame.display.update()
        clock.tick(15)

def car1_select():
    global car_display
    car_display = pygame.image.load('racecar1.png')
    game_loop()

def car2_select():
    global car_display
    car_display = pygame.image.load('racecar2.png')
    game_loop()

def car3_select():
    global car_display
    car_display = pygame.image.load('racecar3.png')
    game_loop()


def select():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    sys.exit()
                if event.key == pygame.K_b:
                    main_menu()
        gameDisplay.fill(black)
        car1 = gameDisplay.blit(carImg1, (175, 200))
        car2 = gameDisplay.blit(carImg2, (375, 200))
        car3 = gameDisplay.blit(carImg3, (575, 200))
        button("Back", 10, 10, 100, 50, yellow, bright_yellow, main_menu)
        button("Select", 155,300,100,50, red, bright_red, car1_select)
        button("Select", 360,300,100,50, blue, bright_blue, car2_select)
        button("Select", 560,300,100,50, green, bright_green, car3_select)

        pygame.display.update()


def help():
    black = (0,0,0)
    white = (255,255,255)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    main_menu()
                if event.key == pygame.K_q:
                    sys.exit()
                if event.key == pygame.K_b:
                    main_menu()

        gameDisplay.fill(black)
        help_text = pygame.font.SysFont("agencyfb", 40, bold=True)
        help_text_render = help_text.render('Keybinds', True, white)
        help_text_keys_c = help_text.render('c: Continue', True, white)
        help_text_keys_q = help_text.render('q: Exit', True, white)
        help_text_keys_p = help_text.render('p: Pause', True, white)
        help_text_keys_b = help_text.render('b: Back', True, white)
        help_text_keys_right = help_text.render("Right arrow: move right", True, white)
        help_text_keys_left = help_text.render("Left arrow: move left", True, white)
        help_src_code = help_text.render("Code: github.com/arpanneupane19/DodgeTheCars", True, white)
        gameDisplay.blit(help_text_render, (325, 50))
        gameDisplay.blit(help_text_keys_c, (325, 100))
        gameDisplay.blit(help_text_keys_q, (325, 150))
        gameDisplay.blit(help_text_keys_p, (325, 200))
        gameDisplay.blit(help_text_keys_b, (325, 250))
        gameDisplay.blit(help_text_keys_right, (325, 300))
        gameDisplay.blit(help_text_keys_left, (325, 350))
        gameDisplay.blit(help_src_code, (0, 400))

        button("Back", 20,20,150,50, yellow, bright_yellow, main_menu)
        pygame.display.update()
        clock.tick(15)
        


def main_menu():
    intro = True

    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    sys.exit()
                if event.key == pygame.K_SPACE:
                    game_loop()

        gameDisplay.fill(black)
        largeText = pygame.font.SysFont("agencyfb",115, bold=True)
        TextSurf, TextRect = text_objects("DodgeTheCars!", largeText)
        TextRect.center = ((display_width/2),(display_height/2))
        gameDisplay.blit(TextSurf, TextRect)

        button("Play", 150,450,100,50, green, bright_green, game_loop)
        button("Select", 350,450, 100,50, yellow, bright_yellow, select)
        button("Help?", 550,450,100,50, blue, bright_blue, help)
        button("Exit", 350,525,100,50, red, bright_red, quitgame)


        pygame.display.update()
        clock.tick(15)


# Main Game Loop
def game_loop():
    global pause
    
    x = (display_width * 0.45)
    y = (display_height * 0.8)

    enemyCar_startx = random.randrange(0, display_width)
    enemyCar_starty = -600
    enemyCar_speed = 9
    
    dodged = 0

    # Game Logic
    gameExit = False

    while not gameExit:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        if keys[pygame.K_LEFT]:
            x -= 13
        if keys[pygame.K_RIGHT]:
            x += 13
        if keys[pygame.K_p]:
            pause = True
            paused()
        if keys[pygame.K_q]:
            sys.exit()


        gameDisplay.fill(black)         


        #enemyx, enemyy
        enemy_car_display = gameDisplay.blit(enemy_car, (enemyCar_startx, enemyCar_starty))
        enemyCar_starty += enemyCar_speed
        gameDisplay.blit(car_display,(x,y))
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
sys.exit()
