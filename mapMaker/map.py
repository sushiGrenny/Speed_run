import pygame
import csv
import pickle

pygame.init()
caption = pygame.display.set_caption("Map-Maker 1.0")
clock = pygame.time.Clock()

D_width = 800
D_height = 600
D_margin = 280
D_bottom = 50
screen = pygame.display.set_mode((D_width + D_margin, D_height + D_bottom))

#variables

rows = 20
columns = 450
Tile_size = D_height// 20
Tile_types = 21
left_scroll = False
right_scroll =False
scroll = 0
scroll_speed = 1
current_tile = 0
level = 0

font = pygame.font.SysFont('Futura', 30)

#Tile list
world_data = []
for row in range(rows):
    r = [-1] * columns
    world_data.append(r)
#create gorund
for tile in range(0, columns):
    world_data[rows -1][tile] = 0

#TEXTS
def draw_text(text, font, colour, x,y ):
    img = font.render(text, True, colour)
    screen.blit(img, (x,y))



#background
bg_one = pygame.image.load('back/Sprite-0001.PNG').convert_alpha()
#bg_two = pygame.image.load('back/Sprite-0002.PNG').convert_alpha()
#bg_three = pygame.image.load('back/Sprite-0003.PNG').convert_alpha()
#bg_four = pygame.image.load('back/Sprite-0004.PNG').convert_alpha()
#bg_five = pygame.image.load('back/Sprite-0005.PNG').convert_alpha()
#Tiles
img_list =[]
for x in range(Tile_types):
    img = pygame.image.load(f'tile/{x}.png').convert_alpha()
    img = pygame.transform.scale(img, (Tile_size, Tile_size))
    img_list.append(img)
save_img = pygame.image.load('buttons/save_btn.png').convert_alpha()
load_img = pygame.image.load('buttons/load_btn.png').convert_alpha()


def bg_draw():
    width = bg_one.get_width()
    for x in range(5):
        screen.blit(bg_one, ((x * width)- scroll*0.5 ,0))
        #screen.blit(bg_two, ((x * width)- scroll*0.6,0))
        #screen.blit(bg_three, ((x * width)- scroll*0.7,0))
        #screen.blit(bg_four, ((x * width)- scroll*0.8, 0))
        #screen.blit(bg_five, ((x * width)- scroll,0.9))
        

def bg_scroll():
    global scroll  
    if left_scroll == True and scroll >0:
        scroll -= 10 * scroll_speed
    if right_scroll == True and (scroll < (columns * Tile_size)- D_width):
        scroll += 10 * scroll_speed

def draw_grid():
    #vertical grid
    for c in range(columns+1):
        pygame.draw.line(screen, (255,255,255),(c * Tile_size-scroll,0), (c* Tile_size-scroll, D_height))

    for c in range(rows+1):
        pygame.draw.line(screen, (255,255,255),(0, c*Tile_size), (D_width, c*Tile_size))



def draw_world():
    for y, row in enumerate(world_data):
        for x, tiles in enumerate(row):
            if tiles >=0:
                screen.blit(img_list[tiles],(x * Tile_size - scroll, y * Tile_size))



#button class
class Button():
	def __init__(self,x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action

#button list
button_list = []
button_col = 0
button_row = 0
for i in range(len(img_list)):
    tile_button = Button(D_width + (75*button_col)+50, 75*button_row+50, img_list[i], 1)
    button_list.append(tile_button)
    button_col += 1
    if button_col == 3:
        button_row += 1
        button_col = 0

save_button = Button(D_width//2 - 100, D_height + D_bottom - 40, save_img, 1)
load_button = Button(D_width//2 + 100, D_height + D_bottom - 40, load_img, 1)

def draw_buttons():
    global current_tile
    button_count = 0
    pygame.draw.rect(screen,(0,155,0), (D_width, 0, D_margin, D_height) )
    for button_count, i in enumerate(button_list):
         if i.draw(screen):
             current_tile = button_count

    #highlight the button
    pygame.draw.rect(screen, (155,0,0), button_list[current_tile].rect, 3)

    if save_button.draw(screen):
        #with open(f'level{level}_data.csv', 'w', newline= '')as csvfile:
         #   writer = csv.writer(csvfile, delimiter = ',')
          #  for row in world_data:
           #     writer.writerow(row)
        global world_data
        pickle_out = open(f'level{level}_data', 'wb')
        pickle.dump(world_data, pickle_out)
        pickle_out.close()

    if load_button.draw(screen):
        scroll = 0
        world_data = []
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
        #with open(f'level{level}_data.csv',  newline= '')as csvfile:
         #   reader = csv.reader(csvfile, delimiter = ',')
          #  for x, row in enumerate(reader):
           #     for y, tile in enumerate(row):
            #        world_data[x][y] = int(tile)

# adding tiles to screen
def tile_screen():
    pos = pygame.mouse.get_pos()
    x = (pos[0] + scroll)// Tile_size
    y = (pos[1])//Tile_size
        
    if pos[0] < D_width and pos[1] < D_height:
        if pygame.mouse.get_pressed()[0] == 1:
            if world_data[y][x] != current_tile:
                world_data[y][x] = current_tile
        if pygame.mouse.get_pressed()[2] == 1:
            world_data[y][x] = -1




running = True
while running:
    
    clock.tick(60)
    screen.fill((0,155,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                left_scroll = True
            if event.key == pygame.K_RIGHT:
                right_scroll = True
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 5
            if event.key == pygame.K_UP:
                level += 1
            if event.key == pygame.K_DOWN:
                if level > 0:
                    level -= 1

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                left_scroll = False
            if event.key == pygame.K_RIGHT:
                right_scroll = False
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 1





    bg_draw()
    #draw_grid()
    draw_world()
    draw_buttons()
    tile_screen()
    bg_scroll()
    draw_text(f'Level = {level}', font, (255,255,255), 10,D_height + D_bottom -30 )

    pygame.display.update()

        