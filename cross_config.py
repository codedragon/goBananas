# change individual config files, and have script copy to config.py
# configuration file for goBananas
#
subject = 'Test'
#subject = 'MP'

# Are we giving rewards? If true but no pydaq, just won't send pulse.
#reward = False
reward = True

# Are we collecting eye data?
eyeData = False
#eyeData = True
#

# # reward
# numBeeps = 3

# # for activating reward system
pulseInterval = 0.2  # in seconds
#
# start rewarding backward?
# zero, all backward allowed
# one, straight backward not rewarded (actually small angle backward not rewarded)
# two, backward in general not rewarded (actually just a much large angle backward not rewarded)
backward = 0