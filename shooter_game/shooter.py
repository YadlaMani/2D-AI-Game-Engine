import pygame
import random
import numpy as np


SPEED_FACTOR = 4
WIDTH,HEIGHT = 800, 600
PLAYER_SIZE = 40
PLAYER_COLOR = (0, 255, 0)
ASTEROID_SIZE = 40
ASTEROID_COLOR = (255, 0, 0)
ASTEROID_SPEED = 2
BULLET_SIZE = 5
BULLET_SPEED = 5
BULLET_COLOR = (0, 0, 255)

starx = []
stary = []

for i in range(60):
    starx.append(random.randint(0 ,WIDTH))        
    stary.append(random.randint(0 ,HEIGHT))

def display_stars(screen):
    for y in range(len(starx)):
        pygame.draw.circle(screen,(255,255,255),(starx[y],stary[y]),1)

class SpaceShooter:
    def __init__(self):
        pygame.init()

        self.WIDTH, self.HEIGHT = 800, 600
        self.BACKGROUND_COLOR = (0, 0, 0)
        self.PLAYER_COLOR = (0, 255, 0)
        self.ASTEROID_COLOR = (255, 0, 0)
        self.BULLET_COLOR = (0, 0, 255)
        self.PLAYER_SIZE = 40
        self.BULLET_SIZE = 5
        self.ASTEROID_SIZE = 40
        self.ASTEROID_SPEED = 2
        self.BULLET_SPEED = 5
        self.score=0
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Space Shooter")
        self.clock = pygame.time.Clock()
        self.frames = 0
        self.frames_in_loop = 0
        self.player = self.Player()
        self.asteroids = []
        self.bullets = []
        self.times =0
        self.font = pygame.font.Font('arial.ttf', 25)

    class Player:
        def __init__(self):
            self.x = WIDTH // 2
            self.y = HEIGHT - PLAYER_SIZE
            self.width = PLAYER_SIZE
            self.height = PLAYER_SIZE

        def move(self, dx):
            if 0 < self.x + PLAYER_SIZE + dx*SPEED_FACTOR < WIDTH:
                self.x += dx*SPEED_FACTOR

        def draw(self, screen):
            pygame.draw.rect(screen, PLAYER_COLOR, (self.x, self.y, self.width, self.height))

    class Asteroid:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.width = ASTEROID_SIZE
            self.height = ASTEROID_SIZE

        def move(self):
            self.y += SPEED_FACTOR*ASTEROID_SPEED

        def draw(self, screen):
            pygame.draw.rect(screen, ASTEROID_COLOR, (self.x, self.y, self.width, self.height))

    class Bullet:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.width = BULLET_SIZE
            self.height = BULLET_SIZE

        def move(self):
            self.y -= BULLET_SPEED*SPEED_FACTOR

        def draw(self, screen):
            pygame.draw.rect(screen, BULLET_COLOR, (self.x, self.y, self.width, self.height))
    def reset(self):
        self.score = 0
        self.player = self.Player()
        self.asteroids = []
        self.bullets = []
        self.frames = 0
        self.frames_in_loop = 0
        self.times = 0
        

    def place_asteroids(self):
        x = random.randint(0, self.WIDTH - self.ASTEROID_SIZE)
        y = random.randint(-self.HEIGHT, 0)
        asteroid = self.Asteroid(x, y)
        self.asteroids.append(asteroid)

    def play_step(self, action):
        self.frames +=1 
        self.frames_in_loop +=1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        reward = 0
        done = False
        score = self.score
        if np.array_equal(action ,[1,0,0]):
            self.player.move(-5)
        if np.array_equal(action ,[0,0,1]):
            self.player.move(5)
        if np.array_equal(action ,[0,1,0]):
            self.shoot()
        if self.frames_in_loop > 120:
            reward = -10 + 1 if int(self.times) == 0 else self.times
            self.frames_in_loop = 0
            self.times += 1
            return reward,done,score
        if self.asteroid_damaged():
            reward = 10
            self.frames_in_loop = 0
            return reward , done,score
        
        if self.is_game_over() : 
            reward = -10
            done = True
            return reward ,done ,score
        
        asteroid_not_shooted , reward_as , done_as ,score_as = self.asteroids_not_damaged()
        if asteroid_not_shooted:
            return reward_as , done_as,score_as
        self._update_ui()
        self.clock.tick(60)
        return reward, done,score

    def _update_ui(self):
        self.screen.fill(self.BACKGROUND_COLOR)
        icon=pygame.image.load('startup.png')
        pygame.display.set_icon(icon)
        display_stars(self.screen)
        for asteroid in self.asteroids:
            asteroid.move()
        for bullet in self.bullets:
            bullet.move()
        
        self.bullets[:] = [bullet for bullet in self.bullets if bullet.y < self.HEIGHT]
        if self.frames%30 ==0:
            self.place_asteroids()     

        self.player.draw(self.screen)
        for asteroid in self.asteroids:
            asteroid.draw(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)

        score_text = self.font.render(f'Score: {self.score}', True, (255, 255, 0))
        self.screen.blit(score_text, (10, 10))

        pygame.display.flip()
    def shoot(self):
        bullet = self.Bullet(self.player.x + self.player.width // 2 - self.BULLET_SIZE // 2, self.player.y)
        self.bullets.append(bullet)
    def asteroids_not_damaged(self):
        temp = self.asteroids
        self.asteroids = []
        reward =0
        done=False
        score = self.score
        asteroid_not_shooted = False
        for asteroid in temp:
            if asteroid.y < self.HEIGHT:
                self.asteroids.append(asteroid)
            else:
                reward += -5
                asteroid_not_shooted = True
        return asteroid_not_shooted,reward,done,score
                

    def asteroid_damaged(self):
        for bullet in self.bullets:
            for asteroid in self.asteroids:
                if (
                    bullet.x < asteroid.x + asteroid.width
                    and bullet.x + bullet.width > asteroid.x
                    and bullet.y < asteroid.y + asteroid.height
                    and bullet.y + bullet.height > asteroid.y
                ):
                    self.asteroids.remove(asteroid)
                    self.bullets.remove(bullet)
                    self.score +=1    
                    return True
        return False

    def is_game_over(self):
        for asteroid in self.asteroids:
            if (
                self.player.x < asteroid.x + asteroid.width
                and self.player.x + self.player.width > asteroid.x
                and self.player.y < asteroid.y + asteroid.height
                and self.player.y + self.player.height > asteroid.y
            ):
                return True
        return False

    def is_collision(self,x,y):
        if (
            x+PLAYER_SIZE < self.asteroids[0].x + self.asteroids[0].width
            and x+PLAYER_SIZE + PLAYER_SIZE > self.asteroids[0].x
            and y+PLAYER_SIZE < self.asteroids[0].y + self.asteroids[0].height
            and y+PLAYER_SIZE + PLAYER_SIZE > self.asteroids[0].y
        ):
                return True
        return False

