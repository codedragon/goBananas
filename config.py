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
# 'original'
environ = 'original'
#environ = 'circle'

# Are we giving rewards?
reward = True
#reward = False

# Are we collecting eye data?
eyeData = True
#eyeData = False

# are we sending data to plexon or blackrock?
sendData = True
#sendData = False

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
# weighted bananas creates bananas of different rewards according to
# placement in the environment
weightedBananas = True
# Are we changing the location of the weights during the experiment?
# False or number of trials to go before switching
changeWeightLoc = False
high_reward = 7
mid_reward = 5
low_reward = 3

# for activating reward system
pulseInterval = 200  # in ms

# eye position calibration information
# since we are getting voltage from IScan of -5:5
# gain of 100 gives us a range of 1000, which is
# close enough to the number of pixels we are using.
# if increase resolution beyond 1024, should probably
# adjust this

# increased resolution to 1280, 800, so increased x gain
# to 150 to give us 1500 max pixels.
gain = (150, 100)  # (x, y)
offset = (1, 1)  # (x,y)

#### Core PandaEPL settings ####

FOV = 60

# Movement
linearAcceleration = 8
fullForwardSpeed = 2.8
fullBackwardSpeed = 0
turningAcceleration = 130
# game is normally at 55
fullTurningSpeed = 30
turningLinearSpeed = 2
maxTurningLinearSpeed = 90.0
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
numBananas = 200
#numBananas = 25
bananaDir = './models/bananas/'
#bananaZ = 1
bananaScale = .6
#bananaRotation = 0  # Rotation speed in degrees/frame.
# how close is too close together?
tooClose = 1  # 1

# Banana Positions
minXDistance = -10
maxXDistance = 10
minYDistance = -10
maxYDistance = 10

# banana positions if using circle environment
radius = 14

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
    keyboard.bind("extra_reward", "space")
