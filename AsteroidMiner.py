# Code adapted from KidsCanCode Shmup by Danielle Raven Ironwing 2018
# Feel free to use or edit this code for your own use as long as your credit my work.
# Artwork by Danielle Raven Ironwing and Kenny on OpenGameArt
# Music from OpenGameArt

import pygame
import pickle
import random
import time
import math
import eztext
import os
import natsort
from os import path
import fractions
import sys

FPS = 30
PLAYER_SIZEX = 85
PLAYER_SIZEY = 65
THRUST_DIV = 7
BULLET_SPEED = 45
max_mobs = 24

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)



# initialize pygame and create window
pygame.mixer.pre_init(44100, -16, 1, 512) #sets the buffer size so there is no delay in palying sounds
pygame.init()
pygame.mixer.init()
pygame.joystick.init()  # Initializes all joysticks/controllers
os.environ['SDL_VIDEO_CENTERED'] = '1'
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
infoObject = pygame.display.Info() #creates an info object to detect native screen resolution.
WIDTH = 960
HEIGHT = 540
flags = pygame.SCALED | pygame.RESIZABLE | pygame.FULLSCREEN
screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
pygame.display.set_caption("Asteroid Miner!")
clock = pygame.time.Clock()
pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0)) #sets cursor to an invisible cursor keeping the program free to receive mouse commands if needed in the future.

# set up assets (art and sound) folders
game_folder = path.dirname(__file__) #finds the location of the game file
img_folder = path.join(game_folder, "img") #finds image folder in game folder
sound_folder = path.join(game_folder, "sounds")

high_scores = dict()
if os.path.exists(path.join(game_folder, "scores.pkl")):
    with open(path.join(game_folder, "scores.pkl"), "rb", -1) as FILE:
        high_scores=pickle.load(FILE)
else:
    with open(path.join(game_folder, "scores.pkl"), "wb", -1) as FILE:
        pickle.dump(high_scores, FILE)

font_name = pygame.font.match_font('arial') #python looks for closest match to arial on whatever computer

def pause():
    draw_text(screen, "PAUSED", 64, WIDTH / 2, HEIGHT / 3)
    draw_text(screen, "Press SPACE to continue.", 24, WIDTH / 2, HEIGHT / 2)
    pygame.display.flip()
    time.sleep(1)
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN: 
                paused = False
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button in [0, 1, 2, 3, 6, 7, 8, 9, 10]:
                    paused = False
                elif event.button in [8, 10]:
                    pygame.quit()

def gravity(obj1, obj2, scale = 3):
    distance = math.sqrt((obj1.rect.centerx - obj2.rect.centerx)**2 + (obj1.rect.centery - obj2.rect.centery)**2)
    if distance == 0:
        distance = 1
    gforce = int(scale * obj1.size * obj2.size / distance**2)
    if obj1.rect.centery > obj2.rect.centery:
        obj1.rect.y -= gforce
    if obj1.rect.centery < obj2.rect.centery:
        obj1.rect.y += gforce
    if obj1.rect.centerx > obj2.rect.centerx:
        obj1.rect.x -= gforce
    if obj1.rect.centerx < obj2.rect.centerx:
        obj1.rect.x += gforce     

def show_go_screen(surf):
    draw_text(surf, "GAME OVER!", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(surf, "Your Score:" + str(player.score), 22, WIDTH / 2, HEIGHT / 2)
    draw_text(surf, "Press a key to continue.", 14, WIDTH / 2, HEIGHT * 3/4)
    pygame.display.flip()
    time.sleep(2)
    waiting = True
    while waiting:
        clock.tick(FPS)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP: #Use keyup instead of keydown so player won't be moving for shooting as soon as you play.
                waiting = False
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button in [0, 1, 2, 3, 6, 7, 8, 9, 10]:
                    waiting = False
                elif event.button in [8, 10]:
                    pygame.quit()

    text = eztext.Input(maxlength=45, color=(WHITE), prompt='Enter your name: ')

    waiting = True
    while waiting:
        # make sure the program is running at 30 fps
        clock.tick(FPS)
        
        # events for txtbx
        events = pygame.event.get()

        # process other events
        for event in events:
            # close it x button is pressed
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button in [0, 1, 2, 3, 6, 7, 8, 9, 10]:
                    if text.value == "":
                        continue
                    else:
                        waiting = False
                        text.value = text.value.strip()
                elif event.button in [8, 10]:
                    pygame.quit()
                    sys.exit()
        
        # clear the screen
        screen.fill((BLACK))
        # update txtbx
        text.update(events)
        # blit txtbx on the sceen
        text.draw(screen)
        # refresh the display
        pygame.display.flip()

        keystate = pygame.key.get_pressed() #gets all keys that are being pressed
        if keystate[pygame.K_RETURN]:
            if text.value == "":
                continue
            else:
                waiting = False
                text.value = text.value.strip()
        if keystate[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()

    #Saves Scores
    if high_scores.get(text.value, 1) == 1: #makes sure there isn't an existing entry with the players name to avoid overwriting.
        high_scores[text.value] = player.score
    if high_scores[text.value] < player.score:
        high_scores[text.value] = player.score
    with open(path.join(game_folder, "scores.pkl"), "wb", -1) as FILE:
        pickle.dump(high_scores, FILE)

    #Sorts Scores
    score_list=[]
    for k,v in high_scores.items():
        score_list.append(str(v)+"|"+k)
    score_list = natsort.natsorted(score_list, reverse = True)
    new_list=[]
    for x in score_list.copy():
        temp_split=x.split("|")
        new_list.append(temp_split[1]+":  "+temp_split[0])
    score_list=new_list
    del new_list

    screen.fill((BLACK))
    draw_text(screen, "High Scores:", 64, WIDTH / 2, 10)

    i=0
    scores_to_show = len(score_list)
    if scores_to_show > 20:
        scores_to_show = 20
    while i < scores_to_show:
        draw_text(screen, str(score_list[i]), 25, WIDTH / 2, 100 + 27*i)      
        i+=1
    
    draw_text(screen, "Press a key to play again.", 14, WIDTH / 2, HEIGHT - 25)
    pygame.display.flip()
    time.sleep(2)
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
               pygame.quit()
               sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button in [0, 1, 2, 3, 6, 7, 8, 9, 10]:
                    waiting = False
                elif event.button in [8, 10]:
                    pygame.quit()
                    sys.exit()
                
def show_start_screen(surf):
    draw_text(screen, "Asteroid Miner", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "Escape - quit, arrows - move, P - Pause, Lshift - fire, Z - bombs.", 22, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "Press a key to begin", 14, WIDTH / 2, HEIGHT * 3/4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button in [0, 1, 2, 3, 6, 7, 8, 9, 10]:
                    waiting = False
                elif event.button in [8, 10]:
                    pygame.quit()
                    sys.exit()
    


def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 40 * i
        img_rect.y = y
        surf.blit(img, img_rect)

def draw_status_bar(surf, x, y, pct, max_value = 100, color = GREEN):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT= 10
    fill = (pct / max_value) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, color, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2) #2 is how wide the rect is.

def draw_text(surf, text, size, x, y, color = WHITE):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color) #True tells whether or not text is anti-aliased (smothed) or not
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y) #midtop centers the text xy at the middle top of the text
    surf.blit(text_surface, text_rect)

