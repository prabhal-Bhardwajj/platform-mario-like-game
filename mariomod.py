'''
So I decide to add few mods to the classic Mario Game ->
It includes features like health powerups, enemy spawning based on score intervals, and dynamic platform generation.
Below are detailed comments explaining each part of the code to help beginners understand how it works.
'''

import pygame
import sys
import random
from os import path
import math

'''
Initialize Pygame and Pygame's mixer (for sound effects). 
pygame.init() initializes all the Pygame modules, and pygame.mixer.init() initializes the mixer module for handling sounds.
'''
pygame.init()
pygame.mixer.init()

'''
Set up constants for the game window size, frames per second (FPS), gravity, jump power, player speed, coin spawn rate, maximum enemies, maximum platforms, and health powerup chance.
'''
WIDTH = 1100  
HEIGHT = 720  
FPS = 60  
GRAVITY = 0.8  
JUMP_POWER = -16  
PLAYER_SPEED = 8  
COIN_SPAWN_RATE = 3000  
MAX_ENEMIES = 10  
MAX_PLATFORMS = 15  
HEALTH_POWERUP_CHANCE = 0.2  
ENEMY_SPAWN_SCORE_INTERVAL = 500  

'''
Define some colors as RGB tuples for easy reference.
'''
WHITE = (255, 255, 255)  
BLACK = (0, 0, 0)  
RED = (255, 0, 0)  
GREEN = (0, 255, 0)  
BLUE = (0, 0, 255)  
YELLOW = (255, 255, 0)  
PINK = (255, 192, 203)  

'''
The HealthPowerup class represents a health powerup that bounces up and down.
It inherits from pygame.sprite.Sprite.
'''
class HealthPowerup(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))  
        self.image.fill(PINK)  
        self.rect = self.image.get_rect(center=(x, y))  
        self.bounce = 0  
    
    def update(self):
        '''
        Update the powerup's position to create a bouncing effect.
        '''
        self.bounce += 0.1
        self.rect.y += int(2 * math.sin(self.bounce))  

'''
The Player class represents the main character controlled by the player. 
It inherits from pygame.sprite.Sprite, which allows it to be easily managed in sprite groups.
'''
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        '''
        Create different sprites for the player's idle, running, and jumping animations.
        Each animation state has a list of surfaces (images) that will be cycled through to create the animation effect.
        '''
        self.sprites = {
            'idle': [pygame.Surface((32, 64)) for _ in range(2)],  
            'run': [pygame.Surface((32, 64)) for _ in range(4)],  
            'jump': pygame.Surface((32, 64))  
        }
        
        '''
        Fill the idle and run frames with blue color, and the jump frame with red color.
        '''
        for sprite in self.sprites['idle']:
            sprite.fill(BLUE)
        for sprite in self.sprites['run']:
            sprite.fill(BLUE)
        self.sprites['jump'].fill(RED)
        
        '''
        Variables to manage the animation frames and timing.
        '''
        self.current_frame = 0  
        self.last_update = 0  
        self.frame_rate = 100  
        self.image = self.sprites['idle'][0]  
        self.rect = self.image.get_rect()  
        self.rect.center = (WIDTH // 4, HEIGHT // 2)  
        
        '''
        Player movement variables.
        '''
        self.velocity_x = 0  
        self.velocity_y = 0  
        self.on_ground = False  
        self.facing_right = True  
        self.health = 100  
        self.score = 0  
        self.jumping = False  
    
    def update(self):
        '''
        Update the player's position, animations, and handle gravity.
        This method is called every frame to update the player's state.
        '''
        now = pygame.time.get_ticks()  
        self.velocity_y += GRAVITY  
        
        '''
        Update the player's animation based on their state (idle, running, or jumping).
        '''
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            if not self.on_ground:  
                self.image = self.sprites['jump']
            elif abs(self.velocity_x) > 0:  
                self.current_frame = (self.current_frame + 1) % len(self.sprites['run'])
                self.image = self.sprites['run'][self.current_frame]
            else:  
                self.current_frame = (self.current_frame + 1) % len(self.sprites['idle'])
                self.image = self.sprites['idle'][self.current_frame]
            
            '''
            Flip the image horizontally if the player is facing left.
            '''
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)
        
        '''
        Update the player's position based on their velocity.
        '''
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        '''
        Prevent the player from moving outside the screen boundaries.
        '''
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.on_ground = True  
            self.velocity_y = 0
            self.jumping = False  
    
    def jump(self):
        '''
        Make the player jump if they are on the ground and not already jumping.
        '''
        if self.on_ground and not self.jumping:
            self.velocity_y = JUMP_POWER  
            self.on_ground = False  
            self.jumping = True  

