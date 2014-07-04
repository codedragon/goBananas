from __future__ import division
from direct.showbase.ShowBase import ShowBase
from joystick import JoystickHandler
from panda3d.core import Point3, Point4
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
    #print 'loaded PyDaq'
except ImportError:
    pydaq = None
    PYDAQ_LOADED = False
    print 'Not using PyDaq'


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
        print('Subject is', config['subject'])
        self.subject = config['subject']
        # set up reward system
        # if unit-testing, pretend like we couldn't
        # load the module
        if unittest:
            pydaq_loaded = False
        if config['reward'] and pydaq_loaded:
            self.reward = pydaq.GiveReward()
            print 'Reward system on'
        else:
            self.reward = None
        if not unittest:
            # if doing unittests, there is no window
            wp = WindowProperties()
            wp.setSize(1280, 800)
            #wp.setSize(1024, 768)
            wp.setOrigin(0, 0)
            wp.setCursorHidden(True)
            self.base.win.requestProperties(wp)
            #base.setFrameRateMeter(True)
            # initialize training file name
            self.data_file_name = ''
            self.data_file = None
            self.open_data_file(config)
        # for bananas, changing the angle from avatar to banana, so left is negative
        # right is positive.
        self.train_dir = 'x'
        if config['trainingDirection'] == 'Right':
            self.multiplier = 1
        elif config['trainingDirection'] == 'Left':
            self.multiplier = -1
        elif config['trainingDirection'] == 'Forward':
            self.train_dir = 'y'
        #print config['trainingDirection']
        #print('multiplier', self.multiplier)
        self.last = self.multiplier
        self.side_bias = config['random_bias']
        # bring some configuration parameters into memory, so we don't need to
        # reload the config file multiple times, also allows us to change these
        # variables dynamically
        self.num_beeps = config['numBeeps']
        # not changing now, but may eventually...
        self.x_alpha = config['xHairAlpha']
        self.reward_time = config['pulseInterval']  # usually 200ms
        # random selection used for training 2.3 and above
        self.random_choices = config['random_choices']
        # amount need to hold crosshair on banana to get reward (2.3)
        # must be more than zero. At 1.5 distance, must be greater than
        # 0.5 to require stopping
        self.hold_aim = config['hold_aim']
        self.initial_speed = config['initial_speed']
        self.training = config['training']
        if not unittest:
            print('training level is', self.training)

        # initialize training variables
        # will be set to proper levels in set_level_variables method
        self.free_move = False
        self.must_release = False
        self.random_banana = False
        self.require_aim = False
        self.go_forward = False
        self.set_level_variables(self.training)

        # variable used to notify when changing direction of new target
        self.new_dir = None
        # variable to notify when changing levels
        self.change_level = False

        # set up banana
        self.banana = self.base.loader.loadModel("models/bananas/banana.bam")
        self.banana.setPos(Point3(0, 2.5, 0))
        #self.banana.setPos(Point3(0, 0, 0))
        self.banana.setH(280)
        self.banana.setScale(0.5)
        self.banana.reparentTo(self.base.render)
        collision_node = self.banana.find('**/+CollisionNode')
        collision_node.setScale(0.2)
        #collision_node.show()
        #cs = CollisionSphere(0, 0, 0, 1)

        # set up collision system and collision ray to camera
        self.base.cTrav = CollisionTraverser()
        self.collHandler = CollisionHandlerQueue()
        ray_node = self.base.camera.attachNewNode(CollisionNode('CrossHairRay'))
        # ray that comes straight out from the camera
        ray_solid = CollisionRay(0, 0, 0, 0, 1, 0)
        ray_node_path = self.make_coll_node_path(ray_node, ray_solid)
        cam_ray_node = ray_node_path.node()
        cam_ray_node.setIntoCollideMask(0)

        # add collision sphere to camera
        sphere_node = self.base.camera.attachNewNode(CollisionNode('CollisionSphere'))
        camera_sphere = CollisionSphere(0, 0, 0, 0.5)
        sphere_node_path = self.make_coll_node_path(sphere_node, camera_sphere)
        cam_sphere_node = sphere_node_path.node()
        cam_sphere_node.setIntoCollideMask(0)

        #print 'ray'
        #print cam_ray_node.getFromCollideMask()
        #print cam_ray_node.getIntoCollideMask()
        self.base.cTrav.addCollider(ray_node_path, self.collHandler)
        self.base.cTrav.addCollider(sphere_node_path, self.collHandler)
        #self.base.cTrav.showCollisions(self.base.render)
        #ray_node_path.show()
        #sphere_node_path.show()

        # set avatar position/heading
        self.avatar_pos = Point3(0, 0, 1)
        if self.training >= 3:
            self.avatar_h = 0
            #self.fullForwardSpeed = config['fullForwardSpeed']
        elif self.training >= 2:
            self.avatar_h = config['avatar_start_h']
            #avatar.setH(self.multiplier * self.avatar_h)
            #self.fullTurningSpeed = config['fullTurningSpeed']
        self.base.camera.setH(self.multiplier * self.avatar_h)

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
        #crosshair_pos = Point3(0, 0, 0)
        crosshair_pos = Point3(-0.07, 0, -0.05)
        #print text_node_path.getPos()
        text_node_path.setPos(crosshair_pos)
        # setup keyboard/joystick inputs
        self.setup_inputs()
        # Initialize more variables
        # These variables are set to their initial states in reset_variables, so
        # does not matter what they are set to here.
        self.delay_start = False
        self.yay_reward = False
        self.reward_delay = False
        self.reward_on = True
        self.reward_count = 0
        self.x_mag = 0
        self.y_mag = 0
        self.speed = self.initial_speed  # factor to slow down movement of joystick and control acceleration
        # toggle for whether moving is allowed or not
        self.moving = True
        # toggle for making sure stays on banana for min time for 2.3
        self.set_zone_time = False
        # speed for going in the wrong direction, 1 is no change, higher numbers slower
        self.wrong_speed = 4
        # keeps track of how long we have held
        self.hold_time = 0
        self.check_zone = False
        self.check_time = 0
        # toggle for when trial begins
        self.start_trial = True
        # set up main loop
        self.frameTask = self.base.taskMgr.add(self.frame_loop, "frame_loop")
        self.frameTask.delay = -0.1  # want initial delay less than zero
        self.frameTask.last = 0  # task time of the last frame
        # set variables to their actual starting values
        self.reset_variables()

    def frame_loop(self, task):
        #print 'loop'
        dt = task.time - task.last
        task.last = task.time
        #print('dt', dt)
        # delay_start means we just gave reward and need to set wait
        # until reward pump is done to do anything
        if self.delay_start:
            task.delay = task.time + self.reward_time
            #print('time now', task.time)
            #print('delay until', task.delay)
            self.delay_start = False
            #self.reward_delay = True
            return task.cont
        # set_zone_time means we have the crosshair over the banana,
        # and have to set how long to leave it there
        if self.set_zone_time:
            #print 'reset zone time'
            self.hold_time = task.time + self.hold_aim
            self.set_zone_time = False
            self.check_zone = True
        # reward delay is over, on to regularly scheduled program
        if task.time > task.delay:
            #print 'past delay'
            # check for reward
            #print('beeps so far', self.reward_count)
            if self.yay_reward and self.reward_count < self.num_beeps:
                #print 'reward'
                self.reward_count += 1
                self.give_reward()
                return task.cont
            elif self.yay_reward and self.reward_count == self.num_beeps:
                #print 'going to restart'
                # done giving reward, time to start over, maybe
                # hide the banana
                self.banana.stash()
                # change the color of the crosshair
                self.x_change_color(self.x_start_c)
                # before we can proceed, subject may need to let go of the joystick
                if self.must_release:
                    #print 'checking x_mag'
                    #print self.x_mag
                    if abs(self.x_mag) > 0:
                        #print('let go!')
                        return task.cont
                # and now we can start things over again
                #print('start over')
                self.restart_bananas()
                # used to see how long it takes subject to get banana from
                # time plotted
                self.check_time = task.time
                return task.cont
            # check to see if we are moving
            if self.moving:
                #print 'moving'
                # want to create some acceleration, so
                # every frame we will increase the self.speed by a very small fraction of the previous self.x_mag
                # if self.x_mag was zero, than we reset slow_factor
                #print self.base.camera.getH()
                #print(self.x_mag * self.speed * -self.multiplier)
                #print self.speed
                heading = self.base.camera.getH()
                #print heading
                # set new speed, if new trial or subject stopped, reverts to default
                if self.start_trial or self.x_mag == 0:
                    self.speed = self.initial_speed
                    self.start_trial = False
                else:
                    #self.speed = 1
                    # self.x_mag (how much you push the joystick) affects
                    # acceleration as well as speed
                    self.speed += 0.05 * abs(self.x_mag)
                #print('new speed', self.speed)
                # edges of screen are like a wall
                # if heading is 22 or over, and moving away from center, nothing happens
                if abs(heading) >= 22 and self.x_mag * self.multiplier > 0:
                    #print 'hit a wall'
                    delta_heading = 0
                elif self.check_zone is None:
                    #print 'went past zone'
                    # if gone past banana target zone, no acceleration
                    delta_heading = self.x_mag * self.initial_speed * dt
                else:
                    # use dt so when frame rate changes the rate of movement changes proportionately
                    delta_heading = self.x_mag * self.speed * dt
                    #print self.speed
                    #print('dt', dt)
                    #print('x', self.x_mag)
                #print('change heading', delta_heading)
                self.base.camera.setH(heading + delta_heading)
                #print('camera heading', self.base.camera.getH())
                # check for collision:
                if self.go_forward:
                    self.check_y_banana()
                else:
                    # if we need to be stopping and leaving (holding) crosshair over banana,
                    # make sure still in target zone.
                    if self.check_zone:
                        #print('check hold')
                        collide_banana = self.check_x_banana()
                        if collide_banana:
                            #print('in the zone')
                            if task.time > self.hold_time:
                                #print('ok, get reward')
                                # stop moving and get reward
                                self.x_change_color(self.x_stop_c)
                                self.moving = False
                                self.yay_reward = True
                                self.check_zone = False
                            else:
                                pass
                                #print('keep holding')
                                #print('time', task.time)
                                #print('hold until', self.hold_time)
                        else:
                            print('left zone, wait for another collision')
                            self.x_change_color(self.x_start_c)
                            self.check_zone = None
                    else:
                        #print('camera heading before collision', self.base.camera.getH())
                        collide_banana = self.check_x_banana()
                        if collide_banana:
                            #print('time took: ', task.time - self.check_time)
                            #print 'collision'
                            #print 'change xhair color to red'
                            self.x_change_color(self.x_stop_c)
                            if self.require_aim:
                                self.set_zone_time = True
                            else:
                                #print 'yes'
                                # stop moving
                                self.moving = False
                                # move to center
                                if self.base.camera.getH != 0:
                                    #print 'moved camera'
                                    self.base.camera.setH(0)
                                self.yay_reward = True
        return task.cont

    def give_reward(self):
        print('beep')
        if self.reward:
            self.reward.pumpOut()
        self.delay_start = True

    def check_x_banana(self):
        #print 'check banana'
        collide_banana = False
        # check to see if crosshair is over banana
        if self.collHandler.getNumEntries() > 0:
            # the only object we can be running into is the banana, so there you go...
            collide_banana = True
            #print self.collHandler.getEntries()
            #print self.base.camera.getH()
        return collide_banana

    def check_y_banana(self):
        # for the forward motion, we need to know when the banana is close,
        # use collision sphere around avatar, instead of ray.
        #print 'check banana'
        collide_banana = False
        # check to see if crosshair is over banana
        if self.collHandler.getNumEntries() > 0:
            # the only object we can be running into is the banana, so there you go...
            collide_banana = True
            #print self.collHandler.getEntries()
            #print self.base.camera.getH()
        return collide_banana

    def restart_bananas(self):
        #print 'restarted'
        # reset a couple of variables
        self.yay_reward = False
        self.reward_count = 0
        self.check_time = 0
        self.start_trial = True
        #print self.multiplier
        # check to see if we are switching the banana to the other side
        if self.new_dir is not None:
            self.multiplier = self.new_dir
            self.new_dir = None
            # for some versions, subject could still be holding joystick at this point.
            # this means we x_mag is at a position that might no longer be
            # allowed, so we are going to send the current joystick position
            # through the move method to correct that. move switches the sign, so switch
            # the sign here as well.
            #print 'move'
            self.move('x', -self.x_mag)
            #print('change direction')
        if self.change_level:
            print 'change level'
            self.set_level_variables(self.change_level)
            self.change_level = False
        # check to see if banana is on random
        if self.random_banana:
            # make side not entirely random. Don't want too many in a row on one side
            # for MP, because he is a bit of an idiot.
            # First check if we care about the next direction
            if self.side_bias and abs(self.last) > 1:
                # if there have been two in a row in the same direction, pick the opposite
                # direction, otherwise choose randomly
                print 'change, self.last is zero'
                self.multiplier = - self.multiplier
            else:
                print 'random'
                self.multiplier = random.choice([1, -1])
            #print('next up', self.multiplier)
            # multiplier should never be zero
            # if this gives you a negative 1, than we are switching sides,
            # and should reset to zero
            # if we don't care about side_bias, then this doesn't matter
            if self.last/self.multiplier != 1:
                print 'reset'
                self.last = 0
            self.last += self.multiplier
            print('last currently', self.last)
            self.avatar_h = random.choice(self.random_choices)
            # for some versions, subject could still be holding joystick at this point.
            # this means we x_mag is at a position that might no longer be
            # allowed, so we are going to send the current joystick position
            # through the move method to correct that. move switches the sign, so switch
            # the sign here as well.
            #print 'move'
            self.move('x', -self.x_mag)
        #print('rotate avatar back so at correct angle:', self.avatar_h)
        self.base.camera.setH(self.multiplier * self.avatar_h)
        print('avatar heading', self.base.camera.getH())
        if not unittest:
            self.data_file.write(str(self.frameTask.time) + ', ' +
                                 'banana position, ' +
                                 str(self.multiplier * self.avatar_h) + '\n')

        #print('min time to reward:', sqrt(2 * self.avatar_h / 0.05 * 0.01))
        # un-hide banana
        self.banana.unstash()
        #print 'avatar can move again'
        self.moving = True
        #print('yay', self.yay_reward)

    def x_change_color(self, color):
        #print self.crosshair.getColor()
        self.crosshair.setTextColor(color)
        #self.cross.setColor(Point4(1, 0, 0, 1))

    def move(self, js_dir, js_input):
        if not unittest:
            self.data_file.write(str(self.frameTask.time) + ', ' +
                                 str(js_dir) + ', ' +
                                 str(-js_input) + '\n')
            #print(js_dir, js_input)
        if abs(js_input) < 0.1:
            js_input = 0
        if js_dir == 'x' or js_dir == 'x_key':
            #print js_input
            # we are moving the camera in the opposite direction of the joystick
            self.x_mag = -js_input
            # hack for Mr. Peepers...
            # barely touch joystick and goes super speedy. speed not dependent
            # on how hard he touches joystick.
            #if self.subject == 'MP' and js_input != 0:
            #    #print 'yes'
            #    # need it to be the same direction as negative of js_input
            #    self.x_mag = js_input/abs(js_input) * -2
            # new hack for Mr. Peepers...
            # joystick pressure has more of an effect than acceleration
            if self.subject == 'MP' and js_input != 0:
                self.x_mag = js_input * -2
            #print('x', self.x_mag)
            # slow down or stop movement in direction away from banana
            # if joystick direction and multiplier are same sign,
            # will be positive and therefor direction to be blocked
            if self.x_mag * self.multiplier > 0:
                #print('greater than zero:', self.x_mag * self.multiplier)
                # None is no movement, False is limited movement
                if self.free_move is None:
                    #print 'none'
                    self.x_mag = 0
                elif not self.free_move:
                    #print 'slow'
                    print self.wrong_speed
                    self.x_mag /= self.wrong_speed
            print('new x', self.x_mag)
        else:
            self.y_mag = js_input

    def inc_distance(self):
        if not self.go_forward:
            print 'increase angle'
            #print('old pos', self.avatar_h)
            #self.avatar_h[0] = self.avatar_h[0] * 1.5
            self.avatar_h *= 1.5
            if abs(self.avatar_h) > 18:
                self.avatar_h = 18
            # y is always going to be positive
            #self.avatar_h[1] = sqrt(25 - self.avatar_h[0] ** 2)
            print('new heading', self.avatar_h)
            #print('min time to reward:', sqrt(2 * self.avatar_h / 0.05 * 0.01))

    def dec_distance(self):
        if not self.go_forward:
            print 'decrease angle'
            #print('old pos', self.avatar_h)
            self.avatar_h /= 1.5
            if abs(self.avatar_h) < 0.3:
                self.avatar_h = 0.3
            #self.banana_pos[0] = x_sign * (abs(self.banana_pos[0]) - 1)
            #self.banana_pos[1] = sqrt(25 - self.banana_pos[0] ** 2)
            print('new heading', self.avatar_h)
            #print('min time to reward:', sqrt(2 * self.avatar_h / 0.05 * 0.01))

    def inc_reward(self):
        print 'increase reward'
        self.num_beeps += 1
        print('new reward', self.num_beeps)

    def dec_reward(self):
        print 'decrease reward'
        self.num_beeps -= 1
        print('new reward', self.num_beeps)

    def inc_level(self):
        # in level 2 have 2 thru 2.5
        # currently level 3 is highest
        if self.training == 3:
            self.change_level = self.training
            print 'cannot increase level'
        elif self.training == 2.5:
            self.change_level = 3
        else:
            self.change_level = self.training + 0.1
        print('new level', self.change_level)

    def dec_level(self):
        if self.training == 2:
            self.change_level = self.training
            print 'cannot decrease level'
        elif self.training == 3:
            self.change_level = 2.5
        else:
            self.change_level = self.training - 0.1
        print('new level', self.change_level)

    def inc_wrong_speed(self):
        print 'increase speed in wrong direction'
        # larger numbers are slower, so decrease number
        # to increase speed
        if self.wrong_speed == 1:
            print 'now same speed as towards the banana'
        else:
            self.wrong_speed -= 1
        print('new speed', self.wrong_speed)

    def dec_wrong_speed(self):
        print 'decrease speed in wrong direction'
        # smaller numbers are faster, so increase number
        # to decrease speed
        self.wrong_speed += 1
        print('new speed', self.wrong_speed)

    def change_left(self):
        self.new_dir = -1
        print('new dir: left')

    def change_right(self):
        self.new_dir = 1
        print('new dir: right')

    def change_forward(self):
        self.new_dir = 0
        print('new dir: forward')

    def reset_variables(self):
        self.base.taskMgr.remove("frame_loop")
        # get back to the original state of variables, used for testing
        self.delay_start = False
        self.yay_reward = False
        self.reward_delay = False
        self.reward_on = True
        self.reward_count = 0
        self.x_mag = 0
        self.y_mag = 0
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
        self.check_zone = False
        self.check_time = 0
        # speed for going in the wrong direction, 1 is no change, higher numbers slower
        self.wrong_speed = 4
        # toggle for when trial begins
        self.start_trial = True
        self.frameTask = self.base.taskMgr.add(self.frame_loop, "frame_loop")
        self.frameTask.delay = -0.1  # want initial delay less than zero
        self.frameTask.last = 0  # task time of the last frame

    def set_level_variables(self, training):
        # default is lowest training level
        self.training = training
        self.free_move = None
        self.must_release = False
        self.random_banana = False
        self.require_aim = False
        self.go_forward = False
        if training > 2:
            self.must_release = True
        if training > 2.1:
            self.random_banana = True
        if training > 2.2:
            self.free_move = False
        if training > 2.3:
            self.free_move = True
        if training > 2.4:
            self.require_aim = True
        if training > 2.9:
            self.go_forward = True

    def open_data_file(self, config):
        # open file for recording eye data
        data_dir = 'data/' + config['subject']
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        self.data_file_name = data_dir + '/t_bananas_' + datetime.datetime.now().strftime("%y_%m_%d_%H_%M")
        print('open', self.data_file_name)
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
        self.accept('arrow_right', self.move, ['x_key', 2])
        self.accept('arrow_left', self.move, ['x_key', -2])
        self.accept('arrow_right-up', self.move, ['x_key', 0])
        self.accept('arrow_left-up', self.move, ['x_key', 0])
        self.accept('arrow_right-repeat', self.move, ['x_key', 2])
        self.accept('arrow_left-repeat', self.move, ['x_key', -2])
        self.accept('q', self.close)
        self.accept('w', self.inc_reward)
        self.accept('s', self.dec_reward)
        self.accept('e', self.inc_distance)
        self.accept('d', self.dec_distance)
        self.accept('t', self.inc_level)
        self.accept('g', self.dec_level)
        self.accept('y', self.inc_wrong_speed)
        self.accept('h', self.dec_wrong_speed)
        self.accept('f', self.change_forward)
        self.accept('r', self.change_right)
        self.accept('l', self.change_left)

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
        #collision_node_path.show()
        return collision_node_path

unittest = False
if __name__ == '__main__':
    #print 'main?'
    TB = TrainingBananas()
    TB.base.run()
else:
    #print 'test'
    unittest = True