def spawn_newmobs(split=0, x = 0, y = 0, size=0, speedx=0, speedy=0):
        if len(mobs.sprites()) > max_mobs:
            return
        m = Mob(split, x, y, size, speedx, speedy)
        all_sprites.add(m)
        mobs.add(m)
    

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        self.num_joysticks = len(self.joysticks)
        self.score = 0
        self.image = pygame.transform.scale(player_img, (PLAYER_SIZEX, PLAYER_SIZEY)) #scales image
        self.image.set_colorkey(BLACK) #makes black transparent
        self.rect = self.image.get_rect()  #defines the outside boundaries of the player sprite
        self.radius = PLAYER_SIZEX / 2.5
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.speedy = 0
        self.max_hp = 100
        self.hp = 100
        self.shield_power = 0
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.damaged = False
        self.lives = 2
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()
        self.size = 150
        self.thrust = 3
        self.energy = 100
      
   
    def update(self):       #creates an update module to be called in update part of loop
        #Rechanges gun energy
        
        now = pygame.time.get_ticks()
        if (now - self.last_shot > 100000 / player.hp):
            self.energy += 5
            if self.energy > 100:
                self.energy = 100
            self.last_shot = now

        #Makes you lose fire power if you run out of energy
        if self.energy == 0 and self.power > 1:
            self.power -= 1
            if self.power < 1:
                self.power = 1
            self.energy = 10               
        
        #unhide if hidden
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.image = pygame.transform.scale(player_img, (PLAYER_SIZEX, PLAYER_SIZEY)) #resets damaged ship to new
            self.image.set_colorkey(BLACK) #makes black transparent
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10
            self.damaged = False
        self.shoot_delay = 25000 / self.hp #makes it so you fire slower when you get damaged
        if self.shoot_delay > 800:
            self.shoot_delay = 800
        self.speedx = 0 #always sitting still unless key is pressed down
        self.speedy = 0
        self.thrust = int(self.hp / THRUST_DIV)
        if self.thrust < 1:
            self.thrust = 1
        keystate = pygame.key.get_pressed() #gets all keys that are being pressed
        if self.hidden == False: # doesn't let you move if you are dead
            # gets state of hat for moving blocks.
            # gets state of hat for moving blocks.
            if self.num_joysticks > 0:
                stick = self.joysticks[0]
                hat_state = stick.get_hat(0)
                self.speedx += hat_state[0] * self.thrust
                self.speedy += hat_state[1] * -self.thrust
                stick_x = stick.get_axis(0)
                stick_y = stick.get_axis(1)
                deadzone = 0.2
                if abs(stick_x) > deadzone:
                    self.speedx += stick_x * self.thrust * 1.2
                if abs(stick_y) > deadzone:
                    self.speedy += stick_y * self.thrust * 1.2
                if self.joysticks[0].get_button(0):
                    self.shoot()
                if self.joysticks[0].get_button(1):
                    self.bombs()

            if keystate[pygame.K_LEFT]:
                self.speedx =-self.thrust
            if keystate[pygame.K_RIGHT]:
                self.speedx = self.thrust
            self.rect.x += self.speedx
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH
            if self.rect.left < 0:
                self.rect.left = 0
            if keystate[pygame.K_UP]:
                self.speedy =-self.thrust
            if keystate[pygame.K_DOWN]:
                self.speedy = self.thrust
            self.rect.y += self.speedy
            if self.rect.bottom > HEIGHT:
                self.rect.bottom = HEIGHT
            if self.rect.top < 0:
                self.rect.top = 0
            if keystate[pygame.K_z]:
                self.bombs()
            if keystate[pygame.K_LSHIFT]:
                self.shoot()

        if self.hp < 90 and self.damaged == False:
                old_center = self.rect.center
                self.image = pygame.transform.scale(dplayer_images[int(self.hp / 15)], (PLAYER_SIZEX, PLAYER_SIZEY))
                self.rect = self.image.get_rect()
                #self.image.set_colorkey(BLACK) #makes black transparent
                self.rect.center = old_center
                self.damaged = True
                 

    def powerup(self, type = 1):
        if type == 1:
            if player.energy >= 70:
                self.power += 1
            player.energy += 50

        if type == 2:
            if player.energy >= 60:
                self.power += 2
            player.energy += 80

        if type == 3:
            if player.energy >= 50:
                self.power += 3
            player.energy += 100
                
        if self.power > 19:
            self.power = 19
            self.power_time = pygame.time.get_ticks()

        if player.energy > 100:
            player.energy = 100

    def shield_powerup(self):
        self.shield_power = int(len(shield_dots.sprites())/2)
        for dot in shield_dots:
            dot.kill()
        self.shield_power += 1
        if self.shield_power > 4:
            self.shield_power = 4
        self.hp = 100
        if len(shield_dots.sprites()) < 8:
            for i in range(self.shield_power):
                dot = Shield_Dots(20*i, - 80 + 3*i)
                all_sprites.add(dot)
                bullets.add(dot)
                player_bullets.add(dot)
                shield_dots.add(dot)
                dot = Shield_Dots(-20*i, - 80 + 3*i)
                all_sprites.add(dot)
                bullets.add(dot)
                player_bullets.add(dot)
                shield_dots.add(dot)

    def death(self):
        global death_explosion
        death_explosion = Explosion(self.rect.center, 'player')
        player_die_sound.play()
        all_sprites.add(death_explosion)
        self.power = 1
        self.hide()
        self.lives -= 1
        self.hp = 100
        self.shield_power = 0
        for dot in shield_dots:
            dot.kill()
    
            
    def shoot(self):
        now = pygame.time.get_ticks()
        if (now - self.last_shot > self.shoot_delay) and self.energy > 0:
            self.last_shot = now
            shoot_sound.play()
            for i in range(self.power):
                self.energy -= 1
                if self.energy < 0:
                    self.energy = 0
                if self.power > 1:
                    bullet = Bullets(self.rect.centerx, self.rect.top, self.speedx, self.speedy, int(-BULLET_SPEED * math.sin(math.radians(i * 10))), int(-BULLET_SPEED * math.cos(math.radians(i * 10))), i * 10)
                    all_sprites.add(bullet)
                    bullets.add(bullet)
                    player_bullets.add(bullet)
                bullet = Bullets(self.rect.centerx, self.rect.top, self.speedx, self.speedy, int(BULLET_SPEED * math.sin(math.radians(i * 10))), int(-BULLET_SPEED * math.cos(math.radians(i * 10))), -i * 10)
                all_sprites.add(bullet)
                bullets.add(bullet)
                player_bullets.add(bullet)
                
                """
                bullet = Bullets(self.rect.centerx + (i + 1), self.rect.top, self.speedx + i, self.speedy + random.randrange(0, 4))
                all_sprites.add(bullet)
                bullets.add(bullet)
                bullet = Bullets(self.rect.centerx - (i + 1), self.rect.top, self.speedx - i, self.speedy + random.randrange(0, 4))
                all_sprites.add(bullet)
                bullets.add(bullet)
                player_bullets.add(bullet)
                """
    def bombs(self):
        now = pygame.time.get_ticks()
        if (now - self.last_shot > self.shoot_delay) and self.energy > 0:
            self.last_shot = now
            shoot_sound.play()
            bomb = Bombs(self.rect.centerx, self.rect.top + self.speedy - 20, self.speedx, self.speedy)
            all_sprites.add(bomb)
            bombs.add(bomb)
            bullets.add(bomb)
            player_bullets.add(bomb)
            player.energy -= 5
            if player.energy < 0:
                player.energy = 0


    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH * 2, HEIGHT + 500)

