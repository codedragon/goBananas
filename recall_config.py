# change individual config files, and have script copy to config.py
# configuration file for goBananas
from panda3d.core import Point3, Point4
from pandaepl import Keyboard

# Experiment-specific settings

# environ types available:
# 'original', 'circle'
# environ = 'circle'
environ = 'original'

# fruit is set up as a list, in the case that there are multiple fruit types to be had
# for recallBanana, this list does NOT include the recall fruit
fruit = ['cherry']
num_fruit = [1]
# for bananaRecall, first number is for recall fruit, second for all other fruit
num_beeps = [8, 2]
# num_beeps = [3, 5]

# RecallBanana configurations
# for experiments where need to recall location, otherwise have fruit_to_remember set to None
fruit_to_remember = 'old_banana'
auto_pilot = True
# fruit_to_remember = None
# how close to remembered location to get reward?
distance_goal = [3, 3]
manual = True  # using pre-configured locations, False: use random locations (either way can specify sub-area)
repeat_recall_fruit = False  # can be toggled with key, repeats location
time_to_recall = 120  # number of seconds to get to remembered location
time_to_flash = 0  # number of seconds to flash fruit, zero for no flashing
# for training, fruit_to_remember location can be limited to a small area of the courtyard
# (areas arranged same as numbers on keypad), zero means can be anywhere
# if manual is true, this specifies a particular position in this subarea, otherwise
# random location in this area
# to use the whole area, use subarea 10
subarea = 6  # this is the starting spot, can be changed by a keypress later on
# once trained, alpha will be at zero, no banana showing
# can use this to set specific area for alternate fruit to show up. if not set, alternate
# fruit can show up anywhere except the subarea where the recall fruit is. List
# alt_subarea = [3]
# if alpha is greater than zero in config, when recall fruit moves to a new area will automatically
# be at this alpha again until changed.
alpha = 0.1  # this is for training in the recall task. fully visible is 1, invisible is 0
first_fruit_alpha = False  # make the first recall fruit (after solids) be alpha, even
# if using invisible for last trial
# how many times to repeat the recall fruit at full visible before
# subject has to remember where the fruit is.
num_repeat_visible = 1
points = {1: (-9.5, -9.5),
          2: (0, -9.5),
          3: (9.5, -9.5),
          4: (-9.5, 0),
          5: (0, 0),
          6: (9.5, 0),
          7: (-9.5, 9.5),
          8: (0, 9.5),
          9: (9.5, 9.5)}

# which fruit to make alpha, False for none (goBananas only)
go_alpha = False

# factor to increase reward for last banana
# in bananaRecall, this is how much extra subject gets for remembered banana
# (multiplied by lowest number in num_beeps)
extra = 2

# are we repeating a certain configuration of fruit?
# one of the first x banana configurations will be chosen
# at random to be repeated. not implemented for recall, see
# below for recall options
# fruit_repeat = True
fruit_repeat = False
# How often to repeat the trial (will be one randomized
# within this number of trials)
repeat_number = 3

# Are we giving rewards?
reward = True
# reward = False

# Are we collecting eye data?
# eyeData = True
eyeData = True

# are we sending data to plexon or blackrock?
# sendData = True
sendData = True

# 3d?
# framebuffer-stereo 1

# toggle for adding training crosshair
crosshair = False

# for activating reward system (ms)
pulseInterval = 200

# models are in goBananas directory by default
path_models = ''

# eye position calibration information
# since we are getting voltage from IScan of -5:5
# gain of 100 gives us a range of 1000, which is
# close enough to the number of pixels we are using.
# if increase resolution beyond 1024, should probably
# adjust this
gain = (150, 100)  # (x, y)
offset = (1, 1)  # (x, y)

# ### Core PandaEPL settings ####

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
    keyboard.bind("override_alpha", "a")
    keyboard.bind("increase_dist_goal", "t")
    keyboard.bind("decrease_dist_goal", "g")
    keyboard.bind("toggle_manual", "m")
    keyboard.bind("toggle_repeat", "r")
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
