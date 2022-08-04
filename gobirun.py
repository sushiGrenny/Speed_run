import pygame
import os
import pickle
import random
from pygame.draw import rect

from pygame.transform import scale

pygame.init()

screen_width = 800
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Gobi run")

#set framerate
clock = pygame.time.Clock()
FPS = 60

#define game variable
GRAVITY = 0.75
scroll_thresh = 200
bg_scroll = 0
screen_scroll = 0
rows = 20
columns = 150
Tile_size = 600// 20
Tile_types = 21
level = 0

#define player variable
moving_left = False
moving_right = False
shoot = False

#load images

#Tiles
img_list =[]
for x in range(Tile_types):
    img = pygame.image.load(f'img/tile/{x}.png').convert_alpha()
    img = pygame.transform.scale(img, (Tile_size, Tile_size))
    img_list.append(img)

#define colors
BG = (0,0,0)
RED = (255,0,0)

#background
bg_one = pygame.image.load('img/Back/Sprite-0001.PNG').convert_alpha()
bg_two = pygame.image.load('img/Back/Sprite-0002.PNG').convert_alpha()
bg_three = pygame.image.load('img/Back/Sprite-0003.PNG').convert_alpha()
bg_four = pygame.image.load('img/Back/Sprite-0004.PNG').convert_alpha()
bg_five = pygame.image.load('img/Back/Sprite-0005.PNG').convert_alpha()

def draw_BG():
    screen.fill(BG)
    pygame.draw.line(screen, RED, (0,440), (screen_width, 440))
    width = bg_one.get_width()
    for x in range(5):
        screen.blit(bg_one, ((x * width)- bg_scroll*0.6 ,0))
        screen.blit(bg_two, ((x * width)- bg_scroll*0.7,0))
        screen.blit(bg_three, ((x * width)- bg_scroll*1,0))
        screen.blit(bg_four, ((x * width)- bg_scroll*1.2, 0))
        screen.blit(bg_five, ((x * width)- bg_scroll*1.5,0))


class Soldier(pygame.sprite.Sprite):
    def __init__(self,char_type,x,y,scale,speed,ammo):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.shoot_cooldown = 0
        self.direction = 1 #looking right
        self.vel_y = 0
        self.jump = False
        self.in_air = False
        self.flip = False
        self.animation_list = []
        self.index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        #ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 350, 20)
        self.idling = False
        self.idling_counter = 0

        self.health = 100
        

        #load all images for the players
        animation_types = ['idle', 'run', 'shoot', 'jump', 'death',]
        for animation in animation_types:
			#reset temporary list of images
            temp_list = []
			#count number of files in the folder
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(1, num_of_frames+1):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/Sprite-000{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
    
    def update(self):
        self.update_animation()
        #update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        #movement variable
        screen_scroll = 0
        dx = 0
        dy = 0

        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        #hump
        if self.jump == True and self.in_air == False:
            self.vel_y = -15
            self.jump = False
            self.in_air = True

        #apply gravity   
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        #collison 
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx , self.rect.y , self.width, self.height):
                dx = 0
            if tile[1].colliderect(self.rect.x , self.rect.y + dy , self.width, self.height):
                dy = 0
                #check if below the ground, i.e. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
				#check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        #if self.rect.bottom + dy > 440:
            #dy = 440- self.rect.bottom
            #self.in_air = False
        
        #health_rect = pygame.Rect(self.rect.x-15, self.rect.y - 10, 70,10)
        #pygame.draw.rect(screen, RED, health_rect)

        #update rect pos
        self.rect.x += dx
        self.rect.y += dy
    

        #update scroll
        if self.char_type == 'player':
            if (self.rect.right > screen_width - scroll_thresh and bg_scroll < (world.level_length * Tile_size) - screen_width)\
				or (self.rect.left < scroll_thresh and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll

    def ai(self):
        if self.alive:
            if self.idling == False and random.randint(1, 1000) == 1:
                self.update_action(0)#0: idle
                #self.idling = True
                self.idling_counter = 0
            #check if the ai in near the player
            if self.vision.colliderect(player.rect):
                #stop running and face the player
                self.update_action(0)#0: idle
                #shoot
                self.shoot()
                self.idling = False


            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)#1: run
                    self.move_counter += 1
                    #update ai vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 175 * self.direction, self.rect.centery)

                    if self.move_counter > Tile_size*1.5:
                        self.direction *= -1
                        self.move_counter *= -1
                    #else:
                        #self.idling_counter -= 1
                        #if self.idling_counter < 0:
                            #self.idling = False
            
            self.rect.x += screen_scroll

    
    #def shoot(self):
        #if self.shoot_cooldown == 0 and self.ammo >0:
           # self.shoot_cooldown = 20
            #bullet = Bullet(self.rect.centerx + (0.6*self.rect.size[0]* self.direction), self.rect.centery, self.direction)
            #bullet_group.add(bullet)
            #reduce ammo
            #self.ammo -=1


    def update_animation(self):
        #update animation
        animation_cooldown = 100
        self.image = self.animation_list[self.action][self.index]
        #check if enough time passed
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.index += 1

        if self.index >= len(self.animation_list[self.action]):
            self.index = 0
        
    def update_action(self, new_action):
            if new_action != self.action:
                self.action = new_action

                self.index = 0
                self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class Demoney(pygame.sprite.Sprite):
    def __init__(self,char_type,x,y,scale,speed,ammo):
        pygame.sprite.Sprite.__init__(self)

        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.shoot_cooldown = 0
        self.direction = 1 #looking right
        self.vel_y = 0
        self.jump = False
        self.in_air = False
        self.flip = False
        self.animation_list = []
        self.index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        #ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 16, 30)
        self.idling = False
        self.idling_counter = 0
        
        #load all images for the players
        animation_types = ['idle', 'attack']
        for animation in animation_types:
			#reset temporary list of images
            temp_list = []
			#count number of files in the folder
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(1, num_of_frames+1):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/Sprite-000{i}.png')
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()

    def update_animation(self):
        #update animation
        animation_cooldown = 100
        self.image = self.animation_list[self.action][self.index]
        #check if enough time passed
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.index += 1

        if self.index >= len(self.animation_list[self.action]):
            self.index = 0
        
    def update_action(self, new_action):
            if new_action != self.action:
                self.action = new_action
                self.index = 0
                self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
    

    def move(self):
        dx = 0
        dy = 0

        #apply gravity   
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        #collison 
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx , self.rect.y , self.width, self.height):
                dx = 0
            if tile[1].colliderect(self.rect.x , self.rect.y + dy , self.width, self.height):
                dy = 0
                #check if below the ground, i.e. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
				#check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        if self.alive:
            if self.idling == False and random.randint(1, 1000) == 1:
                self.update_action(0)#0: idle
                #self.idling = True
                #self.idling_counter = 50
            #check if the ai in near the player
            if self.vision.colliderect(player.rect):
                #stop running and face the player
                self.update_action(1)#0: attack
                #shoot
                #self.shoot()
                #self.idling = True
                #self.idling_counter = 50

            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    
                    if ai_moving_left:
                        dx = -self.speed
                        self.flip = True
                        self.direction = -1
                    if ai_moving_right:
                        dx = self.speed
                        self.flip = False
                        self.direction = 1
                    
                    #self.rect.x += dx
                    #self.rect.y += dy 
                    
                    self.update_action(0)#1: run
                    self.move_counter += 1
                    #update ai vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 4 * self.direction, self.rect.centery)

                    if self.move_counter > Tile_size * 0.8:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling_counter = False

            self.rect.x += screen_scroll