class Shield_Dots(pygame.sprite.Sprite):
    def __init__(self, xdist, ydist):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(shield_dot_img, (18, 18)) #scales image
        self.image.set_colorkey(BLACK) #makes black transparent
        self.rect = self.image.get_rect()
        self.xdist = xdist
        self.ydist = ydist
        self.rect.centerx = player.rect.centerx + self.xdist
        self.rect.centery = player.rect.centery + self.ydist
        self.damage = 20

    def update(self):
        self.rect.centerx = player.rect.centerx + self.xdist
        self.rect.centery = player.rect.centery + self.ydist

class Alien(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = 50
        self.image = pygame.transform.scale(enemy_images[5], (self.size + 20, self.size)) #scales image
        self.image.set_colorkey(BLACK) #makes black transparent
        self.rect = self.image.get_rect()
        self.radius =int(self.rect.width / 2)
        self.rect.x = random.randrange(WIDTH * .85 - self.rect.width)     #makes the Mob apear at a random x value within the screen width
        self.rect.y = - 2 * self.size #sets a random y coordinate for the Mobs
        self.last_goodx = self.rect.centerx
        self.last_goody = self.rect.centery
        self.speedx = 4
        self.speedy = 4
        self.maxspeed = 4
        self.max_hp = 100
        self.hp = 100
        self.directionx = 0
        self.directiony = 2
        self.directionx = random.randrange(1, 2)
        self.last_update = pygame.time.get_ticks()
        self.damaged = False

    def shoot(self):
        alien_bullet = AlienBullets(self.rect.centerx - 7, self.rect.bottom, self.speedx, self.speedy)
        all_sprites.add(alien_bullet)
        bullets.add(alien_bullet)
        alien_bullets.add(alien_bullet)
        alien_bullet = AlienBullets(self.rect.centerx + 7, self.rect.bottom, self.speedx, self.speedy)
        all_sprites.add(alien_bullet)
        bullets.add(alien_bullet)
        alien_bullets.add(alien_bullet)
        
    def update(self):
        self.speedx = (self.hp / self.max_hp) * self.maxspeed
        if self.speedx < 1:
            self.speedx = 1
        self.speedy = (self.hp / self.max_hp) * self.maxspeed
        if self.speedy < 1:
            self.speedy = 1           

        now = pygame.time.get_ticks()
        if now - self.last_update > 200:
            #if random.randrange(80) == 1:
             #   self.shoot()
              #  self.last_update = now

            if self.rect.centerx in range(int(player.rect.centerx - (self.speedx + player.speedx)), int(player.rect.centerx + (self.speedx + player.speedx))):
                if self.rect.centery < player.rect.centery:
                    self.shoot()
                    self.last_update = now

            for mob in mobs:
                if self.rect.centerx in range(int(mob.rect.centerx - (self.speedx + mob.speedx)), int(mob.rect.centerx + (self.speedx + mob.speedx))):
                    if self.rect.centery < mob.rect.centery:
                        self.shoot()
                        self.last_update = now
                
        #Makes aliens avoid bullets
        evade = False
        for bullet in bullets:
            if self.rect.centerx in range(int(bullet.rect.centerx - 250), int(bullet.rect.centerx + 250)):
                evade = True
            else:
                evade = False
        #Makes aliens follow you when you aren't shooting at them        
        if evade == False and self.rect.centerx not in range(int(player.rect.centerx - random.randrange(60, 400)), int(player.rect.centerx + random.randrange(60, 400))):
            if player.rect.centerx > self.rect.centerx:
                self.directionx = 1
            if player.rect.centerx < self.rect.centerx:
                self.directionx = 2
              
        if self.directionx == 1:
            self.speedx = abs(self.speedx)
        if self.directionx == 2:
            self.speedx = -abs(self.speedx)
        if self.rect.right > WIDTH:
            self.directionx = 2
        if self.rect.left < 0:
            self.directionx = 1
        if self.directiony == 1:
            self.speedy = -abs(self.speedy)
        if self.directiony == 2:
            self.speedy = abs(self.speedy)
        if self.rect.y < 0:
            self.directiony = 2
        if random.randrange(1, 500) == 1:
            if self.rect.y > player.rect.y - 100:
                self.directiony = 1
        else: 
            if self.rect.y > HEIGHT - random.randrange(1, 400):
                self.directiony = 1
        lastx = self.rect.x
        lasty = self.rect.y
        self.rect.x += self.speedx 
        self.rect.y += self.speedy

        #makes aliens so they can't occupy the same space.
        if len(aliens.sprites()) > 1:
            aliens.remove(self)
            hits = pygame.sprite.spritecollide(self, aliens, False) 
            for hit in hits:
                if self.rect.y < 0: #makes it so aliens can't spawn on top of each other.
                    hit.kill()
                else:
                    self.rect.x = lastx
                    self.rect.y = lasty
                    self.directionx +=1
                    if self.directionx > 2:
                        self.directionx = 1
                    self.directiony +=1
                    if self.directiony > 2:
                        self.directiony = 1
            aliens.add(self)

        #Makes Alien look damaged when damaged.
        if self.hp < 90 and self.damaged == False:
                old_center = self.rect.center
                self.image = pygame.transform.scale(enemy_images[int(self.hp / 15)], (self.size + 20, self.size))
                self.rect = self.image.get_rect()
                self.rect.center = old_center
                self.damaged = True

    def death(self):
        global alien_expl
        alien_expl = Explosion(self.rect.center, 'player')
        all_sprites.add(alien_expl)
        player_die_sound.play()
        global alien_dead
        alien_dead = True
        global pow
        pow = Pow(self.rect.center)
        powerups.add(pow)
        all_sprites.add(powerups)
        global last_hit_score
        last_hit_score = self.max_hp * 10
        player.score += last_hit_score
        global last_hitx
        last_hitx = self.rect.centerx
        global last_hity
        last_hity = self.rect.centery
        self.kill()


class Alien_Mothership(Alien):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = 100
        self.image = pygame.transform.scale(enemy_images[5], (self.size + 20, self.size)) #scales image
        self.image.set_colorkey(BLACK) #makes black transparent
        self.rect = self.image.get_rect()
        self.radius =int(self.rect.width / 2)
        self.rect.x = random.randrange(WIDTH * .85 - self.rect.width)     #makes the Mob apear at a random x value within the screen width
        self.rect.y = - 2 * self.size #sets a random y coordinate for the Mobs
        self.last_goodx = self.rect.centerx
        self.last_goody = self.rect.centery
        self.speedx = 3
        self.speedy = 3
        self.maxspeed = 3
        self.max_hp = 300
        self.hp = 300
        self.directionx = 0
        self.directiony = 2
        self.directionx = random.randrange(1, 2)
        self.last_update = pygame.time.get_ticks()
        self.damaged = False

class Small_Alien(Alien):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = 35
        self.image = pygame.transform.scale(enemy_images[5], (self.size + 20, self.size)) #scales image
        self.image.set_colorkey(BLACK) #makes black transparent
        self.rect = self.image.get_rect()
        self.radius =int(self.rect.width / 2)
        self.rect.x = random.randrange(WIDTH * .85 - self.rect.width)     #makes the Mob apear at a random x value within the screen width
        self.rect.y = - 2 * self.size #sets a random y coordinate for the Mobs
        self.last_goodx = self.rect.centerx
        self.last_goody = self.rect.centery
        self.speedx = 5
        self.speedy = 5
        self.maxspeed = 5
        self.max_hp = 50
        self.hp = 50
        self.directionx = 0
        self.directiony = 2
        self.directionx = random.randrange(1, 2)
        self.last_update = pygame.time.get_ticks()
        self.damaged = False

class AlienBullets(pygame.sprite.Sprite):
    def __init__(self, x, y, xspeed, yspeed):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(alien_bullet_img, (15, 40)) #scales image
        self.image.set_colorkey(BLACK) #makes black transparent
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = BULLET_SPEED + yspeed
        self.speedx = xspeed
        self.damage = alien.hp / 8

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        #kill if it moves off the top of the screen
        if self.rect.top > HEIGHT:
            self.kill()
                
        
        
class Mob(pygame.sprite.Sprite):
    def __init__(self, split=0, x=0, y=0, size = 0, speedx=0, speedy=0):
        pygame.sprite.Sprite.__init__(self)
        
        if split == 0:
            self.size = random.randrange(15, 100)
            self.sizey = random.randrange(0, 30)
            self.image_orig = pygame.transform.scale(random.choice(meteor_images), (self.size, self.size+self.sizey)) #scales image
            self.image_orig.set_colorkey(BLACK) #makes black transparent
            self.image = self.image_orig.copy()
            self.rect = self.image.get_rect()
            self.radius = int(self.rect.width / 2)
            #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
            self.rect.x = random.randrange(int(WIDTH * .85 - self.rect.width))     #makes the Mob apear at a random x value within the screen width
            self.rect.y = random.randrange(-1500, -100) #sets a random y coordinate for the Mobs
        if speedx == 0:
            self.speedx = random.randrange(-3, 3)
        else:
            self.speedx = speedx
        if speedy == 0:
            self.speedy = random.randrange(1, 8) #sets random speed for mobs
        else:
            self.speedy = speedy
        if split == 1:
            self.size = int(size / 2)
            self.image_orig = pygame.transform.scale(random.choice(meteor_images), (self.size, self.size)) #scales image
            self.image_orig.set_colorkey(BLACK) #makes black transparent
            self.image = self.image_orig.copy()
            self.rect = self.image.get_rect()
            self.radius = int(self.rect.width / 2)
            self.rect.x = x
            self.rect.y = y
            self.speedx = speedx
            self.speedy = speedy
            
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

       
    def update(self):
        if self.speedy == 0:
            self.speedy = 1
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        #if a mob goes off the screen
        if self.rect.top > HEIGHT + 20 or self.rect.left < -35 or self.rect.right > WIDTH + 35:
            if len(mobs.sprites()) > max_mobs / 2:
                self.kill()
            if self.size < 20:
                self.kill()
                spawn_newmobs()
            self.rect.x = random.randrange(WIDTH - self.rect.width)     #makes the Mob apear at a random x value within the screen width
            self.rect.y = random.randrange(-100, -40) #sets a random y coordinate for the Mobs
            self.speedy = random.randrange(1, 8) #sets random speed for mobs
            self.rotation = random.randrange(-8, 8) #sets random rotation speed

class Black_Hole(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = random.randrange(int(WIDTH/3.2), int(WIDTH/2))
        self.orig_size = self.size
        self.image = pygame.transform.scale((black_hole_img), (self.size, self.size)) #scales image
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width / 2)
        self.rect.center = (random.randrange(0, WIDTH), 0)     #makes the black hole apear at a random x value within the screen width
        #self.rect.y = -self.size #sets a random y coordinate for the black hole
        self.speedy = random.randrange(1, 2)
        self.speedx = random.randrange(-1, 1)
        self.hp = self.size / 7
         
    def update(self):
        gravity(player, self)
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        #kill if it moves off the bottom of the screen
        if self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

        for mob in mobs:
            gravity(mob, self)
        for alien in aliens:
            gravity(alien, self)
        for bomb in bombs:
            gravity(bomb, self)

    def update_size(self):
        center = self.rect.center
        self.image = pygame.transform.scale((black_hole_img), (self.size, self.size)) #scales image
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width / 2)
        self.rect.center = center

