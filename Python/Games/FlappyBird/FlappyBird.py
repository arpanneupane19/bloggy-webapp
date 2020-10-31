import pygame
import random
import sys

pygame.mixer.pre_init(frequency = 44100, size = -16, channels = 1, buffer = 512)
pygame.init()

birdIcon = pygame.image.load('assets/bluebird-midflap.png')

width = 288
height = 512
win = pygame.display.set_mode((width, height))
pygame.display.set_caption('Flappy Bird')
pygame.display.set_icon(birdIcon)
clock = pygame.time.Clock()
gameFont = pygame.font.SysFont("agencyfb",40)

gravity = 0.25
birdMovement = 0
gameRunning = True
score = 0
highScore = 0

background = pygame.image.load('assets/background-night.png').convert()


ground = pygame.image.load('assets/base.png').convert()


groundX = 0

birdDownflap = pygame.image.load('assets/bluebird-downflap.png').convert_alpha()
birdDownflap = pygame.transform.scale2x(birdDownflap)
birdMidflap = pygame.image.load('assets/bluebird-midflap.png').convert_alpha()
birdMidflap = pygame.transform.scale2x(birdMidflap)
birdUpflap = pygame.image.load('assets/bluebird-upflap.png').convert_alpha()
birdUpflap = pygame.transform.scale2x(birdUpflap)


birdFrames = [birdDownflap, birdMidflap, birdUpflap]
birdIndex = 0
bird = birdFrames[birdIndex]
birdRect = bird.get_rect(center = (50, 256))

BIRDFLAP = pygame.USEREVENT + 1
pygame.time.set_timer(BIRDFLAP, 200)

pipeSurface = pygame.image.load('assets/pipe-green.png').convert()
pipeSurface = pygame.transform.scale2x(pipeSurface)

pipeList = [] 
spawnPipe = pygame.USEREVENT
pygame.time.set_timer(spawnPipe, 800)
pipeHeight = [356, 366, 376, 386,400]

gameOverFont = pygame.font.SysFont("agencyfb", 25)
gameOverText = gameOverFont.render("Game Over. Press space to play.", True, (255,255,255))
gameOverRect = gameOverText.get_rect(center = (144, 256))

flapSound = pygame.mixer.Sound('sound/sfx_wing.wav')
deathSound = pygame.mixer.Sound('sound/sfx_hit.wav')
scoreSound = pygame.mixer.Sound('sound/sfx_point.wav')
scoreSoundCountdown = 100

def drawGround():
    win.blit(ground, (groundX, 450))
    win.blit(ground, (groundX + 288, 450))


def createPipe():
    global topPipe
    global bottomPipe

    randomPipePos = random.choice(pipeHeight)
    bottomPipe = pipeSurface.get_rect(midtop = (350, randomPipePos))
    topPipe = pipeSurface.get_rect(midbottom = (350, randomPipePos - 300))
    return bottomPipe, topPipe


def movePipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 5
    return pipes



def drawPipe(pipes):
    for pipe in pipes:
        if pipe.bottom >= 512:
            win.blit(pipeSurface,pipe)
        else:
            flipPipe = pygame.transform.flip(pipeSurface, False, True)
            win.blit(flipPipe, pipe)




def collision(pipes):
    for pipe in pipes: 
        if birdRect.colliderect(pipe):
            deathSound.play()
            return False
    
    if birdRect.top <= 0 or birdRect.bottom >= 450:
        deathSound.play()
        return False
    
    return True

def rotateBird(bird):
    newBird = pygame.transform.rotozoom(bird, -birdMovement * 3, 1)
    return newBird


def birdAnimation():
    newBird = birdFrames[birdIndex]
    newBirdRect = newBird.get_rect(center = (50, birdRect.centery))
    return newBird, newBirdRect

def displayScore(gameState):
    if gameState == "game running":
        scoreSurface = gameFont.render(str(int(score)), True, (255,255,255))
        scoreRect = scoreSurface.get_rect(center = (144, 50))
        win.blit(scoreSurface, scoreRect)
    if gameState == "game over":
        scoreSurface = gameFont.render(f'Score: {int(score)}', True, (255,255,255))
        scoreRect = scoreSurface.get_rect(center = (144, 50))
        win.blit(scoreSurface, scoreRect)

        highScoreSurface = gameFont.render(f'High Score: {int(highScore)}', True, (255,255,255))
        highScoreRect = highScoreSurface.get_rect(center = (144, 425))
        win.blit(highScoreSurface, highScoreRect)


def updateScore(score, highScore):
    if score > highScore:
        highScore = score

    return highScore

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and gameRunning == True:
                birdMovement = 0
                birdMovement -= 7
                flapSound.play()
            if event.key == pygame.K_SPACE and gameRunning == False:
                gameRunning = True
                pipeList.clear()
                birdRect.center = (50, 256)
                birdMovement = 0
                score = 0
            if event.key == pygame.K_q:
                sys.exit()
            
        if event.type == spawnPipe:
            pipeList.extend(createPipe())

        if event.type == BIRDFLAP:
            if birdIndex < 2:
                birdIndex += 1
            else:
                birdIndex = 0

            bird, birdRect = birdAnimation()

    win.blit(background, (0,0))

    if gameRunning:
        # Bird
        birdMovement += gravity
        rotatedBird = rotateBird(bird)
        birdRect.centery += birdMovement
        win.blit(rotatedBird, birdRect)
        gameRunning = collision(pipeList)

        # Pipes
        pipeList = movePipes(pipeList) 
        drawPipe(pipeList)
        score += 0.01
        displayScore("game running")
        scoreSoundCountdown -= 1
        if scoreSoundCountdown <= 0:
            scoreSound.play()
            scoreSoundCountdown = 100

    else:
        win.blit(gameOverText, gameOverRect)
        highScore = updateScore(score, highScore)
        displayScore("game over")

    # Floor
    groundX -= 1
    drawGround()
    if groundX <= -288:
        groundX = 0

    pygame.display.update()
    clock.tick(100)
