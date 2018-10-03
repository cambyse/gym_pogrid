#!/usr/bin/env python
import gym
from gym import spaces
import numpy as np
import random
import itertools
from skimage import transform
import math
from numpy import linalg
import pygame 

pygame.init()

REWARD_STEP = 0.0
REWARD_FIRE = -1.0
REWARD_COIN = 1.0
COIN = 'coin'
FIRE = 'fire'

class gameOb():
    def __init__(self,coordinates,size,intensity,channel,reward,name):
        metadata = {'render.modes': ['human']}
        self.x = coordinates[0]
        self.y = coordinates[1]
        self.size = size
        self.intensity = intensity
        self.channel = channel
        self.reward = reward
        self.name = name
        self.action_space_n = 4
        
class PoGrid(gym.Env):
    def __init__(self, output_size, partial):
        self.sizeX = 5
        self.sizeY = 5
        self.actions = 4
        
        self.objects = []
        self.partial = partial #False
        self.output_size = output_size #84

        self.action_space = spaces.Discrete(self.actions)
        self.observation_space = spaces.Box(low=0.0, high=1.0, shape=(self.output_size, self.output_size, 3),
                                                dtype=np.float32)
        
        a = self.reset()

        self.screen = pygame.display.set_mode((self.output_size, self.output_size))

    def step(self,action):
        self.moveChar(action)
        reward,done = self.checkGoal()
        state = self.renderEnv()
        return state,reward,done, None
        
    def reset(self):
        self.objects = []
        hero = gameOb(self.newPosition(),1,1,2,None,'hero')
        self.objects.append(hero)
        self.objects.append(gameOb(self.newPosition(),1,1,1, REWARD_COIN,COIN))
        self.objects.append(gameOb(self.newPosition(),1,1,0, REWARD_FIRE,FIRE))
        self.objects.append(gameOb(self.newPosition(),1,1,1, REWARD_COIN,COIN))
        self.objects.append(gameOb(self.newPosition(),1,1,0, REWARD_FIRE,FIRE))
        self.objects.append(gameOb(self.newPosition(),1,1,1, REWARD_COIN,COIN))
        self.objects.append(gameOb(self.newPosition(),1,1,0, REWARD_FIRE,FIRE))
        self.state = self.renderEnv()
        return self.state

    def render(self, mode='human', close=False):
        observation = self.renderEnv()
        rgb_obs = (observation*255).astype("uint8")
        #print(rgb_obs.flatten())
        image = pygame.image.frombuffer(rgb_obs.flatten(), ( self.output_size, self.output_size ), 'RGB')
        self.screen.blit(image, (0,0))
        pygame.display.flip()

    def renderEnv(self):
        #a = np.zeros([self.sizeY,self.sizeX,3])
        a = np.ones([self.sizeY+2,self.sizeX+2,3])
        a[1:-1,1:-1,:] = 0
        hero = None
        for item in self.objects:
            if self.partial == False or self.isVisible(item):
                a[item.y+1:item.y+item.size+1,item.x+1:item.x+item.size+1,item.channel] = item.intensity
        #    if item.name == 'hero':
        #        hero = item
        #if self.partial == True:
        #    a = a[hero.y:hero.y+3,hero.x:hero.x+3,:]
        b = transform.resize(a[:,:,0],[self.output_size,self.output_size,1], order=0, anti_aliasing=False)
        c = transform.resize(a[:,:,1],[self.output_size,self.output_size,1], order=0, anti_aliasing=False)
        d = transform.resize(a[:,:,2],[self.output_size,self.output_size,1], order=0, anti_aliasing=False)

        a = np.stack([b,c,d],axis=2)

        return a[:,:,:,0]

    def moveChar(self,direction):
        # 0 - up, 1 - down, 2 - left, 3 - right
        hero = self.objects[0]
        if direction == 0 and hero.y >= 1:
            hero.y -= 1
        if direction == 1 and hero.y <= self.sizeY-2:
            hero.y += 1
        if direction == 2 and hero.x >= 1:
            hero.x -= 1
        if direction == 3 and hero.x <= self.sizeX-2:
            hero.x += 1     
        #if hero.x == heroX and hero.y == heroY:
        #    penalize = 0.0
        self.objects[0] = hero
        return
    
    def newPosition(self):
        iterables = [ range(self.sizeX), range(self.sizeY)]
        points = []
        for t in itertools.product(*iterables):
            points.append(t)
        currentPositions = []
        for objectA in self.objects:
            if (objectA.x,objectA.y) not in currentPositions:
                currentPositions.append((objectA.x,objectA.y))
        for pos in currentPositions:
            points.remove(pos)
        location = np.random.choice(range(len(points)),replace=False)
        return points[location]

    def checkGoal(self):
        nRemainingCoins = 0
        ended = False

        for obj in self.objects:
            if obj.name == COIN:
                nRemainingCoins+=1
            if obj.name == 'hero':
                hero = obj

        # return early when we encounter an object
        for obj in self.objects[1:]:
            if hero.x == obj.x and hero.y == obj.y:
                if obj.reward == 1:
                    self.objects.remove(obj)
                    nRemainingCoins-=1
                if nRemainingCoins == 0:
                    ended = True
                return obj.reward,ended

        # simple small negative reward otherwise
        if ended == False:
            return REWARD_STEP,False

    def getHero(self):
        for item in self.objects:
            if item.name == 'hero':
                return item

    def relativePolarCoord(self,hero, item):
        dx = item.x-hero.x
        dy = item.y-hero.y
        r = math.sqrt(math.pow(dx, 2)+math.pow(dy, 2))
        a = math.atan2(dy, dx)
        return r, a

    def relativeDistances(self,hero, item, obstacle):
        v_item = [item.x-hero.x, item.y-hero.y]
        v_obstacle = [obstacle.x-hero.x, obstacle.y-hero.y]
        v_item_u = v_item / np.linalg.norm(v_item)
        v_obstacle_to_item = np.dot(v_obstacle, v_item_u) * v_item_u
        v_delta = v_obstacle - v_obstacle_to_item
        return np.linalg.norm(v_obstacle) - np.linalg.norm(v_item), np.linalg.norm(v_delta)

    def isVisible(self,item):
        hero = self.getHero()
        r, a = self.relativePolarCoord(hero, item)
        if item == hero:
            return True
        for obstacle in self.objects:
            if obstacle != item and obstacle != hero:
                dr, d = self.relativeDistances(hero, item, obstacle)
                if dr < 0 and d <= 0.5:
                   return False
        return True
                
class PoGridFO84(PoGrid):
    def __init__(self):
        PoGrid.__init__(self,84, False)

class PoGridFO42(PoGrid):
    def __init__(self):
        PoGrid.__init__(self,42, False)
    

