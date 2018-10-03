#!/usr/bin/env python
import gym_pogrid
import numpy as np
import gym

env = gym.make('pogrid-fo-84-v0')
for i_episode in range(20):
    observation = env.reset()
    for t in range(100):
        #env.render()
        action = env.action_space.sample()
        observation, reward, done, info = env.step(action)

        print("step:{} - reward:{}".format(t, reward))

        if done:
            print("Episode finished after {} timesteps".format(t+1))
            break

