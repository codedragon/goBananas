# change individual config files, and have script copy to config.py
# configuration file for trainBananas
#
#subject = 'Gromit'
#subject = 'Test'
subject = 'MP'

# whether to show the environment in the background
background = False

#fruit = 'cherry'
# direction subject has to push the joystick to get the banana
#trainingDirection = 'Right'
trainingDirection = 'Left'

training = 2.0
#training = 3.0

# Set Training Level - only using 2 and above in this program
# for all training 2, no forward movement (go_forward = False)
# training 2.0, left/right, can only move direction towards center
#               self.free_move = 1 (only towards banana)
#               self.must_release = False
#               self.random_banana = False
#               self.require_aim = False
# training 2.1, left/right, must let go of joystick to start next trial,
#          can only move direction towards center
#               self.free_move = 1
#               self.must_release = True
#               self.random_banana = False
#               self.require_aim = False
# training 2.2, banana appears randomly on either side, multiple distances. Must let go
#          of joystick to start next trial, can only move direction towards center
#               self.free_move = 1
#               self.must_release = True
#               self.random_banana = True
#               self.require_aim = False
# training 2.3, banana appears randomly on either side, multiple distances. Must let go
#          of joystick to start next trial, both directions allowed, wrong direction
#          slower than towards center
#               self.free_move = 2 (both directions, away from center slow)
#               self.must_release = True
#               self.random_banana = True
#               self.require_aim = False
# training 2.4, banana appears randomly on either side, multiple distances. Must let go
#          of joystick to start next trial, both directions allowed, wrong direction
#          same speed as towards center
#               self.free_move = 3 (both directions, all normal speeds)
#               self.must_release = True
#               self.random_banana = True
#               self.require_aim = False
# training 2.5, subject has to line up crosshair to banana (not go past) for min. time,
#          slows down if goes past banana (for direction away from banana), both directions allowed
#               self.free_move = 3
#               self.must_release = True
#               self.random_banana = True
#               self.require_aim = 'slow'
# training 2.6, subject has to line up crosshair to banana (not go past) for min. time,
#          continues at normal speed if goes past banana, both directions allowed
#               self.free_move = 3
#               self.must_release = True
#               self.random_banana = True
#               self.require_aim = True
# training 3.0, move crosshair to banana, forward, no movement right and left
#               self.go_forward = True
#               self.free_move = 0
#               self.must_release = False
#               self.random_banana = False
#               self.require_aim = False (rather meaningless here)
# training 3.1, move crosshair to banana, forward, must let go of joystick to start
#          new trial
#               self.go_forward = True
#               self.free_move = 0
#               self.must_release = True
#               self.random_banana = False
#               self.require_aim = False (rather meaningless here)
# training 4, combines forward and side movement. banana shows up randomly
#          on either side, must line up going right/left first (no forward allowed)
#          Once lined up, partial reward, and can no longer go left/right,
#          only forward, full reward for running into banana
#      NOTE: For training 4 always use the T block, otherwise may encourage bad habits.
#               self.go_forward = False (starts at False, changes to True)
#               self.free_move = 4
#               self.must_release = False (might want this for actual running into banana)
#               self.random_banana = True
#               self.require_aim = False
# training 4.1, same as 4 except needs to aim before going forward, slows down if misses
#               self.go_forward = False (starts at False, changes to True)
#               self.free_move = 4
#               self.must_release = False (might want this for actual running into banana)
#               self.random_banana = True
#               self.require_aim = "slow" (need to leave it in center for a min. time before
#                                        getting partial reward and allowed to go forward)
# training 4.2, same as 4 except needs to aim before going forward, zooms right past banana
#               self.go_forward = False (starts at False, changes to True)
#               self.free_move = 4
#               self.must_release = False (might want this for actual running into banana)
#               self.random_banana = True
#               self.require_aim = True (need to leave it in center for a min. time before
#                                        getting partial reward and allowed to go forward)

# starting angle between avatar and banana  (turning training)
#avatar_start_h = 1.5
avatar_start_h = 6

# starting distance between avatar and banana (forward training)
# with turning training, this is 2.5, so further than this for
# smaller banana)
avatar_start_d = 3.5

# list of all random selections available (2.3 and above)
#random_lists = [[3, 5, 6.5], [3, 5, 7], [3, 5, 7.5], [3, 5, 7.5, 8], [3, 5, 7.5, 8.5], [3, 5, 7.5, 8.5, 9],
#                [3, 5, 7.5, 8.5, 9.5, 10], [3, 5, 7, 8, 9, 10, 11]]

# random_lists = [[3, 5, 6.5], [3, 5, 7], [3, 5, 6.5, 7.5], [3, 5, 7, 8], [3, 5, 7, 9],
#                 [3, 5, 7, 9.5], [4, 6, 7, 10], [4, 5, 8, 10.5], [4, 6, 9, 11], [4, 6, 8, 10, 12],
#                 [4, 6, 8, 10, 13], [4, 7, 10, 12, 14], [4, 7, 10, 13, 15], [5, 8, 11, 14, 16], [5, 8, 11, 14, 17],
#                 [4, 6, 9, 12, 15, 18], [4, 6, 10, 13, 16, 19], [4, 7, 10, 14, 17, 20], [4, 7, 10, 14, 18, 21],
#                 [4, 7, 10, 14, 18, 22], ]
# # choose starting number of random_lists.
# random_selection = 21

# for cherries, go no closer than 8, 23 is fully on screen
random_lists = [[8, 11, 14, 17, 20, 23]]
# choose starting number of random_lists.
random_selection = 1

# random bias means that it is not strictly random, if there are 2 bananas in a row
# on one side, the next banana will always switch sides.
random_bias = True

# amount of time need to hold crosshair on banana to get reward
# For training 2.3 and higher.
# must be more than zero. At 1.5 distance, must be greater than
# 0.5 to require stopping
hold_aim = 0.6

# what speed to start out at this will be multiplied by pressure on joystick
# and time since last screen refresh
initial_turn_speed = 0.2
#initial_speed = 2

initial_forward_speed = 1.0

# limits how much subject can go to the side when suppose to be going forward
# limit of 1 means no restriction, should not go smaller than 0.2
forward_limit = 1
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
