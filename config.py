# change individual config files, and have script copy to config.py
# configuration file for goBananas
from panda3d.core import Point3, Point4
from pandaepl import Keyboard


# Experiment-specific settings

# environ types available:
# 'original'
environ = 'original'
#environ = 'circle'

# Bananas.
#fruit = ['old_banana','cherry']
#num_fruit = [5, 5]
#num_beeps = [3, 5]
fruit = ['old_banana']
num_fruit = [10]
num_beeps = [4]

# factor to increase reward for last banana
extra = 2

# which fruit to make alpha, False for none (goBananas only)
go_alpha = 'old_banana'

# set how much alpha using for either recall or gobananas
# fully visible is 1, invisible is 0,
# in recall can adjust in 0.1 increments
alpha = 0.5

# how close is too close together?
tooClose = 1  # 1

# are we repeating a certain configuration of bananas?
# one of the first x banana configurations will be chosen
# at random to be repeated.
fruit_repeat = True

# How often to repeat the trial (will be one randomized
# within this number of trials)
repeat_number = 10

# Banana Positions
min_x = -10
max_x = 10
min_y = -10
max_y = 10

# used for placing bananas in circular environment
radius = 14

# toggle for adding training crosshair
crosshair = False

# Are we giving rewards?
reward = True
# reward = False

# Are we collecting eye data?
eyeData = True
# eyeData = False

# are we sending data to plexon or blackrock?
sendData = True
# sendData = False

# for activating reward system
pulseInterval = 200  # in ms still or goBananas

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

# 3d?
# framebuffer-stereo 1

#### Core PandaEPL settings ####

FOV = 60

# Movement
linearAcceleration = 30
fullForwardSpeed = 2.8
fullBackwardSpeed = 0
turningAcceleration = 130
fullTurningSpeed = 55
turningLinearSpeed = 2
maxTurningLinearSpeed = 90.0
minTurningLinearSpeed = 1.5
minTurningLinearSpeedIncrement = 0.5

# Point3 is global from panda3d.core
initialPos = Point3(0, 0, 1)

# If you want to collide with bananas at a closer or 
# further distance, change this, but does no good if 
# thing running into has huge radius
# avatarRadius = 0.3
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

# models are in goBananas directory by default
path_models = ''

# (Non-default) command keys.
# Keyboard is global from pandaepl.common
if 'Keyboard' in globals():
    keyboard = Keyboard.Keyboard.getInstance()
    keyboard.bind("close", ["escape", "q"])
    keyboard.bind("restart", "y")
    keyboard.bind("toggleDebug", ["escape", "d"])
    keyboard.bind("increase_reward", "w")
    keyboard.bind("decrease_reward", "s")
    keyboard.bind("increaseBananas", "e")
    keyboard.bind("decreaseBananas", "d")
    keyboard.bind("extra_reward", "space")
    keyboard.bind("changeWeightedCenter", "c")