'''
The Enemy class represents enemy characters that move back and forth across the screen.
It also inherits from pygame.sprite.Sprite.
'''
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32, 32))  
        self.image.fill(RED)  
        self.rect = self.image.get_rect()  
        self.rect.x = x  
        self.rect.y = y  
        self.direction = 1  
        self.speed = 2  
        
    def update(self):
        '''
        Update the enemy's position. 
        The enemy moves back and forth horizontally, reversing direction when it hits the screen edges.
        '''
        self.rect.x += self.speed * self.direction  
        if self.rect.right > WIDTH or self.rect.left < 0:  
            self.direction *= -1

'''
The Platform class represents platforms that the player can stand on.
It also inherits from pygame.sprite.Sprite.
'''
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, moving=False):
        super().__init__()
        self.image = pygame.Surface((width, height))  
        self.image.fill(GREEN)  
        self.rect = self.image.get_rect()  
        self.rect.x = x  
        self.rect.y = y  
        self.moving = moving  
        if moving:
            self.start_x = x  
            self.direction = 1  
            self.speed = 2  
            
    def update(self):
        '''
        Update the platform's position if it is a moving platform.
        The platform moves back and forth horizontally within a certain range.
        '''
        if self.moving:
            self.rect.x += self.speed * self.direction  
            if abs(self.rect.x - self.start_x) > 100:  
                self.direction *= -1

'''
The Coin class represents coins that the player can collect to increase their score.
It also inherits from pygame.sprite.Sprite.
'''
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((16, 16))  
        self.image.fill(YELLOW)  
        self.rect = self.image.get_rect()  
        self.rect.center = (x, y)  
        self.value = 10  

