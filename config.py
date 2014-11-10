# change individual config files, and have script copy to config.py
# configuration file for goBananas
from panda3d.core import Point3, Point4
from pandaepl import Keyboard

# models are in goBananas directory by default

path_models = ''

# environ types available:
# 'original', 'circle'
#environ = 'circle'
environ = 'original'

# Are we giving rewards?
reward = True
#reward = False

# Are we collecting eye data?
#eyeData = True
eyeData = True

# are we sending data to plexon or blackrock?
#sendData = True
sendData = True

# 3d?
# framebuffer-stereo 1

# reward
numBeeps = 10
# factor to increase reward for last banana
# probably shouldn't use this if using weighted bananas
# (just make it 1)
extra = 2

# are we repeating a certain configuration of fruit?
# one of the first x banana configurations will be chosen
# at random to be repeated. not implemented for recall, see
# below for recall options
#fruit_repeat = True
fruit_repeat = False

# How often to repeat the trial (will be one randomized
# within this number of trials)
repeat_number = 3

# toggle for adding training crosshair
crosshair = False

# for activating reward system
pulseInterval = 0.200  # in s

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
linearAcceleration = 30
fullForwardSpeed = 2.8
fullBackwardSpeed = 0
turningAcceleration = 130
# game is normally at 55
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
#fruit = ['plum']
fruit = ['plum']
num_fruit = [1]
#fruit = ['old_banana', 'plum']  # the fruit_to_remember should NOT be part of this list
#num_fruit = [9, 1]  # number of fruit, other than fruit to remember or other special fruit

# for experiments where need to recall location, otherwise have fruit_to_remember set to None
fruit_to_remember = 'banana'
#fruit_to_remember = None
# how close to remembered location to get reward?
distance_goal = 3
repeat_recall_fruit = True  # can be toggled with key, repeats location
time_to_recall = 10  # number of seconds to get to remembered location
time_to_flash = 0  # number of seconds to flash fruit, zero for no flashing
# for training, fruit_to_remember location can be limited to a small area of the courtyard
# (areas arranged same as numbers on keypad), zero means can be anywhere
subarea = 9  # this is the starting spot, can be changed by a keypress later on
# once trained, alpha will be at zero, no banana showing
alpha = 0.9  # this is for training in the recall task. fully visible is 1, invisible is 0

# how close is too close together for fruit and avatar? Keep in mind that the distance is between the centers, but
# when you run into a fruit, you are not at the center, so could be closer than tooClose at that point
# Therefor, Too close should be at least 1. For recall, it should be at least as far as the distance goal, so
# you don't get a fruit right next to where the recall fruit was and just automatically get a reward
tooClose = 3  # 1

# Banana Positions
min_x = -10
max_x = 10
min_y = -10
max_y = 10

# used for placing bananas in circular environment
radius = 14

# (Non-default) command keys.
# Keyboard is global from pandaepl.common
if 'Keyboard' in globals():
    keyboard = Keyboard.Keyboard.getInstance()
    keyboard.bind("close", ["escape", "q"])
    keyboard.bind("increase_reward", "w")
    keyboard.bind("decrease_reward", "s")
    keyboard.bind("extra_reward", "space")
    keyboard.bind("increase_alpha", "e")
    keyboard.bind("decrease_alpha", "d")
    keyboard.bind("toggle_random", "r")
    keyboard.bind("subarea_1", "1")
    keyboard.bind("subarea_2", "2")
    keyboard.bind("subarea_3", "3")
    keyboard.bind("subarea_4", "4")
    keyboard.bind("subarea_5", "5")
    keyboard.bind("subarea_6", "6")
    keyboard.bind("subarea_7", "7")
    keyboard.bind("subarea_8", "8")
    keyboard.bind("subarea_9", "9")
    keyboard.bind("subarea_0", "0")
