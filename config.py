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
# for activating reward system
pulseInterval = 200 # in ms

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
#turningAcceleration = 130
turningAcceleration = 50
if training == 3.1:
    fullTurningSpeed = 0
elif training >= 2:
    #fullTurningSpeed = 55
    fullTurningSpeed = 35
#fullTurningSpeed = 20
else:
    fullTurningSpeed = 200
#turningLinearSpeed = 2  #Kiril has this as a factor,
# with min and max, eventually implement

# Point3 is global from panda3d.core
initialPos = Point3(0, 0, 1)

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

# Terrain, sky
terrainModel = './models/towns/field.bam'
terrainCenter = Point3(0, 0, 0)
skyModel = './models/sky/sky.bam'
skyScale = 1.6

# Eventually want landmarks in state, and load directory full of
# landmarks, randomly placed in background.

treeModel = './models/trees/palmTree.bam'
treeLoc = Point3(13, 13, 0)
treeScale = .0175

skyScraperModel = './models/skyscraper/skyscraper.bam'
skyScraperLoc = Point3(-13, -13, 0)
skyScraperScale = .3

stLightModel = './models/streetlight/streetlight.bam'
stLightLoc = Point3(-13, 13, 0)
stLightScale = .75

# bananarchy was using amill.bam, but I couldn't load that file,
# and the original amill.egg was not in the folder.
windmillModel = './models/windmill/amill.bam'
windmillLoc = Point3(13, -13, 0)
windmillScale = .2
windmillH = 45

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
