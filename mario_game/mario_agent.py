import torch
import random
import numpy as np
from collections import deque
from mario import MarioRunner
from model import Linear_QNet, QTrainer
from helper import plot


MAX_MEMORY = 100000
BATCH_SIZE = 100
LR = 0.001
WIDTH, HEIGHT = 800, 400
GROUND_HEIGHT = 50
PLAYER_WIDTH, PLAYER_HEIGHT = 50, 50
OBSTACLE_WIDTH, OBSTACLE_HEIGHT = 30, 50
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60
GRAVITY = 1.5
JUMP_HEIGHT = -20

class Agent:

    def __init__(self,Use_Trained = False):
        self.n_games = 0
        self.epsilon = 0 
        self.gamma = 0.8 
        self.memory = deque(maxlen=MAX_MEMORY) 
        self.model = Linear_QNet(4, 256, 3)
        if Use_Trained:
            self.model.load_state_dict(torch.load('./TRAINED_MODEL/model.pt'))
            self.model.eval()
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)


    def get_state(self, game:MarioRunner):
            
            state = [
                1 if len(game.obstacles)>0 and game.obstacles[0].x < (game.player.x + (game.player.rect.width*2)) and ( game.obstacles[0].y ==  (HEIGHT - GROUND_HEIGHT - OBSTACLE_HEIGHT)) else 0,
                1 if len(game.obstacles)>0 and game.obstacles[0].x < (game.player.x + (game.player.rect.width*2)) and (game.obstacles[0].y ==  (HEIGHT-GROUND_HEIGHT-OBSTACLE_HEIGHT-(PLAYER_HEIGHT*0.75))) else 0,
                game.player.jump,
                game.player.crouch,
                ]
            return np.array(state, dtype=int)
    

    

            
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) 
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    
    def get_action(self, state):
        self.epsilon = 80 - self.n_games
        final_move = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move




def main(Use_Trained = False):
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent(Use_Trained)
    game = MarioRunner()
    while True:
        
        state_old = agent.get_state(game)

        final_move = agent.get_action(state_old)

        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                if not Use_Trained == True:
                    agent.model.save()
                

            print('Game', agent.n_games, 'Score', score, 'Record:', record)
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            # if agent.n_games%GRAPH_UPDATE == 0:
            plot(plot_scores, plot_mean_scores)


# main()