class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun', 'none']) #makes lives less common
        if self.type == 'none':
           self.type = random.choice(['shield', 'gun', 'gun2', 'none'])
           if self.type == 'none':
               self.type = random.choice(['shield', 'gun', 'gun2', 'life', 'gun3'])    
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK) #makes black transparent
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 5
 

    def update(self):
        self.rect.y += self.speedy
        #kill if it moves off the bottom of the screen
        if self.rect.top > HEIGHT:
            self.kill()

class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y, xspeed, yspeed, bulletx_speed = 0, bullety_speed = -BULLET_SPEED, angle = 0):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.rotate(pygame.transform.scale(bullet_img, (int(player.hp / 15 + 10), int(player.hp / 6 + 18))), angle)
        #self.image = pygame.transform.scale(bullet_img, (int(player.hp / 15 + 10), int(player.hp / 6 + 18))) #scales image
        self.image.set_colorkey(BLACK) #makes black transparent
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = bullety_speed + yspeed
        self.speedx = bulletx_speed + xspeed
        self.damage = player.hp / 8

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        #kill if it moves off the screen
        if self.rect.bottom < 0 or self.rect.top > HEIGHT or self.rect.right > WIDTH or self.rect.left < 0:
            self.kill()

class Bombs(pygame.sprite.Sprite):
    def __init__(self, x, y, xspeed, yspeed):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bomb_img, (20, 20))
        self.rect = self.image.get_rect()
        self.image.set_colorkey(BLACK)
        self.rect.centerx = x
        self.rect.centery = y
        self.speedx = xspeed
        self.speedy = yspeed
        if self.speedy > 0:
            self.speedy = 0
        self.damage = 50
        self.size = 25
        
    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.bottom < 0 or self.rect.top > HEIGHT or self.rect.right > WIDTH or self.rect.left < 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 75

    def update(self):
        now = pygame.time.get_ticks()
        if now -self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center
         
