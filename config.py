# change individual config files, and have script copy to config.py
# configuration file for goBananas
from panda3d.core import Point3, Point4

# models are in goBananas directory by default
path_models = ''

# manual mode allows you to place up to 2 bananas in specific places,
# rather than having random placement of x bananas
manual = False

# remember_manual allows you to place the fruit to remember in a particular
# starting place. You may then use the j key to jump the fruit to a new
# location, and it will stay there until you jump again, as long as manual is
# set. If manual is not set, it is in a new, random location each trial.
remember_manual = False

# environ types available:
# 'original', 'circle'
environ = 'circle'

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
# probably shouldn't use this if using weighted bananas
# (just make it 1)
extra = 2

# are we repeating a certain configuration of bananas?
# one of the first x banana configurations will be chosen
# at random to be repeated.
fruit_repeat = False
# How often to repeat the trial (will be one randomized
# within this number of trials)
repeat_number = 10

# toggle for adding training crosshair
crosshair = False

# for activating reward system
pulseInterval = 200  # in ms

# eye position calibration information
# since we are getting voltage from IScan of -5:5
# gain of 100 gives us a range of 1000, which is
# close enough to the number of pixels we are using.
# if increase resolution beyond 1024, should probably
# adjust this
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
# fruit is set up as a list, in the case that there are multiple fruit types to be had
fruit = ['banana', 'plum']
num_fruit = [9, 1]  # number of fruit, other than fruit to remember or other special fruit

# for experiments where need to recall location, otherwise have fruit_to_remember set to None
#fruit_to_remember = 'banana'
fruit_to_remember = None
# how close to remembered location to get reward?
distance_goal = 1
# how close is too close together? Keep in mind that the distance is between the centers, but
# when you run into a fruit, you are not at the center, so could be closer than tooClose at that point
# Therefor, Too close should be at least as ar as the distance goal + 0.5
tooClose = 2  # 1

# Banana Positions
minXDistance = -10
maxXDistance = 10
minYDistance = -10
maxYDistance = 10

# Load bananas for testing, know where they are!
# theoretically can load as many as you want, but
# that becomes tedious.
# (no effect if manual False)
bananaModel = './models/bananas/banana.bam'
bananaLoc = [Point3(5, 3, 1), Point3(5.5, 3, 1)]
bananaScale = 0.5
bananaH = 0

# used for placing bananas in cicular environment
radius = 14

# (Non-default) command keys.
# Keyboard is global from pandaepl.common
if 'Keyboard' in globals():
    keyboard = Keyboard.getInstance()
    keyboard.bind("close", ["escape", "q"])
    keyboard.bind("restart", "y")
    keyboard.bind("toggleDebug", ["escape", "d"])
    keyboard.bind("increase_reward", "w")
    keyboard.bind("decrease_reward", "s")
    keyboard.bind("increaseBananas", "e")
    keyboard.bind("decreaseBananas", "d")
    keyboard.bind("extra_reward", "space")
    keyboard.bind("changeWeightedCenter", "c")
