# change individual config files, and have script copy to config.py
# configuration file for trainBananas
#
subject = 'Test'
#subject = 'MP'

# direction subject has to push the joystick to get the banana
#trainingDirection = 'Right'
trainingDirection = 'Left'

# Set Training Level - only using 2 and above in this program
# training 2, move crosshair to banana, left/right, opposite direction does nothing
# training 2.1, move crosshair to banana, must let go of joystick to start next trial,
#               opposite direction still does nothing
# training 2.2, move crosshair to banana, must let go of joystick to start next trial,
#               opposite direction allowed
# training 2.3, subject has to line up crosshair to banana (not go past) for min. time,
#               slows down if goes past banana, opposite direction allowed
# training 3, move crosshair to banana, forward
training = 2.3

# Are we giving rewards? If true but no pydaq, just won't send pulse.
#reward = False
reward = True

# # for activating reward system
pulseInterval = 0.2  # in seconds
#

# how many reward pulses to give per reward
numBeeps = 3

# starting alpha for crosshair
xHairAlpha = 1