class world():
    def __init__(self):
        self.obstacle_list = []
        self.decoration_list = []

    def process_data(self,data):
        self.level_length = len(data[0])

        for y,row in enumerate(data):
            for x,tile in enumerate(row):
                if tile >=0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * Tile_size
                    img_rect.y = y * Tile_size
                    tile_data = (img, img_rect)
                    if tile >=0 and tile <= 9:
                        self.obstacle_list.append(tile_data)
                    elif tile >=10 and tile <= 15:
                        self.decoration_list.append(tile_data)
                    elif tile == 16:
                        money = Demoney('money',x * Tile_size, y * Tile_size, 3, 2, 2000 )
                        money_group.add(money)
                    elif tile == 17:
                        money = Demoney('500',x * Tile_size, y * Tile_size, 2, 2, 2000 )
                        money_group.add(money)
                    elif tile == 18:
                        gst = GST(x * Tile_size, y * Tile_size, 1.9)
                        gst_group.add(gst)
                        #self.obstacle_list.append(tile_data)
                    elif tile == 19:
                        rail = Railway(x * Tile_size, y * Tile_size, 1.9)
                        rail_group.add(rail)
                    else:
                        self.obstacle_list.append(tile_data)
                 
                    
    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])
        for tile in self.decoration_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])

class GST(pygame.sprite.Sprite):
    def __init__(self,x,y,scale):
        pygame.sprite.Sprite.__init__(self)

        img = pygame.image.load('img/gst/Sprite-0001.png')
        img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.rect.x += screen_scroll

class Railway(pygame.sprite.Sprite):
    def __init__(self,x,y,scale):
        pygame.sprite.Sprite.__init__(self)

        img = pygame.image.load('img/rail/Sprite-0001.png')
        img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
    
    def update(self):
        self.rect.x += screen_scroll


player = Soldier('player',80,170,1.5,5,20)
#money = Demoney('money',180,170,3,5,20 )



money_group = pygame.sprite.Group()
gst_group = pygame.sprite.Group()
rail_group = pygame.sprite.Group()

#create empty tile list
world_data = []
for row in range(rows):
    r = [-1]*columns
    world_data.append(r)
#Load in level data
pickle_in = open(f'level/level{level}_data', 'rb')
world_data = pickle.load(pickle_in)
world = world()
world.process_data(world_data)



running = True
while running:

    clock.tick(FPS)

    #update background
    draw_BG()
    world.draw()

    #player.update()
    #player.draw()

    for money in money_group:
        money.move()
        money.update()
        money.draw()

    #update groups
    gst_group.update()
    gst_group.draw(screen)

    rail_group.update()
    rail_group.draw(screen)

    player.update()
    player.draw()

    if player.alive:
        #update action
        #if shoot:
           # player.update_action(2)
            #player.shoot()

        if moving_left or moving_right:
            player.update_action(1)

        else:
            player.update_action(0)
        screen_scroll = player.move(moving_left, moving_right)
        bg_scroll -= screen_scroll

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        #keyboard buttons
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False


    pygame.display.update()