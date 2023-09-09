import torch
import random
import numpy as np
from collections import deque
from shooter import SpaceShooter
from model import Linear_QNet, QTrainer
from helper import plot


MAX_MEMORY = 100000
BATCH_SIZE = 100
LR = 0.001

class Agent:

    def __init__(self,Use_Trained):
        self.n_games = 0
        self.epsilon = 0 
        self.gamma = 0.8 
        self.memory = deque(maxlen=MAX_MEMORY) 
        self.model = Linear_QNet(12, 256, 3)
        if Use_Trained:
            self.model.load_state_dict(torch.load('./TRAINED_MODEL/model.pt'))
            self.model.eval()
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)


    def get_state(self, game:SpaceShooter):
            for i in range(len(game.asteroids)):
                if ((game.player.x - 2*game.player.width) < game.asteroids[i].x < game.player.x) :
                    j=1
                else:
                    j=0
                if((game.player.x + 3*game.player.width) > game.asteroids[i].x > (game.player.x+game.player.width)):
                    k=1
                else:
                    k=0
                if ((game.player.y + 2*game.player.height) < game.asteroids[i].y < game.player.y):
                    l =1
                else:
                    l=0
            state = [
                # Asteroid location 
                game.asteroids[0].x < game.player.x if (len(game.asteroids) > 0) else 0,  # Asteroid left
                game.asteroids[0].x > game.player.x+game.player.width if ((len(game.asteroids) > 0)) else 0,  # Asteroid right
                game.asteroids[0].y < game.player.y if (len(game.asteroids) > 0) else 0,
                game.asteroids[1].x < game.player.x if (len(game.asteroids) > 1) else 0,  # Asteroid left
                game.asteroids[1].x > game.player.x+game.player.width if (len(game.asteroids) > 1)else 0,  # Asteroid right
                game.asteroids[1].y < game.player.y if (len(game.asteroids) > 1) else 0,
                game.asteroids[2].x < game.player.x if (len(game.asteroids) > 2) else 0,  # Asteroid left
                game.asteroids[2].x > game.player.x+game.player.width if (len(game.asteroids) > 2) else 0,  # Asteroid right
                game.asteroids[2].y < game.player.y if (len(game.asteroids) > 2) else 0,
                j if (len(game.asteroids) > 0) else 0,
                k if (len(game.asteroids) > 0) else 0,
                l if (len(game.asteroids) > 0) else 0,
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
    game = SpaceShooter()
    while True:
        
        state_old = agent.get_state(game)

        final_move = agent.get_action(state_old)

        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                if not (Use_Trained == True):
                    agent.model.save()

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            
            plot(plot_scores,plot_mean_scores)



# main()