# change individual config files, and have script copy to config.py
# configuration file for trainBananas
#
subject = 'Test'
#subject = 'MP'

# direction subject has to push the joystick to get the banana
trainingDirection = 'Right'
#trainingDirection = 'Left'

training = 2.4
# Set Training Level - only using 2 and above in this program
# training 2,   left/right, can only move direction towards center
#               self.free_move = False
#               self.must_release = False
#               self.random_banana = False
#               self.require_aim = False
# training 2.1, left/right, must let go of joystick to start next trial,
#               can only move direction towards center
#               self.free_move = False
#               self.must_release = True
#               self.random_banana = False
#               self.require_aim = False
# training 2.2, banana appears randomly on either side, multiple distances. Must let go
#               of joystick to start next trial, can only move direction towards center
#               self.free_move = False
#               self.must_release = True
#               self.random_banana = True
#               self.require_aim = False
# training 2.3, banana appears randomly on either side, multiple distances. Must let go
#               of joystick to start next trial, both directions allowed
#               self.free_move = True
#               self.must_release = True
#               self.random_banana = True
#               self.require_aim = False
# training 2.4, subject has to line up crosshair to banana (not go past) for min. time,
#               slows down if goes past banana, both directions allowed
#               self.free_move = True
#               self.release = True
#               self.random_banana = True
#               self.require_aim = True
# training 3, move crosshair to banana, forward
#               self.go_forward = True

avatar_start_h = 1

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