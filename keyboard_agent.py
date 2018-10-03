#!/usr/bin/env python
import gym_pogrid
import numpy as np
import gym

env = gym.make('pogrid-fo-84-v0')
for i_episode in range(20):
    observation = env.reset()
    env.render()
    for t in range(100):
        #action = env.action_space.sample()
        action = input("action? ")
        action_id = int(action)
        print(action_id)
        if action_id >= 0 and action_id < 4:#env.action_space.n:
            observation, reward, done, info = env.step(action_id)
            print("step:{} - reward:{}".format(t, reward))
            env.render()

        if done:
            print("Episode finished after {} timesteps".format(t+1))
            break
