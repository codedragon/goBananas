# configuration file for goBananas
from random import uniform
# Set Training Level
# 5.2 - fully trained
# 3.1   fullTurningSpeed = 0
# >= 3  fullForwardSpeed = 2.8
# < 3   fullForwardSpeed = 0
# >= 2  fullTurningSpeed = 55
# < 2   fullTurningSpeed = 200
training = 5.2

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
avatarRadius = 0.3
cameraPos = Point3(0, 0, 0)
friction = 0.4
movementType = 'walking' # car | walking

# Experiment-specific settings

# Bananas.
bananaDir = './models/bananas/'
bananaZ = 1
bananaScale = .5
bananaRotation = 0  # Rotation speed in degrees/frame.
numBananas = 10
# Bananas replenish after eating this many bananas.
bananaReplenishment = 0
# Double the reward for the last banana in trial. 1=Yes; 0 = No.
lastBananaBonus = 1

# Banana Positions
bananaLocs = []
minDistance = -5
maxDistance = 5
minFwDistance = -5
maxFwDistance = 5
fwDistanceIncrement = .1

for i in range(0, numBananas):
	x = uniform(minDistance, maxDistance)
	y = uniform(minFwDistance, maxFwDistance)
	bananaLocs.append([x, y, 90])

if (training > 0) and (training < 5):
	numBananas = 1
	distance = .15
	bananaLocs[0] = [initialPos[0] - distance, initialPos[1] + 2, 90]

# Target Ray
targetRayWindow = .45
fovRayVecX = 30

# Target header window, to the left and right
if (training > 2) & (training < 2.5):
	targetHwinL = 4 - (((training - 2) * 10) - 1)
	targetHwinR = 4 - (((training - 2) * 10) - 1)
else:
	targetHwinL = 2  #1.2 is sort of the boundary.
	targetHwinR = 2  #1.2 is sort of the boundary.

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
windmillModel = './models/windmill/windmill.bam'
windmillLoc = Point3(13, -13, 0)
windmillScale = .2
windmillH = 45

# (Non-default) command keys.
# Keyboard is global from pandaepl.common
keyboard = Keyboard.getInstance()
keyboard.bind("exit", ["escape", "q"])
keyboard.bind("toggleDebug", ["escape", "d"])
keyboard.bind("left", "l")
keyboard.bind("right", "r")

