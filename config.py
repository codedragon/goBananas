# configuration file for goBananas

# Set Training Level
# 5.2 - fully trained
# >= 3 fullForwardSpeed = 2.8
# < 3 fullForwardSpeed = 0
training = 5.2

#### Core PandaEPL settings ####

FOV = 60

if training >= 3:
	fullForwardSpeed = 2.8
else:
	fullForwardSpeed = 0

fullBackwardSpeed = 0
if training == 3.1:
	fullTurningSpeed = 0
elif training >= 2:
	fullTurningSpeed = 55
else:
	fullTurningSpeed = 200

# Point3 is global from pandaepl.common
initialPos = Point3(0, 0, 1)