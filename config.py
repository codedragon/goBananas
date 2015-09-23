# change individual config files, and have script copy to config.py
# configuration file for goBananas
from panda3d.core import Point3, Point4
from pandaepl import Keyboard


# Experiment-specific settings

# environ types available:
environ = 'narrow'
# environ = 'original'
# environ = 'circle'

# Bananas.
# fruit = ['old_banana','cherry']
# num_fruit = [5, 5]
# num_beeps = [3, 5]
fruit = ['old_banana']
num_fruit = [5]
num_beeps = [10]
fruit_dict = {'old_banana000': (0, -7.8),
              'old_banana001': (0, 7.8)}

# fruit_dict = {'old_banana008': (1.0308523924023465, 2.696501626688711), 
# 	'old_banana009': (-0.8415660617180905, 8.517858840690405), 
# 	'old_banana006': (-7.840797155108468, 6.988693437399192), 
# 	'old_banana007': (-7.570439700755076, 1.638789689558127), 
# 	'old_banana004': (-8.39561713487198, -3.3586250946766283), 
# 	'old_banana005': (-5.393856172370732, -4.211553443023264), 
# 	'old_banana002': (-9.824605435042828, -9.058700527886014), 
# 	'old_banana003': (5.012920228098546, -4.492073778058923), 
# 	'old_banana000': (-7.920266364380111, -0.7079936339602284), 
# 	'old_banana001': (-2.6398400012779843, 8.638750166559326)}
# fruit_dict = {}

# factor to increase reward for last banana
extra = 1.5

# which fruit to make alpha, False for none (goBananas only)
# go_alpha = 'old_banana'

# set how much alpha using for either recall or gobananas
# fully visible is 1, invisible is 0,
# in recall can adjust in 0.1 increments
alpha = 0.2

# how close is too close together?
tooClose = 2  # 1

# are we repeating a certain configuration of bananas?
# one of the first x banana configurations will be chosen
# at random to be repeated.
# this must be true if using manual positions, in which
# case repeat_number is ignored, and manual positions are
# always used
fruit_repeat = True

# How often to repeat the trial (will be one randomized
# within this number of trials)
repeat_number = 10

# Banana Positions
min_x = -0.1
max_x = 0.1
min_y = -6
max_y = 6

# used for placing bananas in circular environment
radius = 14

# toggle for adding training crosshair
crosshair = False

# Are we giving rewards?
# reward = True
reward = False

# Are we collecting eye data?
# eyeData = True
eyeData = False

# are we sending data to plexon or blackrock?
# sendData = True
sendData = False

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
linearAcceleration = 20
fullForwardSpeed = 1
fullBackwardSpeed = 0
turningAcceleration = 130
fullTurningSpeed = 55
turningLinearSpeed = 2
maxTurningLinearSpeed = 90.0
minTurningLinearSpeed = 1.5
minTurningLinearSpeedIncrement = 0.5

# Point3 is global from panda3d.core
initialPos = Point3(0, -7.5, 1)

# If you want to collide with bananas at a closer or 
# further distance, change this, but does no good if 
# thing running into has huge radius
# avatarRadius = 0.3
avatarRadius = 0.1

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
    keyboard.bind("increase_reward", "w")
    keyboard.bind("decrease_reward", "s")
    keyboard.bind("increase_bananas", "e")
    keyboard.bind("decrease_bananas", "d")
    keyboard.bind("extra_reward", "space")
    keyboard.bind("override_alpha", "a")
