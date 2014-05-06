# change individual config files, and have script copy to config.py
# configuration file for goBananas
#
subject = 'Test'

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
# one, straight backward not rewarded
# two, no backward rewarded
backward = 0