# change individual config files, and have script copy to config.py
# configuration file for goBananas
#
subject = 'Test'
#subject = 'MP'

# direction subject has to push the joystick to get the banana
trainingDirection = 'Right'
#trainingDirection = 'Left'

# Set Training Level - only using 2 and above in this program
# training 2, move crosshair to banana, left/right
# training 2.1, move crosshair to banana, must let go of joystick to start next trial
# training 2.2, subject has to line up crosshair to banana for min. time, slows down if goes past banana
# training 3, move crosshair to banana, forward
training = 2

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