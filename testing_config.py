# change individual config files, and have script copy to config.py
# configuration file for goBananas
from panda3d.core import Point3, Point4

subject = 'Test'
# Set Training Level 
# See README for info about Training Levels
training = 1

# models are in goBananas directory by default
path_models = ''

# direction subject has to push the joystick
trainingDirection = 'Right'
#trainingDirection = 'Left'

# manual mode allows you to place up to 2 bananas in specific places,
# rather than having random placement of x bananas
manual = True

# environ types available:
# 'training'
# 'original'
# None gives you nothing
environ = None
#environ = 'original'

# Are we giving rewards? not if not using pydaq
#reward = False
reward = True

# Are we collecting eye data?
eyeData = False
#eyeData = True

# 3d?
# framebuffer-stereo 1

# reward
numBeeps = 3
# factor to increase reward for last banana
extra = 2
# for activating reward system
pulseInterval = 200  # in ms

# eye position calibration information
# since we are getting voltage from IScan of -5:5
# gain of 100 gives us a range of 1000, which is
# close enough to the number of pixels we are using.
# if increase resolution beyond 1024, should probably
# adjust this
gain = (100, 100)  # (x, y)
offset = (1, 1)  # (x,y)

#### Core PandaEPL settings ####

FOV = 60

# Movement
linearAcceleration = 30
if training >= 3:
    fullForwardSpeed = 2.8
#fullForwardSpeed = 0.0
else:
    fullForwardSpeed = 0
fullBackwardSpeed = 0
#turningAcceleration = 30
turningAcceleration = 130
if training == 3.1:
    fullTurningSpeed = 0
elif training >= 2:
    fullTurningSpeed = 55
#fullTurningSpeed = 20
else:
    fullTurningSpeed = 200
turningLinearSpeed = 2  #Kiril has this as a factor, 
# with min and max, eventually implement

# Point3 is global from panda3d.core
initialPos = Point3(0, 0, 1)

# If you want to collide with bananas at a closer or 
# further distance, change this, but does no good if 
# thing running into has huge radius
#avatarRadius = 0.3
avatarRadius = 0.2

cameraPos = Point3(0, 0, 0)
friction = 0.4 #0.4
movementType = 'walking' # car | walking

# needed for joystick (instructions)
instructSize = 0.1
instructFont = '/c/Windows/Fonts/times.ttf'
instructBgColor = Point4(0, 0, 0, 1)
instructFgColor = Point4(1, 1, 1, 1)
instructMargin = 0.06
instructSeeAll = False

# Experiment-specific settings

# starting alpha for crosshair
xHairAlpha = 1
# how far to travel per joystick push
xHairDist = 0.01
# starting distance from center (range 0-1), use positive numbers,
# direction determined by trainingDirection.
xStartPos = Point3(0.05, 0, 0)
beginning_x = Point3(0.05, 0, 0)

# Bananas.
numBananas = 1
posBananas = [-0.2, 5]
#posBananas = [0, 0, 1, 0]
#numBananas = 25
bananaDir = './models/bananas/'
#bananaZ = 1
#bananaScale = .5
bananaScale = 5
#bananaRotation = 0  # Rotation speed in degrees/frame.
# how close is too close together?
tooClose = 2  # 1.7

# Banana Positions
minDistance = -7
maxDistance = 7
minFwDistance = -7
maxFwDistance = 7
#fwDistanceIncrement = .1

# (Non-default) command keys.
# Keyboard is global from pandaepl.common
if 'Keyboard' in globals():
    keyboard = Keyboard.getInstance()
    keyboard.bind("close", ["escape", "q"])
    #keyboard.bind("exit", ["escape", "q"])
    #keyboard.bind("restart", "r")
    keyboard.bind("toggleDebug", ["escape", "d"])
    #keyboard.bind("increaseDist", ["shift", "up"])
    #keyboard.bind("decreaseDist", ["shift", "down"])
    keyboard.bind("increaseDist", "w")
    keyboard.bind("decreaseDist", "s")
    #keyboard.bind("increaseBananas", "w")
    #keyboard.bind("decreaseBananas", "s")
    keyboard.bind("increaseTouch", "e")
    keyboard.bind("decreaseTouch", "d")
    keyboard.bind("increaseInt", "u")
    keyboard.bind("decreaseInt", "j")
    keyboard.bind("changeLeft", "l")
    keyboard.bind("changeRight", "r")
    keyboard.bind("changeForward", "f")
    keyboard.bind("allowBackward", "b")
    keyboard.bind("pause", "p")
    keyboard.bind("reward", "space")