'''
The Game class manages the overall game logic, including setting up the level, handling events, updating the game state, and drawing everything to the screen.
'''
class Game:
    def __init__(self, num_platforms=5):
        '''
        Initialize the game window, clock, font, and sprite groups.
        '''
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))  
        pygame.display.set_caption("Enhanced PyMario")  
        self.clock = pygame.time.Clock()  
        self.font = pygame.font.Font(None, 36)  
        self.running = True  
        self.game_over = False  
        self.last_coin_spawn = 0  
        self.num_platforms = min(num_platforms, MAX_PLATFORMS)  
        
        '''
        Create sprite groups to manage all game objects.
        '''
        self.all_sprites = pygame.sprite.Group()  
        self.platforms = pygame.sprite.Group()  
        self.coins = pygame.sprite.Group()  
        self.enemies = pygame.sprite.Group()  
        self.powerups = pygame.sprite.Group()  
        
        self.setup_level()  
    
    def setup_level(self):
        '''
        Set up the initial level by creating the player, platforms, and enemies.
        '''
        self.player = Player()  
        self.all_sprites.add(self.player)  
        
        '''
        Generate platforms dynamically based on the number of platforms specified.
        '''
        platform_height = HEIGHT - 40
        platform_spacing = (HEIGHT - 200) // self.num_platforms
        for i in range(self.num_platforms):
            width = random.randint(80, 150)  
            x = random.randint(0, WIDTH - width)  
            y = platform_height - (i * platform_spacing)  
            moving = random.choice([True, False]) if i > 0 else False  
            platform = Platform(x, y, width, 20, moving)
            self.platforms.add(platform)
            self.all_sprites.add(platform)
        
        '''
        Create initial enemies and add them to the appropriate groups.
        '''
        for _ in range(3):  
            enemy = Enemy(random.randint(0, WIDTH), HEIGHT - 80)  
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
    
    def spawn_coin(self):
        '''
        Spawn a new coin at random positions on the screen.
        Coins are spawned at regular intervals defined by COIN_SPAWN_RATE.
        There is also a chance to spawn a health powerup along with the coin.
        '''
        now = pygame.time.get_ticks()  
        if now - self.last_coin_spawn > COIN_SPAWN_RATE:  
            self.last_coin_spawn = now
            x = random.randint(0, WIDTH)  
            y = random.randint(HEIGHT//2, HEIGHT-100)  
            coin = Coin(x, y)  
            self.coins.add(coin)  
            self.all_sprites.add(coin)  
            
            '''
            Chance to spawn a health powerup along with the coin.
            '''
            if random.random() < HEALTH_POWERUP_CHANCE:  
                powerup = HealthPowerup(x + 40, y)  
                self.powerups.add(powerup)
                self.all_sprites.add(powerup)
    
    def handle_collisions(self):
        '''
        Handle collisions between the player and other game objects (platforms, coins, enemies, powerups).
        '''
        hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
        if hits:
            lowest = hits[0]
            for hit in hits:
                if hit.rect.bottom > lowest.rect.bottom:
                    lowest = hit
            
            if self.player.velocity_y > 0:  
                self.player.rect.bottom = lowest.rect.top  
                self.player.velocity_y = 0  
                self.player.on_ground = True  
                self.player.jumping = False  
        
        '''
        Check for collisions between the player and coins.
        '''
        coin_hits = pygame.sprite.spritecollide(self.player, self.coins, True)  
        for coin in coin_hits:
            self.player.score += coin.value  
            
            '''
            Spawn a new enemy when the player's score reaches certain intervals.
            '''
            if self.player.score // ENEMY_SPAWN_SCORE_INTERVAL > \
               (self.player.score - coin.value) // ENEMY_SPAWN_SCORE_INTERVAL:
                if len(self.enemies) < MAX_ENEMIES:  
                    enemy = Enemy(random.randint(0, WIDTH), HEIGHT - 80)  
                    self.enemies.add(enemy)
                    self.all_sprites.add(enemy)
        
        '''
        Check for collisions between the player and health powerups.
        '''
        powerup_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)  
        for powerup in powerup_hits:
            self.player.health = min(100, self.player.health + 30)  
        
        '''
        Check for collisions between the player and enemies.
        '''
        enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        if enemy_hits:
            self.player.health -= 10  
            if self.player.health <= 0:  
                self.game_over = True
    
    def draw_hud(self):
        '''
        Draw the heads-up display (HUD) showing the player's score and health.
        '''
        score_text = self.font.render(f'Score: {self.player.score}', True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        '''
        Draw the health bar.
        '''
        pygame.draw.rect(self.screen, RED, (10, 40, 100, 20))  
        pygame.draw.rect(self.screen, GREEN, (10, 40, self.player.health, 20))  
    
    def run(self):
        '''
        The main game loop. This method runs continuously while the game is active.
        '''
        while self.running:
            self.handle_events()  
            if not self.game_over:
                self.update()  
                self.draw()  
            else:
                self.draw_game_over()  
            self.clock.tick(FPS)  
    
    def handle_events(self):
        '''
        Handle user input events such as quitting the game, jumping, and moving the player.
        '''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  
                self.running = False
            elif event.type == pygame.KEYDOWN:  
                if event.key == pygame.K_SPACE:  
                    self.player.jump()
                elif event.key == pygame.K_r and self.game_over:  
                    self.__init__(self.num_platforms)
        
        '''
        Handle continuous keyboard input for left and right movement.
        '''
        keys = pygame.key.get_pressed()
        self.player.velocity_x = 0  
        if keys[pygame.K_LEFT]:  
            self.player.velocity_x = -PLAYER_SPEED
            self.player.facing_right = False
        if keys[pygame.K_RIGHT]:  
            self.player.velocity_x = PLAYER_SPEED
            self.player.facing_right = True
    
    def update(self):
        '''
        Update the game state by spawning coins, updating all sprites, and handling collisions.
        '''
        self.spawn_coin()  
        self.all_sprites.update()  
        self.handle_collisions()  
    
    def draw(self):
        '''
        Draw the game screen, including the background, sprites, and HUD.
        '''
        self.screen.fill(BLACK)  
        self.all_sprites.draw(self.screen)  
        self.draw_hud()  
        pygame.display.flip()  
    
    def draw_game_over(self):
        '''
        Draw the game over screen, showing the final score and instructions to restart the game.
        '''
        self.screen.fill(BLACK)  
        game_over_text = self.font.render('GAME OVER', True, RED)  
        score_text = self.font.render(f'Final Score: {self.player.score}', True, WHITE)  
        restart_text = self.font.render('Press R to Restart', True, WHITE)  
        
        '''
        Center the text on the screen.
        '''
        self.screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 60))
        self.screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        self.screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 60))
        
        pygame.display.flip()  

'''
Prompt the user to enter the number of platforms for the game.
Ensure the input is valid and within the allowed range.
'''
def get_platform_count():
    pygame.init()
    screen = pygame.display.set_mode((400, 200))
    font = pygame.font.Font(None, 36)
    input_box = pygame.Rect(100, 80, 200, 32)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
        screen.fill((30, 30, 30))
        txt_surface = font.render(f"Enter number of platforms (max {MAX_PLATFORMS}):", True, WHITE)
        screen.blit(txt_surface, (20, 20))
        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(screen, color, input_box, 2)
        pygame.display.flip()
    
    try:
        num = min(int(text), MAX_PLATFORMS)
        return max(1, num)
    except ValueError:
        return 5

'''
The entry point of the program. This block runs when the script is executed.
'''
if __name__ == '__main__':
    num_platforms = get_platform_count()  
    game = Game(num_platforms)  
    game.run()  
    pygame.quit()  
    sys.exit()  
