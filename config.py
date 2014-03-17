# change individual config files, and have script copy to config.py
# configuration file for goBananas
from panda3d.core import Point3, Point4

# Set Training Level 
# See README for info about Training Levels
training = 5.2

# are we using pydaq? Not available on the mac. Assume that if using pydaq,
# both collecting data and giving reward, but these are separate configs below,
# so could change individually, if desired.
pydaq = False

# testing mode allows you to place 2 bananas in specific places,
# rather than having random placement of x bananas

testing = False

# environ types available:
# 'training'
# 'original'
environ = 'original'

# set this if models is not in current directory
path_models = ''

if pydaq:
    # Are we giving rewards?
    reward = True
    # Are we collecting eye data?
    eyeData = True
else:
    reward = False
    eyeData = False

# 3d?
# framebuffer-stereo 1

# reward
numBeeps = 3
# factor to increase reward for last banana
extra = 2
# for activating reward system
pulseInterval = 200 # in ms

# eye position calibration information
# must be entered before every experiment from
# presentation callibration
gain = (262, 236)  #(x, y)
offset = (-55, -46)  #(x,y)

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
avatarRadius = 0.05

cameraPos = Point3(0, 0, 0)
friction = 0.4 #0.4
movementType = 'walking' # car | walking

instructSize = 0.1
instructFont = '/c/Windows/Fonts/times.ttf';
instructBgColor = Point4(0, 0, 0, 1)
instructFgColor = Point4(1, 1, 1, 1)
instructMargin = 0.06
instructSeeAll = False

# Experiment-specific settings

# Bananas.
numBananas = 10
#numBananas = 25
bananaDir = './models/bananas/'
#bananaZ = 1
bananaScale = .5
#bananaRotation = 0  # Rotation speed in degrees/frame.
# how close is too close together?
tooClose = 2.2  # 1.7

# Banana Positions
minDistance = -7
maxDistance = 7
minFwDistance = -7
maxFwDistance = 7
#fwDistanceIncrement = .1

# if not fully trained, do one banana at a time
#if (training > 0) and (training < 5):
#	numBananas = 1
#	distance = .15
#	bananaLocs[0] = [initialPos[0] - distance, initialPos[1] + 2, 90]

# Target Ray
#targetRayWindow = .45
#fovRayVecX = 30

# Target header window, to the left and right
#if (training > 2) & (training < 2.5):
#	targetHwinL = 4 - (((training - 2) * 10) - 1)
#	targetHwinR = 4 - (((training - 2) * 10) - 1)
#else:
#	targetHwinL = 2  #1.2 is sort of the boundary.
#	targetHwinR = 2  #1.2 is sort of the boundary.

# Load 2 bananas for testing, know where they are!
bananaModel = './models/bananas/banana.bam'
bananaLoc = Point3(5, 3, 1)
bananaScale = 0.5
bananaH = 0
bananaLoc2 = Point3(5.5, 3, 1)

# (Non-default) command keys.
# Keyboard is global from pandaepl.common
if 'Keyboard' in globals():
    keyboard = Keyboard.getInstance()
    keyboard.bind("close", ["escape", "q"])
    #keyboard.bind("exit", ["escape", "q"])
    keyboard.bind("restart", "y")
    keyboard.bind("toggleDebug", ["escape", "d"])
    keyboard.bind("upTurnSpeed", "t")
    keyboard.bind("downTurnSpeed", "g")
    keyboard.bind("increaseBananas", "w")
    keyboard.bind("decreaseBananas", "s")
