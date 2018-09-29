#!/usr/bin/env python

from gym.envs.registration import register

register(
    id='pogrid-v0',
    entry_point='gym_pogrid.envs:PoGrid',
)
