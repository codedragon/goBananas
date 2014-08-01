# change individual config files, and have script copy to config.py
# configuration file for goBananas
#
#subject = 'Test'
subject = 'Grommet'

# Are we giving rewards? If true but no pydaq, just won't send pulse.
#reward = False
reward = True

# # for activating reward system
pulseInterval = 0.2  # in seconds
#

# start rewarding backward?
# zero, all backward allowed
# one, straight backward not rewarded (actually small angle backward not rewarded)
# two, backward in general not rewarded (actually just a much large angle backward not rewarded)
backward = 2

# how many ms to hold for reward (then rewards at that interval 2 = 200ms, 4 = 400ms, etc)
#goal = 2
goal = 1