#Load all game graphics
background = pygame.image.load(path.join(img_folder, "starfield.png")).convert()
background_rect = background.get_rect()
enemy_images = []
enemy_list = ['enemyShip6.png','enemyShip5.png', 'enemyShip4.png', 'enemyShip3.png', 'enemyShip2.png', 'enemyShip1.png'] 
for img in enemy_list:
    enemy_images.append(pygame.image.load(path.join(img_folder, img)).convert_alpha())
for img in enemy_images:
    img.set_colorkey(BLACK)
black_hole_img = pygame.image.load(path.join(img_folder, "black_hole.png")).convert_alpha() #converts the image with alpha channel
player_img = pygame.image.load(path.join(img_folder, "player.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (35, 29))
player_mini_img.set_colorkey(BLACK)
dplayer_images = []
damagedPlayer_list = ['playerDamaged6.png','playerDamaged5.png', 'playerDamaged4.png', 'playerDamaged3.png', 'playerDamaged2.png', 'playerDamaged1.png'] 
for img in damagedPlayer_list:
    dplayer_images.append(pygame.image.load(path.join(img_folder, img)).convert())
for img in dplayer_images:
    img.set_colorkey(BLACK)
bullet_img = pygame.image.load(path.join(img_folder, "laserBlue.png")).convert()
bomb_img = pygame.image.load(path.join(img_folder, "bomb.png")).convert()
shield_dot_img = pygame.image.load(path.join(img_folder, "shield_dot.png")).convert()
alien_bullet_img = pygame.image.load(path.join(img_folder, "laserGreen.png")).convert()

meteor_images = []
#meteor_list = ['meteor1.png', 'meteor2.png', 'meteor3.png']
for i in range(6):
    filename = 'meteor{}.png'.format(i+1)
    img = pygame.image.load(path.join(img_folder, filename)).convert()
#    img.set_colorkey(BLACK)
    meteor_images.append(img)
    
#for img in meteor_list:
#    meteor_images.append(pygame.image.load(path.join(img_folder, img)).convert())

explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(8):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_folder, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_folder, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)
powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_folder, 'shield_gold.png')).convert()
powerup_images['gun'] = pygame.image.load(path.join(img_folder, 'bolt_gold.png')).convert()
powerup_images['gun2'] = pygame.image.load(path.join(img_folder, 'bolt_blue.png')).convert()
powerup_images['gun3'] = pygame.image.load(path.join(img_folder, 'bolt_red.png')).convert()
powerup_images['life'] = player_mini_img   
                         
