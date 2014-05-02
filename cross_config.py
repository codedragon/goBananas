# change individual config files, and have script copy to config.py
# configuration file for goBananas
from panda3d.core import Point3
#
subject = 'Test'
# Set Training Level
# See README for info about Training Levels
training = 0

# # direction subject has to push the joystick
# trainingDirection = 'Right'
# #trainingDirection = 'Left'

# Are we giving rewards? not if not using pydaq
#reward = False
reward = True

# Are we collecting eye data?
eyeData = False
#eyeData = True
#

# Joystick thresholds, first one depends a single reward,
# second one is how far to assume it was an intentional
# hold and reward continuously, limits are 0 to 1
threshold = 0.03
confidence = 0.3
# # reward
# numBeeps = 3

# # for activating reward system
# pulseInterval = 200  # in ms
#

# # needed for joystick (instructions)
# #instructSize = 0.1
# instructSize = 0.2
# instructFont = '/c/Windows/Fonts/times.ttf'
# instructBgColor = Point4(0, 0, 0, 1)
# instructFgColor = Point4(1, 1, 1, 1)
# instructMargin = 0.06
# instructSeeAll = False
#
# starting alpha for crosshair
xHairAlpha = 1
# how far to travel per joystick push
xHairDist = 0.01
# starting distance from center (range 0-1), use positive numbers,
# direction determined by trainingDirection.
xStartPos = Point3(0.05, 0, 0)
#beginning_x = Point3(0.05, 0, 0)
#
# # zero, all backward allowed
# # one, straight backward not rewarded
# # two, no backward rewarded
# backward = 0
#
# # Bananas.
# numBananas = 1
# # if training direction is right, both x and y should be positive
# #posBananas = [2, 4.6]
# posBananas = [0.5, 4.975]
# # ack so bloody annoying!!!!
# #startBanana = Point3(2, 4.6, 1)
# startBanana = Point3(0.5, 4.975, 1)
# # posBananas = [0, 5]  # banana in center
# #posBananas = [0, 0, 1, 0]
# #numBananas = 25
# bananaDir = './models/bananas/'
# #bananaZ = 1
# #bananaScale = .5
# bananaScale = 0.5
# #bananaRotation = 0  # Rotation speed in degrees/frame.
# # how close is too close together?
# tooClose = 2  # 1.7
#
# # Banana Positions
# minDistance = -7
# maxDistance = 7
# minFwDistance = -7
# maxFwDistance = 7
# #fwDistanceIncrement = .1
#
# # (Non-default) command keys.
# # Keyboard is global from pandaepl.common
# # if 'Keyboard' in globals():
# #     keyboard = Keyboard.getInstance()
# #     keyboard.bind("close", ["escape", "q"])
# #     #keyboard.bind("exit", ["escape", "q"])
# #     #keyboard.bind("restart", "r")
# #     keyboard.bind("toggleDebug", ["escape", "d"])
# #     #keyboard.bind("increaseDist", ["shift", "up"])
# #     #keyboard.bind("decreaseDist", ["shift", "down"])
# #     keyboard.bind("increaseDist", "w")
# #     keyboard.bind("decreaseDist", "s")
# #     #keyboard.bind("increaseBananas", "w")
# #     #keyboard.bind("decreaseBananas", "s")
# #     keyboard.bind("increaseTouch", "e")
# #     keyboard.bind("decreaseTouch", "d")
# #     keyboard.bind("increaseReward", "t")
# #     keyboard.bind("decreaseReward", "g")
# #     keyboard.bind("increaseInt", "u")
# #     keyboard.bind("decreaseInt", "j")
# #     keyboard.bind("changeLeft", "l")
# #     keyboard.bind("changeRight", "r")
# #     keyboard.bind("changeForward", "f")
# #     keyboard.bind("allowBackward", "b")
# #     keyboard.bind("override", "o")
# #     keyboard.bind("pause", "p")
# #     keyboard.bind("reward", "space")
