
import pygame
import random
import sys

pygame.init()

Width = 800
Height = 600

orange = (255,165,0)
blue = (0,0,255)
bgcolor = (0,0,0)
yellow = (255,255,0)

player_size = 50
player_loc = [Width/2, Height-2*player_size]

op_size = 50
op_loc = [random.randint(0,Width-op_size), 0]
op_list = [op_loc]

speed = 11

screen = pygame.display.set_mode((Width, Height))
title = pygame.display.set_caption("Dodge The Blocks! by Arpan Neupane")

game_over = False

score = 0

clock = pygame.time.Clock()

Font = pygame.font.SysFont("agencyfb", 35)
Font2 = pygame.font.SysFont("agencyfb", 60)

def set_level(score, speed):
    if score < 20:
       speed = 5
    elif score < 40:
       speed = 8
    elif score < 60:
       speed = 12
    else:
       speed = 16
    return speed
    #speed = score / 5 + 1
    return speed

def drop_ops(op_list):
    delay = random.random()
    if len(op_list) < 10 and delay  < 0.1:
        x_loc = random.randint(0, Width-op_size)
        y_loc = 0
        op_list.append([x_loc, y_loc])

def draw_op(op_list):
    for op_loc in op_list:
        pygame.draw.rect(screen, orange, (op_loc[0], op_loc[1], op_size, op_size))

def update_op_loc(op_list, score):
    for idx, op_loc in enumerate(op_list):
        if op_loc[1] >= 0 and op_loc[1] < Height:
            op_loc[1] += speed
        else:
            op_list.pop(idx)
            score += 1
    return score

def collision_check(op_list, player_loc):
    for op_loc in op_list:
        if detect_op(op_loc, player_loc):
            return True
    return False

def detect_op(player_loc, op_loc):
    p_x = player_loc[0]
    p_y = player_loc[1]

    e_x = op_loc[0]
    e_y = op_loc[1]

    if (e_x >= p_x and e_x < (p_x + player_size)) or (p_x >= e_x and (p_x < e_x+op_size)):
        if (e_y >= p_y and e_y < (p_y + player_size)) or (p_y >= e_y and p_y < (e_y+op_size)):
            return True
    return False

while not game_over:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.KEYDOWN:

            x = player_loc[0]
            y = player_loc[1]

            if event.key == pygame.K_LEFT:
                x -= player_size
            elif event.key == pygame.K_RIGHT:
                x += player_size

            player_loc = [x,y]

    screen.fill(bgcolor)

    drop_ops(op_list)
    score = update_op_loc(op_list, score)
    speed = set_level(score, speed)


    text = "Score: " + str(score)
    label = Font.render(text, 1, yellow)
    screen.blit(label, (Width-200, Height-40))

    if collision_check(op_list, player_loc):
        game_over = True
        break

    draw_op(op_list)

    pygame.draw.rect(screen, blue, (player_loc[0], player_loc[1], player_size, player_size))

    clock.tick(36)

    pygame.display.update()