#Load all game sounds
black_hole = pygame.mixer.Sound(path.join(sound_folder, "blackhole.ogg"))
shield_pow = pygame.mixer.Sound(path.join(sound_folder, "shield_pow.ogg"))
lazer_pow = pygame.mixer.Sound(path.join(sound_folder, "lazer_pow.ogg"))
life_pow = pygame.mixer.Sound(path.join(sound_folder, "life_pow.ogg"))
player_die_sound = pygame.mixer.Sound(path.join(sound_folder, "rumble1.ogg"))
shoot_sound = pygame.mixer.Sound(path.join(sound_folder, "laser.wav"))
hit_sound = pygame.mixer.Sound(path.join(sound_folder, "explode.wav"))
damage_sound = pygame.mixer.Sound(path.join(sound_folder, "hit.wav"))
pygame.mixer.music.load(path.join(sound_folder, "BlindShift.ogg"))
pygame.mixer.music.set_volume(0.4)



pygame.mixer.music.play(loops=-1)


# Game Loop
game_over = False
new_game = True
running = True
while running:
    keystate = pygame.key.get_pressed() #gets all keys that are being pressed
    if keystate[pygame.K_p]:
        pause()

    if keystate[pygame.K_ESCAPE]:
        pygame.quit()
        sys.exit()

    if new_game:
        new_game = False
        screen.blit(background, background_rect) #draws background on screen
        show_start_screen(screen)
        start_time = pygame.time.get_ticks()
        game_over = False
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        mobs_temp = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        alien_bullets = pygame.sprite.Group()
        player_bullets = pygame.sprite.Group()
        bombs = pygame.sprite.Group()
        bullets.add(player_bullets)
        bullets.add(alien_bullets)
        black_holes = pygame.sprite.Group()
        aliens = pygame.sprite.Group()
        alien_motherships = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        shield_dots = pygame.sprite.Group()
        player = Player()        #creates a player object
        all_sprites.add(player)     #adds player to all_sprites group  
        for i in range(8):
            m = Mob()
            all_sprites.add(m)
            mobs.add(m)
        last_hit_score = 0
        last_hitx = 0
        last_hity = 0
        deadbh = False
        alien_dead = False
        last_spawn = 0
    
    if game_over:
        screen.blit(background, background_rect) #draws background on screen
        show_go_screen(screen)
        start_time = pygame.time.get_ticks()
        game_over = False
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        mobs_temp = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        alien_bullets = pygame.sprite.Group()
        player_bullets = pygame.sprite.Group()
        bombs = pygame.sprite.Group()
        bullets.add(player_bullets)
        bullets.add(alien_bullets)
        black_holes = pygame.sprite.Group()
        aliens = pygame.sprite.Group()
        alien_motherships = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        shield_dots = pygame.sprite.Group()
        player = Player()        #creates a player object
        all_sprites.add(player)     #adds player to all_sprites group  
        for i in range(8):
            m = Mob()
            all_sprites.add(m)
            mobs.add(m)
        last_hit_score = 0
        last_hitx = 0
        last_hity = 0
        deadbh = False
        alien_dead = False
        last_spawn = 0
        
    # Keep running at the correct speed
    clock.tick(FPS)
    # Process input (events)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button in [7, 9]:
                pause()
            elif event.button in [6, 10]:
                pygame.quit()
                sys.exit()
        
    # Update
    all_sprites.update()

    # spawn black holes
    if random.randrange(0, 6000) == 1:
        if len(black_holes.sprites()) < 1:
            hole = Black_Hole()
            all_sprites.add(hole)
            black_holes.add(hole)
            black_hole.play()

    # spawn aliens
    now = pygame.time.get_ticks()
    if now - start_time > 15000: #Makes it so aliens don't spawn for the first 15 seconds.
        if now - last_spawn > 2000:
            if random.randrange(0, 2000) == 1:
                alien = Alien()
                all_sprites.add(alien)
                aliens.add(alien)
                last_spawn = pygame.time.get_ticks()

    # spawn aliens motherships
    now = pygame.time.get_ticks()
    if now - start_time > 200000:
        if len(aliens.sprites()) < 3:
            if len(alien_motherships.sprites()) < 1:
                start_time = pygame.time.get_ticks()
                alien = Alien_Mothership()
                all_sprites.add(alien)
                aliens.add(alien)
                alien_motherships.add(alien)
                for i in range(3):
                    alien = Small_Alien()
                    all_sprites.add(alien)
                    aliens.add(alien)

    # Checks to see if black holes hit mobs, the player, or an alien
    hits = pygame.sprite.groupcollide(black_holes, mobs, False, True, pygame.sprite.collide_circle_ratio(0.25))
    for hit in hits:    
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        spawn_newmobs()
    hits = pygame.sprite.spritecollide(player, black_holes, True, pygame.sprite.collide_circle_ratio(0.25))
    for hit in hits:    
        player.death()
    hits = pygame.sprite.groupcollide(aliens, black_holes, True, False, pygame.sprite.collide_circle_ratio(0.25))
    for hit in hits:
        hit.death()

    #Check to see if a bomb hit a black hole:
    hits = pygame.sprite.groupcollide(black_holes, bombs, False, True, pygame.sprite.collide_circle_ratio(0.25))
    for hit in hits:
        black_hole_death = Explosion(hit.rect.center, 'player')
        all_sprites.add(black_hole_death)
        player_die_sound.play()
        hit.hp -= 50
        hit.size = int(hit.size / 1.5)
        hit.update_size()
        if hit.hp < 1:
            deadbh = True
            last_hit_score = hit.orig_size * 20
            player.score += last_hit_score
            last_hitx = hit.rect.centerx
            last_hity = hit.rect.centery
            hit.kill()
            for i in range(10):
                spawn_newmobs (1, last_hitx + random.randrange(-30, 30), last_hity + random.randrange(-30, 30), random.randrange(20, 50), random.randrange(-5, 5), random.randrange(-5, 5))

    #Check to see if a bullet hit a black hole:
    hits = pygame.sprite.groupcollide(black_holes, bullets, False, True, pygame.sprite.collide_circle_ratio(0.25))
    for hit in hits:
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)

    #Check to see if a bullet hit an alien:
    for bullet in player_bullets:         
        hits = pygame.sprite.spritecollide(bullet, aliens, False)
        for hit in hits:
            hit_sound.play()
            hit.damaged = False
            expl = Explosion(hit.rect.center, 'sm')
            all_sprites.add(expl)
            hit.hp -= bullet.damage
            bullet.kill()
            if hit.hp <= 0:
                hit.death()

    #Check to see if a mob hit an alien:
    hits = pygame.sprite.groupcollide(aliens, mobs, False, True) 
    for hit in hits:
        hit_sound.play()
        hit.damaged = False
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        hit.hp -= mob.radius / 3
        if hit.hp <= 0:
            hit.death()
            spawn_newmobs()

    #Check to see if the player hit an alien
    hits = pygame.sprite.spritecollide(player, aliens, False, pygame.sprite.collide_circle_ratio(0.80)) #first true deltes mobs, second delets bullets
    for hit in hits:
        hit.hp = hit.hp / 1.3
        player.damaged = False
        expl = Explosion(player.rect.center, 'sm')
        hit_sound.play()
        all_sprites.add(expl)
        player.hp = player.hp / 1.3
        if player.hp < 1:
            player.death()
        if hit.hp < 1:
            hit.death()
            
        

    #check to see if a bullet hit a mob
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True) #first true deltes mobs, second delets bullets
    #spons new mobs if old ones are killed.
    for hit in hits:    
        last_hit_score = 50 - hit.radius
        player.score += last_hit_score
        last_hitx = hit.rect.x
        last_hity = hit.rect.y
        hit_sound.play()
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        #makes a powerup appear
        if hit.size <= 50:
            if random.random() > 0.88:
                pow = Pow(hit.rect.center)
                powerups.add(pow)
                all_sprites.add(powerups)
        if hit.size > 10:
            if len(mobs.sprites()) >= max_mobs:
                spawn_newmobs (1, last_hitx, last_hity, int(hit.size), hit.speedx, hit.speedy)
            elif len(mobs.sprites()) < max_mobs:
                speed_vector = math.sqrt((hit.speedx**2+(hit.speedy)**2)) #the magnitude of the mobs velocity
                speed1_vector_max = int(math.sqrt(2)*speed_vector)          #the maximum velocity of one of the 2 particles if KE is preserved
                if speed1_vector_max > 0:
                    speed1_vector =  random.randrange(0, speed1_vector_max)
                else:
                    speed1_vector = 0
                speed2_vector = int(math.sqrt(2*speed_vector**2 - speed1_vector**2)) #magnitude of velocity of 2nd particle
                if speed1_vector > 0:
                    xspeed_1 = random.randrange(0, speed1_vector)
                else:
                    xspeed_1 = 0
                yspeed_1 = abs(int(math.sqrt(speed1_vector**2 - xspeed_1**2)))
                if yspeed_1 == 0:
                    yspeed_1 = 1
                if speed2_vector > 0:
                    xspeed_2 = random.randrange(0, speed2_vector )
                else:
                    xspeed_2 = 0
                yspeed_2 = abs(int(math.sqrt(speed2_vector**2 - xspeed_2**2)))
                if yspeed_2 == 0:
                    yspeed_2 = 1


                #Correctly assigns direction of particle vectors
                xspeed_1 = abs(xspeed_1)
                xspeed_2 = abs(xspeed_2)
                if speed1_vector > speed2_vector:
                    if hit.speedx < 0:
                        xspeed_1 = -xspeed_1
                elif speed1_vector < speed2_vector:
                    if hit.speedx < 0:
                        xspeed_2 = -xspeed_2
                        
                elif speed1_vector == speed2_vector:
                    if yspeed_1 > yspeed_2:
                        if hit.speedx < 0:
                            xspeed_2 = -xspeed_2
                    else:
                        if hit.speedx < 0:
                            xspeed_1 = -xspeed_1
                if xspeed_1 == 0 and xspeed_2 == 0:
                    xspeed_1 = -1
                    xspeed_2 = 1
                            

                
                spawn_newmobs (1, last_hitx, last_hity + hit.radius, int(hit.size), xspeed_1, yspeed_1)
                spawn_newmobs (1, last_hitx, last_hity, int(hit.size), xspeed_2, yspeed_2)
        elif len(mobs.sprites()) <= int(max_mobs / 2) : #only spawns new mobs if there aren't more than the max
            spawn_newmobs()

    #check to see if the player gets a powerup
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'shield':
            shield_pow.play()
            player.damaged = False
            player.hp += random.randrange(10, 30)
            if player.hp >= 90:
                player.image = pygame.transform.scale(player_img, (PLAYER_SIZEX, PLAYER_SIZEY))
                player.image.set_colorkey(BLACK) #makes black transparent
            if player.hp > 100:
                player.shield_powerup()
        if hit.type == 'life':
            life_pow.play()
            player.lives += 1
            if player.lives > 5:
                player.lives = 5
                player.damaged = False
                player.hp += random.randrange(20, 40)
                if player.hp >= 90:
                    player.image = pygame.transform.scale(player_img, (PLAYER_SIZEX, PLAYER_SIZEY))
                    player.image.set_colorkey(BLACK) #makes black transparent
                if player.hp > 100:
                    player.hp = 100
                  
        if hit.type == 'gun':
            lazer_pow.play()
            player.powerup()

        if hit.type == 'gun2':
            lazer_pow.play()
            player.powerup(2)

        if hit.type == 'gun3':
            lazer_pow.play()
            player.powerup(3)
            
        
    #check to see if a mob hit the player
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)  #makes a list of hits; false controls whether or not a mob should be deleted if you hit it
    for hit in hits:
        damage_sound.play()
        player.hp -= hit.radius / 1.6
        if hit.size > 30:
            player.power -= 1
            if player.power < 1:
                player.power = 1
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        if len(mobs.sprites()) < max_mobs:
            spawn_newmobs()
        player.damaged = False
        if player.hp <= 0:
            player.death()

    #check to see if an alien bullet hit the player
    hits = pygame.sprite.spritecollide(player, alien_bullets, True, pygame.sprite.collide_circle)  #makes a list of hits; false controls whether or not a mob should be deleted if you hit it
    for hit in hits:
        damage_sound.play()
        player.hp -= hit.damage
        player.power -= 1
        if player.power < 1:
            player.power = 1
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        player.damaged = False
        if player.hp <= 0:
            player.death()

    #check to see if bomb hit the player
    hits = pygame.sprite.spritecollide(player, bombs, True, pygame.sprite.collide_circle)  #makes a list of hits; false controls whether or not a mob should be deleted if you hit it
    for hit in hits:
        damage_sound.play()
        player.hp -= hit.damage
        player.power -= 1
        if player.power < 1:
            player.power = 1
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        player.damaged = False
        if player.hp <= 0:
            player.death()

    #check to see if an alien bullet hit a shield dot
    hits = pygame.sprite.groupcollide(shield_dots, alien_bullets, True, True, pygame.sprite.collide_circle)  #makes a list of hits; false controls whether or not a mob should be deleted if you hit it
    for hit in hits:
        damage_sound.play()
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)

    #check to see if a mob hit another mob
    for mob in mobs:
        if mob.size > 30:
            mobs.remove(mob)
            hits = pygame.sprite.spritecollide(mob, mobs, True, pygame.sprite.collide_circle_ratio(0.9)) #True kills mob the first obj mob crashes into
            for hit in hits:
                #hit_sound.play()
                expl = Explosion(hit.rect.center, 'sm')
                all_sprites.add(expl)
                mob.kill()    #kills object mob and spawns 4 smaller mobs
                if abs(mob.size - hit.size) < 10: 
                    spawn_newmobs (1, hit.rect.x, hit.rect.y + hit.radius, int(hit.size), hit.speedx / 2 + mob.speedx / 2, hit.speedy / 2 + mob.speedy / 2)
                    spawn_newmobs (1, hit.rect.x + hit.radius, hit.rect.y, int(hit.size), random.randrange(-5, 5), random.randrange(0, 8))
                    spawn_newmobs (1, mob.rect.x, mob.rect.y - mob.radius, int(mob.size), mob.speedx + random.randrange(-1, 1), mob.speedy + random.randrange(0, 1))
                    spawn_newmobs (1, mob.rect.x - mob.radius, mob.rect.y, int(mob.size), random.randrange(-5, 5), random.randrange(0, 8))
                elif mob.size - hit.size < 0: #if the mob hit is bigger
                    spawn_newmobs (1, hit.rect.x, hit.rect.y, int(hit.size * 2*(4/5)), hit.speedx - int(mob.speedx / 4), hit.speedy - int(mob.speedy / 4))
                    spawn_newmobs (1, mob.rect.x, mob.rect.y - mob.radius, int(mob.size), mob.speedx + random.randrange(-1, 1), mob.speedy + random.randrange(0, 1))
                    spawn_newmobs (1, mob.rect.x - mob.radius, mob.rect.y, int(mob.size), random.randrange(-5, 5), random.randrange(0, 8))
                else: #if the mob is bigger than the one it hit
                    spawn_newmobs (1, mob.rect.x, mob.rect.y, int(mob.size * 2*(4/5)), mob.speedx - int(hit.speedx / 4), mob.speedy - int(hit.speedy / 4))
                    spawn_newmobs (1, hit.rect.x, hit.rect.y - hit.radius, int(hit.size), hit.speedx + random.randrange(-1, 1), hit.speedy + random.randrange(0, 1))
                    spawn_newmobs (1, hit.rect.x - hit.radius, hit.rect.y, int(hit.size), random.randrange(-5, 5), random.randrange(0, 8))
                    

            if mob.alive():
                mobs.add(mob)
                all_sprites.add(mob)
        

    #if the player died and the explosion has finished playing then end
    if player.lives == 0 and not death_explosion.alive():
        game_over = True
    
    
    # Draw / Render
    screen.fill(BLACK)
    screen.blit(background, background_rect) #draws background on screen
    all_sprites.draw(screen)
    draw_text(screen, "Score:" + str(player.score), 18, WIDTH / 2, 10)
    draw_text(screen, "Asteroids:" + str(len(mobs.sprites())), 18, WIDTH / 2, 30)
    if len(black_holes.sprites()) > 0:
        draw_text(screen, "Black Hole Detected!", 22, WIDTH / 2, 50, RED)
    if last_hit_score > 0:
        draw_text(screen, "+" + str(last_hit_score), 20, last_hitx, last_hity)   #prints the score added from the last hit near where the mob was.
    if deadbh == True and not black_hole_death.alive():
        draw_text(screen, "+" + str(last_hit_score), 20, last_hitx, last_hity)   #prints the score added from the last hit near where the mob was.
        deadbh = False
    if alien_dead == True and not alien_expl.alive():
        draw_text(screen, "+" + str(last_hit_score), 20, last_hitx, last_hity)   #prints the score added from the last hit near where the mob was.
        alien_dead = False
    draw_status_bar(screen, 5, 5, player.hp, player.max_hp)
    draw_status_bar(screen, 5, 20, player.energy, 100, BLUE)
    draw_lives(screen, WIDTH - 250, 5, player.lives, player_mini_img)
    for alien in aliens:
            draw_status_bar(screen, alien.rect.x, alien.rect.y - 15, alien.hp, alien.max_hp, RED)
    # flip display after drawing everything
    pygame.display.flip()




    
pygame.quit()

