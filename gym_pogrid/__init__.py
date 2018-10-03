#!/usr/bin/env python

from gym.envs.registration import register

register(
    id='pogrid-fo-84-v0',
    entry_point='gym_pogrid.envs:PoGridFO84',
)

register(
    id='pogrid-fo-42-v0',
    entry_point='gym_pogrid.envs:PoGridFO42',
)
