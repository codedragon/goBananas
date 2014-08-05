# change individual config files, and have script copy to config.py
# configuration file for goBananas
from panda3d.core import Point3, Point4

# Set Training Level 
# See README for info about Training Levels
training = 5.2

# models are in goBananas directory by default
path_models = ''
# manual mode allows you to place up to 2 bananas in specific places,
# rather than having random placement of x bananas
manual = False

# environ types available:
# 'training'
# 'original'
environ = 'original'
# Are we giving rewards?
reward = True
#reward = False

# Are we collecting eye data?
#eyeData = True
eyeData = False

# are we sending data to plexon or blackrock?
#sendData = True
sendData = False

# 3d?
# framebuffer-stereo 1

# reward
numBeeps = 3
# factor to increase reward for last banana
extra = 2

# are we repeating a certain configuration of bananas?
# one of the first x banana configurations will be chosen
# at random to be repeated.
bananaRepeat = False
# How often to repeat the trial (will be one randomized
# within this number of trials)
repeatNumber = 10

# Are bananas in different areas worth more/less?
weightedBananas = True
high_reward = 6
mid_reward = 4
low_reward = 2

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
# pretty sure some of these are from bananarchy, and
# aren't used in pandaepl, check this out
linearAcceleration = 30
fullForwardSpeed = 2.8
fullBackwardSpeed = 0
turningAcceleration = 130
fullTurningSpeed = 55
turningLinearSpeed = 2
maxTurningLinearSpeed = 90.0
minTurningLinearSpeedReqd = 1.0
minTurningLinearSpeed = 1.5
minTurningLinearSpeedIncrement = 0.5

# Point3 is global from panda3d.core
initialPos = Point3(0, -8, 1)

# If you want to collide with bananas at a closer or 
# further distance, change this, but does no good if 
# thing running into has huge radius
#avatarRadius = 0.3
avatarRadius = 0.2

cameraPos = Point3(0, 0, 0)
friction = 0.4  # 0.4
movementType = 'walking'  # car | walking

instructSize = 0.1
instructFont = '/c/Windows/Fonts/times.ttf'
instructBgColor = Point4(0, 0, 0, 1)
instructFgColor = Point4(1, 1, 1, 1)
instructMargin = 0.06
instructSeeAll = False

# Experiment-specific settings

# Bananas.
numBananas = 99
#numBananas = 25
bananaDir = './models/bananas/'
#bananaZ = 1
bananaScale = .5
#bananaRotation = 0  # Rotation speed in degrees/frame.
# how close is too close together?
tooClose = 1  # 1

# Banana Positions
minDistance = -10
maxDistance = 10
minFwDistance = -10
maxFwDistance = 10

# Load 2 bananas for testing, know where they are!
# (no effect if manual False)
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
    keyboard.bind("restart", "y")
    keyboard.bind("toggleDebug", ["escape", "d"])
    keyboard.bind("upTurnSpeed", "t")
    keyboard.bind("downTurnSpeed", "g")
    keyboard.bind("increaseBananas", "w")
    keyboard.bind("decreaseBananas", "s")
