# configuration file for goBananas
from panda3d.core import Point3, Point4

# Set Training Level 
# See README for info about Training Levels
training = 5.2

# testing mode allows you to place 2 bananas in specific places,
# rather than having random placement of x bananas

testing = False

# Are we giving rewards?
reward = True

# Are we collecting eye data?
eyeData = False

# reward
numBeeps = 3
pulseInterval = 200 # in ms

# eye position calibration information
gain = (262, 236)  #(x, y)
offset = (-55, -46)  #(x,y)

#### Core PandaEPL settings ####

FOV = 60

# Movement
linearAcceleration = 30
if training >= 3:
	fullForwardSpeed = 2.8
else:
	fullForwardSpeed = 0
fullBackwardSpeed = 0
turningAcceleration = 130
if training == 3.1:
	fullTurningSpeed = 0
elif training >= 2:
	fullTurningSpeed = 55
else:
	fullTurningSpeed = 200
turningLinearSpeed = 2  #Kiril has this as a factor, with min and max, eventually implement

# Point3 is global from pandaepl.common
initialPos = Point3(0, 0, 1)
# If you want to collide with bananas at a closer or further distance, change this
#avatarRadius = 0.3
avatarRadius = 0.8

cameraPos = Point3(0, 0, 0)
friction = 0.4
movementType = 'walking' # car | walking

instructSize = 0.1
instructFont    = '/c/Windows/Fonts/times.ttf';
instructBgColor = Point4(0, 0, 0, 1)
instructFgColor = Point4(1, 1, 1, 1)
instructMargin  = 0.06
instructSeeAll  = False

# Experiment-specific settings

# Bananas.
bananaDir = './models/bananas/'
#bananaZ = 1
bananaScale = .5
#bananaRotation = 0  # Rotation speed in degrees/frame.
numBananas = 10
# how close is too close together?
tooClose = 0.5
# Bananas replenish after eating this many bananas.
#bananaReplenishment = 0
# Double the reward for the last banana in trial. 1=Yes; 0 = No.
#lastBananaBonus = 1

# Banana Positions
minDistance = -5
maxDistance = 5
minFwDistance = -5
maxFwDistance = 5
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
terrainCenter = Point3(0,0,0)
skyModel = './models/sky/sky.bam'
skyScale = 1.6

# Eventually want landmarks in state, and load directory full of
# landmarks, randomly placed in background.

treeModel     = './models/trees/palmTree.bam'
treeLoc       = Point3(13, 13, 0)
treeScale     = .0175

skyScraperModel= './models/skyscraper/skyscraper.bam'
skyScraperLoc  = Point3(-13, -13, 0)
skyScraperScale= .3

stLightModel= './models/streetlight/streetlight.bam'
stLightLoc  = Point3(-13, 13, 0)
stLightScale= .75

# bananarchy was using amill.bam, but I couldn't load that file,
# and the original amill.egg was not in the folder.
windmillModel = './models/windmill/amill.bam'
windmillLoc = Point3(13, -13, 0)
windmillScale = .2
windmillH = 45

# Load 2 bananas for testing, know where they are!
bananaModel = './models/bananas/banana.bam'
bananaLoc = Point3(10, 10, 1)
bananaScale = 0.5
bananaH = 0
bananaLoc2 = Point3(-10, -10, 1)

# (Non-default) command keys.
# Keyboard is global from pandaepl.common
if 'Keyboard' in globals():
    keyboard = Keyboard.getInstance()
    keyboard.bind("exit", ["escape", "q"])
    keyboard.bind("toggleDebug", ["escape", "d"])


