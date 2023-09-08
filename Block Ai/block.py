import pygame
import random
import numpy as np
# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 400
GROUND_HEIGHT = 50
PLAYER_WIDTH, PLAYER_HEIGHT = 50, 50
OBSTACLE_WIDTH, OBSTACLE_HEIGHT = 30, 50
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60
GRAVITY = 1.5
JUMP_HEIGHT = -20

# Create the self.screen
class MarioRunner():
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Block Escape Game")
        self.player = self.Player(self.screen)
        self.obstacles = []
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.frames = 0
        self.score = 0
        self.reset()
    # Player class
    class Player:
        def __init__(self , screen):
            self.x = 100
            self.y = HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT
            self.velocity_y = 0
            self.jump = False
            self.crouch = False
            self.screen = screen
        def jump_action(self):
            if not self.jump:
                self.velocity_y = JUMP_HEIGHT
                self.jump = True

        def crouch_action(self):
            self.crouch = True

        def uncrouch_action(self):
            self.crouch = False

        def update(self):
            if self.jump:
                self.y += self.velocity_y
                self.velocity_y += GRAVITY
                if self.y >= HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT:
                    self.y = HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT
                    self.jump = False
                    self.velocity_y = 0

        def draw(self):
            if self.crouch:
                self.rect = pygame.Rect(self.x, self.y + PLAYER_HEIGHT // 2, PLAYER_WIDTH, PLAYER_HEIGHT // 2)
                pygame.draw.rect(self.screen, BLACK, self.rect)
            else:
                self.rect = pygame.Rect(self.x, self.y, PLAYER_WIDTH, PLAYER_HEIGHT)
                pygame.draw.rect(self.screen, BLACK, self.rect)

    # Obstacle class
    class Obstacle:
        def __init__(self,screen ,x , y = HEIGHT - GROUND_HEIGHT - OBSTACLE_HEIGHT ):
            self.x = x
            self.y = y
            self.screen = screen

        def move(self):
            self.x -= 5

        def off_screen(self):
            return self.x + OBSTACLE_WIDTH < 0

        def draw(self):
            self.rect = pygame.Rect(self.x, self.y, OBSTACLE_WIDTH, OBSTACLE_HEIGHT)
            pygame.draw.rect(self.screen, BLACK, self.rect)

    # Game initialization
    def is_collision(self):
        for obstacle in self.obstacles:
            if self.player.rect.colliderect(obstacle.rect):
                return True
        return False
    
    def wiil_collide(self, player,obstacle):
        if player.rect.colliderect(obstacle.rect):
            return True
        return False

    def play_step(self,action):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        # running = True
        # while running:
        #     self.update_ui()
        #     for event in pygame.event.get():
        #         if event.type == pygame.QUIT:
        #             running = False
        #         elif event.type == pygame.KEYDOWN:
        #             if event.key == pygame.K_SPACE:
        #                 self.player.jump_action()
        #             elif event.key == pygame.K_DOWN:
        #                 self.player.crouch_action()
        #         elif event.type == pygame.KEYUP:
        #             if event.key == pygame.K_DOWN:
        #                 self.player.uncrouch_action()
        reward = 0
        done = False
        score = self.score
        if np.array_equal(action,[1,0,0]):
            self.player.jump_action()
            self.player.uncrouch_action()
        if np.array_equal(action,[0,1,0]):
                self.player.crouch_action()
        if np.array_equal(action,[0,0,1]):
            self.player.uncrouch_action()

        if self.is_collision():
            reward = -10
            done = True
            return reward,done ,score
        

        for obstacle in self.obstacles:
            obstacle.move()
            if obstacle.off_screen():
                self.score +=1
                self.obstacles.remove(obstacle)
                reward +=10
        self.update_ui()
        return reward , done , score

    def update_ui(self):
        self.frames +=1
        i = random.randint(0, 1)
        if len(self.obstacles) <= 4 and self.frames%120==0:
            if i == 0:
                self.obstacles.append(self.Obstacle(self.screen,WIDTH))
            else:
                self.obstacles.append(self.Obstacle(self.screen,WIDTH,HEIGHT-GROUND_HEIGHT-OBSTACLE_HEIGHT-(PLAYER_HEIGHT*0.75)))
        
        
        self.player.update()
        self.screen.fill(WHITE)
        image = pygame.image.load('images.jpeg')
        rect_dis = pygame.Rect(0,0,WIDTH,HEIGHT)
        self.screen.blit(image, (0, 0),rect_dis)
        icon=pygame.image.load('block.png')
        pygame.display.set_icon(icon)
        pygame.draw.rect(self.screen, BLACK, (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))
        self.player.draw()
        for obstacle in self.obstacles:
            obstacle.draw()
        
        score_text = self.font.render(f'Score: {self.score}', True, (255, 0, 255))
        self.screen.blit(score_text, (10, 10))
        pygame.display.flip()
        self.clock.tick(FPS)
    def reset(self):
        self.player = self.Player(self.screen)
        self.obstacles = []
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.frames = 0
        self.score = 0


# MarioRunner().play_step()