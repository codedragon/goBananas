from __future__ import division
from direct.showbase.ShowBase import ShowBase
from joystick import JoystickHandler
from panda3d.core import Point3, Point4, BitMask32
from panda3d.core import TextNode, WindowProperties
from panda3d.core import CollisionNode, CollisionRay, CollisionSphere
from panda3d.core import CollisionTraverser, CollisionHandlerQueue
import random
import sys
import os
import datetime
# only load pydaq if it's available
try:
    sys.path.insert(1, '../pydaq')
    import pydaq
    PYDAQ_LOADED = True
    # print 'loaded PyDaq'
except ImportError:
    pydaq = None
    PYDAQ_LOADED = False
    sys.stdout.write('Not using PyDaq \n')


class TrainingBananas(JoystickHandler):
    def __init__(self):
        """
        Initialize the experiment
        """
        pydaq_loaded = PYDAQ_LOADED
        self.base = ShowBase()
        config = {}
        execfile('train_config.py', config)
        if not unittest:
            JoystickHandler.__init__(self)
        self.base.disableMouse()
        sys.stdout.write('Subject is ' + str(config['subject']) + '\n')
        self.subject = config['subject']
        self.levels_available = [[2, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6], [3, 3.1], [4, 4.1, 4.2]]

        # set up reward system
        # if unit-testing, pretend like we couldn't
        # load the module
        if unittest:
            pydaq_loaded = False
        if config['reward'] and pydaq_loaded:
            self.reward = pydaq.GiveReward()
        else:
            self.reward = None
            sys.stdout.write('Warning: reward system not on \n')

        # setup windows
        if not unittest:
            # if doing unittests, there is no window
            wp = WindowProperties()
            # wp.setSize(1280, 800)
            wp.setSize(1024, 768)
            wp.setOrigin(0, 0)
            wp.setCursorHidden(True)
            self.base.win.requestProperties(wp)
            # base.setFrameRateMeter(True)
            # initialize training file name
            self.data_file_name = ''
            self.data_file = None
            self.open_data_file(config)

        # Get initial direction, only matters for manual, random will override later
        # for bananas, changing the angle from avatar to banana, so left is negative
        # right is positive.
        if config['trainingDirection'] == 'Right':
            self.multiplier = 1
        elif config['trainingDirection'] == 'Left':
            self.multiplier = -1
        # print config['trainingDirection']
        self.last_multiplier = self.multiplier

        # get more variables from configuration
        self.side_bias = config['random_bias']
        # bring some configuration parameters into memory, so we don't need to
        # reload the config file multiple times, also allows us to change these
        # variables dynamically
        self.num_beeps = config['numBeeps']
        # not changing now, but may eventually...
        self.x_alpha = config['xHairAlpha']
        self.reward_time = config['pulseInterval']  # usually 200ms
        # amount need to hold crosshair on banana to get reward (2.3)
        # must be more than zero. At 1.5 distance, must be greater than
        # 0.5 to require stopping
        self.hold_aim = config['hold_aim']
        self.initial_speed = config['initial_turn_speed']
        self.initial_forward_speed = config['initial_forward_speed']
        self.forward_limit = config['forward_limit']
        self.training = config['training']
        if not unittest:
            sys.stdout.write('training level: ' + str(self.training) + '\n')
            if self.training < 2.2:
                sys.stdout.write('starting direction: ' + str(config['trainingDirection']) + '\n')
        # random selection used for training 2.3 and above
        self.all_random_selections = config['random_lists']
        self.current_choice = config['random_selection'] - 1
        self.random_choices = self.all_random_selections[self.current_choice]

        # Setup Graphics
        # bitmasks for collisions
        ray_mask = BitMask32(0x1)
        sphere_mask = BitMask32(0x2)
        self.mask_list = [ray_mask, sphere_mask, ray_mask | sphere_mask]
        if config['background']:
            field = self.base.loader.loadModel("models/play_space/field.bam")
            field.setPos(Point3(0, 0, 0))
            field.reparentTo(self.base.render)
            field_node_path = field.find('**/+CollisionNode')
            field_node_path.node().setIntoCollideMask(0)
            sky = self.base.loader.loadModel("models/sky/sky.bam")
            sky.setPos(Point3(0, 0, 0))
            sky.reparentTo(self.base.render)

        # set up banana
        self.banana = None
        self.banana_mask = None
        self.banana_node_path = None
        self.banana_coll_node = None
        self.load_fruit(config.get('fruit', 'banana'))

        # set up collision system and collision ray to camera
        self.base.cTrav = CollisionTraverser()
        self.collHandler = CollisionHandlerQueue()
        ray_node = self.base.camera.attachNewNode(CollisionNode('CrossHairRay'))
        # ray that comes straight out from the camera
        ray_solid = CollisionRay(0, 0, 0, 0, 1, 0)
        self.ray_node_path = self.make_coll_node_path(ray_node, ray_solid)
        self.ray_node_path.node().setIntoCollideMask(0)
        self.ray_node_path.node().setFromCollideMask(ray_mask)

        # add collision sphere to camera
        sphere_node = self.base.camera.attachNewNode(CollisionNode('CollisionSphere'))
        # camera_sphere = CollisionSphere(0, 0, 0, 1.3)
        # avatar_radius = 0.3
        avatar_radius = 1
        camera_sphere = CollisionSphere(0, 0, 0, avatar_radius)
        self.sphere_node_path = self.make_coll_node_path(sphere_node, camera_sphere)
        self.sphere_node_path.node().setIntoCollideMask(0)
        self.sphere_node_path.node().setFromCollideMask(sphere_mask)

        # into collide masks are set with level variables, since we change
        # whether between using the sphere or the ray for detecting collisions,
        # depending on which level we are on.

        self.base.cTrav.addCollider(self.ray_node_path, self.collHandler)
        self.base.cTrav.addCollider(self.sphere_node_path, self.collHandler)
        # self.base.cTrav.showCollisions(self.base.render)
        self.ray_node_path.show()
        self.sphere_node_path.show()
        self.banana_node_path.show()
        self.base.render.find('**/+CollisionNode').show()

        # Camera
        self.base.camLens.setFov(60)

        # set avatar position/heading
        # Default positions
        self.avatar_pos = Point3(0, -1.5, 1)
        self.avatar_h = 0
        self.screen_edge = 30
        self.config_avatar_d = -config['avatar_start_d']
        self.config_avatar_h = config['avatar_start_h']

        # Cross hair
        # color changes for crosshair
        self.x_start_c = Point4(1, 1, 1, self.x_alpha)
        self.x_stop_c = Point4(1, 0, 0, self.x_alpha)
        self.crosshair = TextNode('crosshair')
        self.crosshair.setText('+')
        text_node_path = self.base.aspect2d.attachNewNode(self.crosshair)
        text_node_path.setScale(0.2)
        # crosshair is always in center, but
        # need it to be in same place as collisionRay is, but it appears that center is
        # at the bottom left of the collisionRay, and the top right of the text, so they
        # don't have center in the same place. Makes more sense to move text than ray.
        # These numbers were scientifically determined. JK, moved around until the cross looked
        # centered on the ray
        # crosshair_pos = Point3(0, 0, 0)
        # crosshair_pos = Point3(-0.07, 0, -0.05)
        crosshair_pos = Point3(-0.055, 0, -0.03)

        # print text_node_path.getPos()
        text_node_path.setPos(crosshair_pos)

        # set level
        # setup variables related to training levels
        # initialize training variables
        # will be set to proper levels in set_level_variables method
        self.free_move = 0
        self.must_release = False
        self.random_banana = False
        self.require_aim = False
        self.go_forward = False
        #self.set_level_variables(self.training)

        # setup keyboard/joystick inputs
        self.setup_inputs()
        # Initialize more variables

        # These variables are set to their initial states in reset_variables, so
        # does not matter what they are set to here.
        # DO NOT SET VARIABLES HERE, GO TO RESET_VARIABLES!!!
        # variable used to notify when changing direction of new target
        self.new_dir = None
        # and variable to notify when changing levels
        self.change_level = False
        self.max_angle = None
        self.min_angle = None
        self.delay_start = False
        self.yay_reward = False
        self.reward_delay = False
        self.reward_on = True
        self.reward_count = 0
        self.x_mag = 0
        self.y_mag = 0
        self.speed = self.initial_speed  # factor to slow down movement of joystick and control acceleration
        # speed for going in the wrong direction, when same speed as initial speed, then no change
        self.forward_speed = self.initial_forward_speed
        self.wrong_speed = 0.005
        self.slow_speed = self.wrong_speed
        # toggle for whether moving is allowed or not
        self.moving = True
        # toggle for making sure stays on banana for min time for 2.3
        self.set_zone_time = False
        # keeps track of how long we have held
        self.hold_time = 0
        self.check_zone = False
        # self.check_time = 0
        # toggle for when trial begins
        self.start_trial = True
        # print self.avatar_h
        # print self.base.camera.getH()
        # print self.avatar_pos
        # print self.base.camera.getPos()
        # print self.base.camLens.getFov()
        # print self.base.camLens.getNear()
        # print self.base.camLens.getFar()
        # print self.base.camLens.getAspectRatio()
        self.base.camLens.setNear(avatar_radius/3.0)
        # print self.banana.getPos()
        # set variables to their actual starting values
        self.reset_variables()
        self.set_level_variables(self.training)
        print 'set level'
        self.set_camera()
        print 'set camera'
        # start stuff happening!
        self.frameTask = self.base.taskMgr.add(self.frame_loop, "frame_loop")
        self.frameTask.delay = -0.1  # want initial delay less than zero
        self.frameTask.last = 0  # task time of the last frame
        print 'set task'
        if not unittest:
            self.data_file.write(str(self.frameTask.time) + ', ' +
                                 'banana position, ' +
                                 str(self.multiplier * self.avatar_h) + '\n')

    def frame_loop(self, task):
        # print self.training
        # print 'loop'
        dt = task.time - task.last
        task.last = task.time
        # print('dt', dt)
        # delay_start means we just gave reward and need to set wait
        # until reward pump is done to do anything
        if self.delay_start:
            task.delay = task.time + self.reward_time
            # print('time now', task.time)
            # print('delay until', task.delay)
            self.delay_start = False
            # self.reward_delay = True
            return task.cont
        # set_zone_time means we have the crosshair over the banana,
        # and have to set how long to leave it there
        if self.set_zone_time:
            # print 'reset zone time'
            self.hold_time = task.time + self.hold_aim
            self.set_zone_time = False
            self.check_zone = True
        # reward delay is over, on to regularly scheduled program
        if task.time > task.delay:
            # print 'past delay'
            # check for reward
            # print('beeps so far', self.reward_count)
            # print self.yay_reward
            if self.yay_reward == 'partial':
                # print 'giving partial reward'
                self.give_reward()
                self.yay_reward = None
                self.go_forward = True
                # since none, don't need to return, won't give more reward, but
                # will go on to let move
            elif self.yay_reward and self.reward_count < self.num_beeps:
                # print 'gave reward'
                self.reward_count += 1
                self.give_reward()
                return task.cont
            elif self.yay_reward and self.reward_count == self.num_beeps:
                # print 'gave final reward'
                # done giving reward, time to start over, maybe
                # hide the banana
                self.banana.stash()
                # change the color of the crosshair
                self.x_change_color(self.x_start_c)
                # before we can proceed, subject may need to let go of the joystick
                if self.must_release:
                    # print 'checking for release'
                    # print self.x_mag
                    if abs(self.x_mag) > 0 or abs(self.y_mag) > 0:
                        # print('let go!')
                        return task.cont
                # and now we can start things over again
                # print('start over')
                self.restart_bananas()
                # check_time is used to see how long it takes subject
                # to get banana from time plotted
                # self.check_time = task.time
                return task.cont
            # check to see if we are moving
            if self.moving:
                # moving, forward first, only bother checking if possible to go forward
                if self.go_forward:
                    # forward needs a little speed boost compared to turning
                    if self.start_trial or self.y_mag == 0:
                        self.forward_speed = self.initial_forward_speed
                        self.start_trial = False
                    else:
                        # self.y_mag (how much you push the joystick) affects
                        # acceleration as well as speed
                        self.forward_speed += self.initial_forward_speed * abs(self.y_mag)
                    position = self.base.camera.getPos()
                    # print(position)
                    # print('y_mag', self.y_mag)
                    # print('speed', self.speed)
                    # print('dt', dt)
                    # print('change in position', self.y_mag * self.speed * dt)
                    position[1] += self.y_mag * self.forward_speed * dt
                    # if this puts us past center, stay at center
                    if position[1] > 0:
                        position[1] = 0
                    self.base.camera.setPos(position)
                # Now check for rotation. Don't need to check this if going forward
                if not self.go_forward:
                    # print 'rotating'
                    heading = self.base.camera.getH()
                    delta_heading = self.get_new_heading(heading, dt)
                    self.base.camera.setH(heading + delta_heading)
                    # print('camera heading', self.base.camera.getH())
                # check for collision:
                collide_banana = self.check_banana()
                # print('collide', collide_banana)
                # if we need to be stopping and leaving (holding) crosshair over banana,
                # make sure still in target zone.
                if self.check_zone:
                    # print('check hold')
                    # not sure if I will use a zone for going forward yet
                    # The 'zone' is whenever the ray is colliding with the banana.
                    # use zone for both left-right training and for forward training,
                    # whenever self.require_aim is true.
                    # with forward training, use to see if we went off course, and then
                    # lined up the crosshair and banana again.
                    # print collide_banana
                    if collide_banana:
                        # print('still in the zone')
                        if task.time > self.hold_time:
                            # print('hold aim', self.hold_aim)
                            # print('ok, get reward')
                            # print self.free_move
                            # print('hold time', task.time > self.hold_time)
                            # stop moving and get reward
                            if self.free_move == 4:
                                # partial reward for lining up banana in level 4.x
                                # print 'partial reward'
                                self.yay_reward = 'partial'
                                self.check_zone = False
                            elif self.yay_reward is not None:
                                self.x_change_color(self.x_stop_c)
                                self.moving = False
                                self.yay_reward = True
                                self.check_zone = False
                        else:
                            pass
                            # print('keep holding')
                            # print('time', task.time)
                            # print('hold until', self.hold_time)
                    else:
                        # print('left zone, wait for another collision')
                        self.x_change_color(self.x_start_c)
                        # print('require aim', self.require_aim)
                        if self.require_aim == 'slow':
                            # print 'aim slow'
                            self.check_zone = None
                        else:
                            # print "don't slow down"
                            self.check_zone = False
                else:
                    # not currently checking zone, so either collide_banana means reward immediately
                    # or start timer to check if leaving zone
                    # print('camera heading before collision', self.base.camera.getH())
                    if collide_banana:
                        # print('time took: ', task.time - self.check_time)
                        # print 'collision'
                        # print 'change xhair color to red'
                        self.x_change_color(self.x_stop_c)
                        # if we require aim, we start timer when we have a collision,
                        # but if self.go_forward, than we have already aimed.
                        if self.require_aim and not self.go_forward:
                            self.set_zone_time = True
                        else:
                            # print 'yes'
                            # reward time!
                            # stop moving
                            self.moving = False
                            # move to center
                            if self.base.camera.getH != 0:
                                pass
                                # print 'moved camera'
                                # self.base.camera.setH(0)
                            self.yay_reward = True
                    elif collide_banana is None:
                        # partial reward for lining up banana in level 4.x
                        # print 'partial reward'
                        self.yay_reward = 'partial'
                        # self.yay_reward = True
                        # self.reward_count = self.num_beeps - 1
        return task.cont

    def give_reward(self):
        # print('beep')
        if self.reward:
            self.reward.pumpOut()
        if not unittest:
            self.data_file.write(str(self.frameTask.time) + ', ' +
                                 'reward' + '\n')
        self.delay_start = True

    def check_banana(self):
        # print 'check banana'
        collide_banana = False
        # print self.base.camera.getPos()
        # if we are doing only forward, or only side, only need to check for entries,
        # but if doing both movement, have to check for whichever we are currently
        # interested in.
        if self.free_move == 4:
            # why doesn't the camera show that we see the banana, ever? wrong camera?
            # print self.base.camNode.isInView(self.banana.getPos())
            for i in range(self.collHandler.getNumEntries()):
                entry = self.collHandler.getEntry(i)
                # in_view = self.base.camNode.isInView(entry.getIntoNodePath().getPos())
                # print in_view
                # print entry.getIntoNodePath().getPos()
                if entry.getFromNodePath() == self.sphere_node_path:
                    # print 'ran into banana going forward'
                    collide_banana = True
                    self.moving = False
                elif entry.getFromNodePath() == self.ray_node_path:
                    # print 'collide ray'
                    # print self.yay_reward
                    # if we are requiring aim, than use collide_banana = True,
                    # since this will automatically get diverted before full reward
                    if self.yay_reward is not None and not self.require_aim:
                        # print 'lined up banana from side'
                        collide_banana = None
                    elif self.yay_reward is not None and self.require_aim:
                        # print 'lined up banana from side, need to aim'
                        collide_banana = True
                # print entry.getFromNodePath()
        elif self.collHandler.getNumEntries() > 0:
            # print 'collided'
            # the only object we can be running into is the banana, so there you go...
            collide_banana = True
            # print self.collHandler.getEntries()
            # print self.base.camera.getH()
            # print self.base.camera.getPos()
            # print self.banana.getPos()
        return collide_banana

    def restart_bananas(self):
        # print 'restarted'
        # print('training', self.training)
        # reset a couple of variables
        self.yay_reward = False
        self.reward_count = 0
        # self.check_time = 0
        # used to reset speed
        self.start_trial = True
        # print self.multiplier
        # check to see if we are switching the banana to the other side
        if self.new_dir is not None:
            self.multiplier = self.new_dir
            self.new_dir = None
            # for some versions, subject could still be holding joystick at this point.
            # (for example, was going to the right, but now is suppose to be going to the left,
            # but since we only detect when the joystick position has changed, and it has
            # not, may not realize that that we are now going what is considered a 'wrong' direction
            # so we are essentially re-checking the the joystick position, given the other updated
            # parameters).
            # send the current joystick position through the move method to correct that.
            # the original signal had its sign changed, so switch the sign here as well.
            # print 'move'
            self.move('x', -self.x_mag)
            #print('change direction', -self.x_mag)
        if self.change_level:
            # print 'actually change level now'
            self.set_level_variables(self.change_level)
            print('angle', self.base.camera.getH())
            self.change_level = False
        # check to see if banana is on random
        if self.random_banana:
            # print 'random'
            # make side not entirely random. Don't want too many in a row on one side
            # for MP, because he is a bit of an idiot.
            # First check if we care about the next direction
            if self.side_bias and abs(self.last_multiplier) > 1:
                # if there have been two in a row in the same direction, pick the opposite
                # direction, otherwise choose randomly
                # print 'change, self.last_multiplier is zero'
                self.multiplier = - self.multiplier
            else:
                # print 'random'
                self.multiplier = random.choice([1, -1])
            # print('next up', self.multiplier)
            # multiplier should never be zero when doing this comparison
            # last_multiplier is the only one that can be zero, and only
            # very briefly
            # if this gives you a negative 1, than we are switching sides,
            # if we don't care about side_bias, we don't look at last_multiplier,
            # and this doesn't matter
            if self.last_multiplier/self.multiplier != 1:
                # print 'reset'
                self.last_multiplier = 0
            self.last_multiplier += self.multiplier
            # print('last currently', self.last_multiplier)
            self.avatar_h = random.choice(self.random_choices)
            # for some versions, subject could still be holding joystick at this point.
            # this means we x_mag is at a position that might no longer be
            # allowed, so we are going to send the current joystick position
            # through the move method to correct that. move switches the sign, so switch
            # the sign here as well.
            # print 'move'
            self.move('x', -self.x_mag)
        self.set_camera()
        if not unittest:
            self.data_file.write(str(self.frameTask.time) + ', ' +
                                 'banana position, ' +
                                 str(self.multiplier * self.avatar_h) + '\n')
        # print('min time to reward:', sqrt(2 * self.avatar_h / 0.05 * 0.01))
        # for training 4, switch from going forward to left/right
        if self.free_move == 4:
            self.go_forward = False
        # un-hide banana
        self.banana.unstash()
        # print 'avatar can move again, new trial starting'
        self.moving = True
        # print('yay', self.yay_reward)

    def set_camera(self):
        self.base.camera.setH(self.multiplier * abs(self.avatar_h))
        self.base.camera.setPos(self.avatar_pos)
        #print self.base.camera.getPos()
        #print self.banana.getPos()
        # print self.base.camera.getH()
        sys.stdout.write('current angle: ' + str(self.base.camera.getH()) + '\n')


    def x_change_color(self, color):
        # print self.crosshair.getColor()
        self.crosshair.setTextColor(color)
        # self.cross.setColor(Point4(1, 0, 0, 1))

    def move(self, js_dir, js_input):
        # most restrictions on movement handled in frame_loop,
        # both due to levels and due to environment
        if not unittest:
            self.data_file.write(str(self.frameTask.time) + ', ' +
                                 str(js_dir) + ', ' +
                                 str(-js_input) + '\n')
            # print(js_dir, js_input)
        # Threshold. If too low, noise will create movement.
        if abs(js_input) < 0.1:
            js_input = 0
        # we are moving the camera in the opposite direction of the joystick,
        # x and y inputs will both be inverted
        if js_dir == 'x' or js_dir == 'x_key':
            # print js_input
            # x direction is reversed
            self.x_mag = -js_input
            # print('x_mag', self.x_mag)
            # hack for Mr. Peepers...
            # barely touch joystick and goes super speedy. speed not dependent
            # on how hard he touches joystick (always 2)
            # if self.subject == 'MP' and js_input != 0:
            #    # print 'yes'
            #    # need it to be the same direction as negative of js_input
            #    self.x_mag = js_input/abs(js_input) * -2
            # new hack for Mr. Peepers...
            # joystick pressure has more of an effect than acceleration
            # (0 to 2 instead of 0 to 1, trying to get him to push harder on
            # on the joystick)
            if self.subject == 'MP' and js_input != 0:
                self.x_mag = js_input * -2
            # print('x', self.x_mag)
        else:
            # y direction is also reversed,
            # not allowed to go backward, ever
            if js_input < 0:
                self.y_mag = -js_input
            else:
                self.y_mag = 0

    def restrict_forward(self):
        """
        :return:
        As self.forward_limit increases, we require the subject to 'go straighter',
        iow, the subject should not be pushing the joystick to the side, only forward
        When forward_limit hits one, can only go forward (any side movement means don't
        go anywhere)
        """
        self.go_forward = True
        if self.x_mag > self.forward_limit:
            self.go_forward = False

    def get_new_heading(self, heading, dt):
        # print 'get new heading'
        # set new turning speed.
        # if new trial or subject stopped moving, reverts to initial speed
        if self.start_trial or self.x_mag == 0:
            self.speed = self.initial_speed
            self.slow_speed = self.wrong_speed
            self.start_trial = False
        else:
            # the larger the push on the joystick,
            # the more the speed increases.
            self.slow_speed += self.wrong_speed * abs(self.x_mag)
            # self.speed += 0.05 * abs(self.x_mag)
            self.speed += self.initial_speed * abs(self.x_mag)
        # determine if moving towards the banana
        to_banana = False
        # first if is to make sure we don't divide by zero,
        if self.x_mag != 0 and heading != 0:
            if self.x_mag/abs(self.x_mag) * heading/abs(heading) < 0:
                to_banana = True
        # unless there is a reason to stop movement, this is the heading
        delta_heading = self.x_mag * self.speed * dt
        # if not allowed to go past banana, stop directly at center
        # if self.free_move == 1:
        # if heading + delta_heading switches it from + to -
        # if heading away from banana, many opportunities to slow or
        # stop movement...
        if not to_banana:
            if abs(heading) >= self.screen_edge:
                # block off edge of screen
                # print 'hit a wall'
                delta_heading = 0
            elif self.check_zone is None:
                # if check_zone is None, than went past banana target zone,
                # and we want to go slow
                # print 'went past zone'
                delta_heading = self.x_mag * self.slow_speed * dt
                # delta_heading = self.x_mag * self.initial_speed * dt
            elif self.free_move == 1:
                # print 'free move is 1'
                # self.free_move is one, only allowed to go towards banana
                delta_heading = 0
            elif self.free_move == 2:
                # print 'free move is 2'
                # self.free_move is two, both directions allowed, but go
                # in direction away from banana more slowly.
                # print 'slow'
                # self.x_mag /= self.wrong_speed
                delta_heading = self.x_mag * self.slow_speed * dt
                # print self.slow_speed
                # delta_heading = self.x_mag * self.speed * dt
        # print('delta heading', delta_heading)
        return delta_heading

    def inc_angle(self):
        # print('old pos', self.avatar_h)
        # self.avatar_h[0] = self.avatar_h[0] * 1.5
        # self.avatar_h *= 1.5
        self.avatar_h *= 1.1
        # print('would be', self.avatar_h)
        if abs(self.avatar_h) > self.max_angle:
            self.avatar_h = self.multiplier * self.max_angle
        # y is always going to be positive
        # self.avatar_h[1] = sqrt(25 - self.avatar_h[0] ** 2)
        sys.stdout.write('increase angle, new angle: ' + str(self.avatar_h) + '\n')
        if not unittest:
            self.data_file.write(str(self.frameTask.time) + ', ' +
                                 'keypress, increase angle ' +
                                 str(self.multiplier * self.avatar_h) + '\n')
        # print('min time to reward:', sqrt(2 * self.avatar_h / 0.05 * 0.01))

    def dec_angle(self):
        # print('old pos', self.avatar_h)
        # self.avatar_h /= 1.5
        self.avatar_h /= 1.1
        if abs(self.avatar_h) < self.min_angle:
            self.avatar_h = self.multiplier * self.min_angle
        # self.banana_pos[0] = x_sign * (abs(self.banana_pos[0]) - 1)
        # self.banana_pos[1] = sqrt(25 - self.banana_pos[0] ** 2)
        sys.stdout.write('decrease angle, new angle: ' + str(self.avatar_h) + '\n')
        if not unittest:
            self.data_file.write(str(self.frameTask.time) + ', ' +
                                 'keypress, decrease angle ' +
                                 str(self.multiplier * self.avatar_h) + '\n')
        # print('min time to reward:', sqrt(2 * self.avatar_h / 0.05 * 0.01))

    def inc_reward(self):
        self.num_beeps += 1
        sys.stdout.write('increase reward, new reward: ' + str(self.num_beeps) + '\n')
        if not unittest:
            self.data_file.write(str(self.frameTask.time) + ', ' +
                                 'keypress, increase reward ' +
                                 str(self.num_beeps) + '\n')

    def dec_reward(self):
        self.num_beeps -= 1
        sys.stdout.write('decrease reward, new reward: ' + str(self.num_beeps) + '\n')
        if not unittest:
            self.data_file.write(str(self.frameTask.time) + ', ' +
                                 'keypress, decrease reward ' +
                                 str(self.num_beeps) + '\n')

    def inc_level(self):
        # increase the level, if we are jumping multiple levels,
        # at once, self.training will not have increased yet, so
        # check to see what self.change_level is first (don't want
        # to change levels in the middle of a trial)
        training = self.training
        if self.change_level:
            training = self.change_level
        # print('old level', training)
        # get current position in sequence:
        seq_num = self.get_seq_num(training)
        if training == self.levels_available[-1][-1]:
            sys.stdout.write('already at most difficult level \n')
            self.change_level = training
        elif training == self.levels_available[seq_num][-1]:
            sys.stdout.write('switching to new sequence \n')
            self.change_level = self.levels_available[seq_num + 1][0]
        else:
            self.change_level = round(training + 0.1, 2)
        sys.stdout.write('increase level, new level: ' + str(self.change_level) + '\n')
        # print('new level', self.change_level)
        if not unittest:
            self.data_file.write(str(self.frameTask.time) + ', ' +
                                 'keypress, increase level ' +
                                 str(self.change_level) + '\n')

    def dec_level(self):
        # decrease the level, if we are jumping multiple levels,
        # at once, self.training will not have increased yet, so
        # check to see what self.change_level is first (don't want
        # to change levels in the middle of a trial)
        training = self.training
        if self.change_level:
            training = self.change_level
        # print('old level', training)
        # get current position in sequence:
        seq_num = self.get_seq_num(training)
        if training == self.levels_available[0][0]:
            sys.stdout.write('already at easiest level \n')
            self.change_level = training
        elif training == self.levels_available[seq_num][0]:
            sys.stdout.write('switching to new sequence \n')
            self.change_level = self.levels_available[seq_num - 1][-1]
        else:
            self.change_level = round(training - 0.1, 2)
        sys.stdout.write('increase level, new level: ' + str(self.change_level) + '\n')
        if not unittest:
            self.data_file.write(str(self.frameTask.time) + ', ' +
                                 'keypress, decrease level ' +
                                 str(self.change_level) + '\n')

    def get_seq_num(self, training):
        seq_num = 0
        for seq_num, sequence in enumerate(self.levels_available):
            if sequence.count(training) > 0:
                if sequence.index(training) is not None:
                    break
        return seq_num

    def inc_wrong_speed(self):
        if self.wrong_speed >= self.initial_speed:
            self.wrong_speed = self.initial_speed
            sys.stdout.write('now same speed as towards the banana \n')
        else:
            self.wrong_speed += 0.01
        sys.stdout.write('increase speed in wrong direction, new: ' + str(self.wrong_speed) + '\n')
        if not unittest:
            self.data_file.write(str(self.frameTask.time) + ', ' +
                                 'keypress, increase wrong speed ' +
                                 str(self.wrong_speed) + '\n')

    def dec_wrong_speed(self):
        self.wrong_speed -= 0.01
        sys.stdout.write('decrease speed in wrong direction, new: ' + str(self.wrong_speed) + '\n')
        if not unittest:
            self.data_file.write(str(self.frameTask.time) + ', ' +
                                 'keypress, decrease wrong speed ' +
                                 str(self.wrong_speed) + '\n')

    def inc_random(self):
        if self.current_choice == len(self.all_random_selections) - 1:
            sys.stdout.write('already at max \n')
        else:
            # current is the current length, which conveniently
            # enough is the next number to use, because of zero indexing
            self.current_choice += 1
            self.random_choices = self.all_random_selections[self.current_choice]
        sys.stdout.write('increase selection of random bananas, new: ' + str(self.random_choices) + '\n')
        if not unittest:
            self.data_file.write(str(self.frameTask.time) + ', ' +
                                 'keypress, increase random selection ' +
                                 str(self.random_choices) + '\n')

    def dec_random(self):
        if self.current_choice == 0:
            sys.stdout.write('already at min \n')
        else:
            # current is the current length, so we need to subtract
            # by two, because of zero indexing
            self.current_choice -= 1
            self.random_choices = self.all_random_selections[self.current_choice]
        sys.stdout.write('decrease selection of random bananas, new: ' + str(self.random_choices) + '\n')
        if not unittest:
            self.data_file.write(str(self.frameTask.time) + ', ' +
                                 'keypress, decrease random selection ' +
                                 str(self.random_choices) + '\n')

    def inc_forward_speed(self):
        self.initial_forward_speed += 0.01
        sys.stdout.write('increase forward speed, new: ' + str(self.initial_forward_speed) + '\n')
        if not unittest:
            self.data_file.write(str(self.frameTask.time) + ', ' +
                                 'keypress, increase forward speed ' +
                                 str(self.initial_forward_speed) + '\n')

    def dec_forward_speed(self):
        self.initial_forward_speed -= 0.01
        sys.stdout.write('decrease forward speed, new: ' + str(self.initial_forward_speed) + '\n')
        if not unittest:
            self.data_file.write(str(self.frameTask.time) + ', ' +
                                 'keypress, decrease forward speed ' +
                                 str(self.initial_forward_speed) + '\n')

    def change_left(self):
        self.new_dir = -1
        sys.stdout.write('new dir: left \n')
        print('new direction', self.new_dir)
        if not unittest:
            self.data_file.write(str(self.frameTask.time) + ', ' +
                                 'keypress, new dir left' + '\n')

    def change_right(self):
        self.new_dir = 1
        sys.stdout.write('new dir: right \n')
        print('new direction', self.new_dir)
        if not unittest:
            self.data_file.write(str(self.frameTask.time) + ', ' +
                                 'keypress, new dir right' + '\n')

    def extra_reward(self):
        sys.stdout.write('beep \n')
        if self.reward:
            self.reward.pumpOut()

    def reset_variables(self):
        # this is only called once, from init
        self.base.taskMgr.remove("frame_loop")
        # set/reset to the original state of variables
        # self.max_angle = 26
        self.max_angle = 40
        self.min_angle = 1.5
        self.delay_start = False
        self.yay_reward = False
        self.reward_delay = False
        self.reward_on = True
        self.reward_count = 0
        self.x_mag = 0
        self.y_mag = 0
        self.speed = self.initial_speed  # factor to change speed of joystick and control acceleration
        self.forward_speed = self.initial_forward_speed
        # speed for going in the wrong direction, when same speed as initial speed, then no change
        self.wrong_speed = 0.005
        self.slow_speed = self.wrong_speed
        # toggle for whether moving is allowed or not
        self.moving = True
        # toggle for making sure stays on banana for min time for 2.3
        self.set_zone_time = False
        # amount need to hold crosshair on banana to get reward (2.3)
        # must be more than zero. At 1.5 distance, must be greater than
        # 0.5 to require stopping
        self.hold_aim = 0.6
        if unittest:
            self.hold_aim = 0.1
        # keeps track of how long we have held
        self.hold_time = 0
        # check_zone is a toggle that happens when lined up crosshair with banana
        # if check_zone is False, not currently in the zone, if true checking to
        # see if we have left the zone. if none, left the zone and in mode where
        # slows down after leaving the zone.
        self.check_zone = False
        # self.check_time = 0
        # speed for going in the wrong direction, 1 is no change, higher numbers slower
        self.wrong_speed = 0.005
        self.slow_speed = self.wrong_speed
        # toggle for when trial begins
        self.start_trial = True

    def set_level_variables(self, training):
        print 'really setting level variables'
        # default is lowest training level
        self.training = training
        self.free_move = 1
        self.must_release = False
        self.random_banana = False
        self.require_aim = False
        self.go_forward = False
        self.banana_coll_node.setIntoCollideMask(self.mask_list[0])
        self.avatar_h = self.config_avatar_h
        self.avatar_pos = Point3(0, -1.5, 1)
        self.banana_node_path.setScale(0.1)
        if training > self.levels_available[0][0]:
            # print '2.1'
            self.must_release = True
        if training > self.levels_available[0][1]:
            # print '2.2'
            self.random_banana = True
        if training > self.levels_available[0][2]:
            # print '2.3'
            self.free_move = 2
        if training > self.levels_available[0][3]:
            # print '2.4'
            self.free_move = 3
        if training > self.levels_available[0][4]:
            # print '2.5'
            self.require_aim = 'slow'
        if training > self.levels_available[0][5]:
            # print '2.6'
            self.require_aim = True
        # print self.levels_available[0][-1]
        # level 3 training
        if training > self.levels_available[0][-1]:
            # print '3.0'
            self.avatar_pos = Point3(0.01, self.config_avatar_d, 1)
            self.banana_coll_node.setIntoCollideMask(self.mask_list[1])
            # defaults for level 3 training
            self.go_forward = True
            self.free_move = 0
            self.must_release = False
            self.random_banana = False
            self.require_aim = True
        if training > self.levels_available[1][0]:
            # print '3.1'
            self.must_release = True
        # level 4 training
        if training > self.levels_available[1][-1]:
            #self.banana_node_path.setScale(0.2)
            # print '4.0'
            self.banana_coll_node.setIntoCollideMask(self.mask_list[2])
            self.go_forward = False
            self.free_move = 4
            self.must_release = False
            self.random_banana = False
            self.require_aim = False
        if training > self.levels_available[2][0]:
            # print '4.1'
            self.random_banana = True
        if training > self.levels_available[2][1]:
            # print '4.2'
            self.require_aim = 'slow'
        if training > self.levels_available[2][2]:
            # print '4.3'
            self.require_aim = True
        #print('what sequence?', self.get_seq_num(training))
        # In case random_bananas changed:
        if self.random_banana:
            self.random_choices = self.all_random_selections[self.current_choice]
            self.avatar_h = random.choice(self.random_choices)
            sys.stdout.write('current angles available ' + str(self.random_choices) + '\n')
        elif self.get_seq_num(training) == 1:
            # really should have started out with training zero,
            # then numbering would be better...
            #print 'sequence 3?'
            self.avatar_h = 0
        else:
            self.avatar_h = self.config_avatar_h
        # print self.banana.getH()
        print self.avatar_pos
        # print self.avatar_h
        sys.stdout.write('forward: ' + str(self.go_forward) + '\n')
        sys.stdout.write('free move: ' + str(self.free_move) + '\n')
        sys.stdout.write('random: ' + str(self.random_banana) + '\n')
        sys.stdout.write('require aim: ' + str(self.require_aim) + '\n')

    def load_fruit(self, fruit):
        if fruit == 'banana':
            self.banana = self.base.loader.loadModel("models/bananas/banana.bam")
            self.banana.setH(280)
            # self.banana.setH(0)
            self.banana.setScale(0.5)
            # banana always in the same position, just move avatar.
            self.banana.setPos(Point3(0, 0, 1))
            self.banana_node_path = self.banana.find('**/+CollisionNode')
            self.banana.reparentTo(self.base.render)
        elif fruit == 'cherry':
            # or cherry as banana?
            self.banana = self.base.render.attachNewNode('root')
            # banana center is off, re-center with new node
            new_node_path = self.base.loader.loadModel("models/fruit/cherries_no_cn.egg")
            new_node_path.reparentTo(self.banana)
            new_node_path.setPos(0, 0, 0)
            #new_node_path.setScale(0.08)
            self.banana.setScale(0.08)  # cherry
            # move the center of the cherries
            self.banana.setPos(Point3(0.08, 0, 1))
            # can't get built in cherry collision node to work properly...
            cs = CollisionSphere(-10, 0, 0, 11)
            self.banana_node_path = new_node_path.attachNewNode(CollisionNode('c_node'))
            self.banana_node_path.node().addSolid(cs)

        # usually 0.1 for banana
        # self.banana_node_path = self.banana.find('**/+CollisionNode')
        # self.banana_node_path.setScale(1)
        self.banana_mask = BitMask32(0x1)
        # banana intoCollideMask will change depending on which level we
        # are training on.
        self.banana_coll_node = self.banana_node_path.node()
        self.banana_coll_node.setIntoCollideMask(self.mask_list[0])

    def open_data_file(self, config):
        # open file for recording eye data
        data_dir = 'data/' + config['subject']
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        self.data_file_name = data_dir + '/' + config['subject'] + '_TR_' + \
                              datetime.datetime.now().strftime("%y_%m_%d_%H_%M")
        sys.stdout.write('data file: ' + str(self.data_file_name) + '\n')
        # open file for recording eye positions
        self.data_file = open(self.data_file_name, 'w')
        self.data_file.write('timestamp, joystick input, for subject: ' + config['subject'] + '\n')

    # Closing methods
    def close_files(self):
        self.data_file.close()

    def close(self):
        if not unittest:
            self.close_files()
        sys.exit()

    def setup_inputs(self):
        self.accept('x_axis', self.move, ['x'])
        self.accept('y_axis', self.move, ['y'])
        self.accept('arrow_right', self.move, ['x_key', 0.5])
        self.accept('arrow_left', self.move, ['x_key', -0.5])
        self.accept('arrow_right-up', self.move, ['x_key', 0])
        self.accept('arrow_left-up', self.move, ['x_key', 0])
        self.accept('arrow_right-repeat', self.move, ['x_key', 0.5])
        self.accept('arrow_left-repeat', self.move, ['x_key', -0.5])
        self.accept('arrow_up', self.move, ['y_key', -0.5])
        self.accept('arrow_up-up', self.move, ['y_key', 0])
        self.accept('arrow_up-repeat', self.move, ['y_key', -0.5])
        self.accept('q', self.close)
        self.accept('w', self.inc_reward)
        self.accept('s', self.dec_reward)
        self.accept('e', self.inc_angle)
        self.accept('d', self.dec_angle)
        self.accept('t', self.inc_level)
        self.accept('g', self.dec_level)
        self.accept('y', self.inc_wrong_speed)
        self.accept('h', self.dec_wrong_speed)
        self.accept('u', self.inc_random)
        self.accept('j', self.dec_random)
        self.accept('i', self.inc_forward_speed)
        self.accept('k', self.dec_forward_speed)
        self.accept('r', self.change_right)
        self.accept('l', self.change_left)
        self.accept('space', self.extra_reward)

    @staticmethod
    def make_coll_node_path(node_path, solid):
        # Creates a collision node and attaches the collision solid to the
        # supplied NodePath. Returns the nodepath of the collision node.

        # Creates a collision node named after the name of the NodePath.
        coll_node = CollisionNode("%s c_node" % node_path.getName())
        coll_node.addSolid(solid)
        collision_node_path = node_path.attachNewNode(coll_node)
        # Show the collision node, which makes the solids show up.
        # actually, it appears to do nothing...
        # collision_node_path.show()
        return collision_node_path

unittest = False
if __name__ == '__main__':
    # print 'main?'
    TB = TrainingBananas()
    TB.base.run()
else:
    # print 'test'
    unittest = True
