from direct.showbase.ShowBase import ShowBase
from joystick import JoystickHandler
from panda3d.core import Point3, Point4
from panda3d.core import TextNode, WindowProperties
from panda3d.core import CollisionNode, CollisionRay, CollisionSphere
from panda3d.core import CollisionTraverser, CollisionHandlerQueue
import datetime
import sys
# only load pydaq if it's available
try:
    sys.path.insert(1, '../pydaq')
    import pydaq
    PYDAQ_LOADED = True
    #print 'loaded PyDaq'
except ImportError:
    PYDAQ_LOADED = False
    print 'Not using PyDaq'


class TrainingBananas(JoystickHandler):
    def __init__(self):
        """
        Initialize the experiment
        """
        self.base = ShowBase()
        config = {}
        execfile('train_config.py', config)
        JoystickHandler.__init__(self)
        self.base.disableMouse()
        print('Subject is', config['subject'])
        # set up reward system
        if config['reward'] and PYDAQ_LOADED:
            self.reward = pydaq.GiveReward()
            print 'pydaq'
        else:
            self.reward = None
        self.frameTask = self.base.taskMgr.add(self.frame_loop, "frame_loop")
        if not unittest:
            wp = WindowProperties()
            wp.setSize(1024, 768)
            wp.setOrigin(0, 0)
            base.win.requestProperties(wp)

        # set up banana
        self.banana = self.base.loader.loadModel("models/bananas/banana.bam")
        self.banana.setPos(Point3(0, 2.5, 0))
        #self.banana.setPos(Point3(0, 0, 0))
        self.banana.setH(280)
        self.banana.setScale(0.5)
        collision_node = self.banana.find('**/+CollisionNode')
        collision_node.setScale(0.2)
        #collision_node.show()
        #cs = CollisionSphere(0, 0, 0, 1)
        #cnodePath = self.banana.attachNewNode(CollisionNode('cnode'))
        #cnodePath.node().addSolid(cs)
        #cnodePath.setScale(0.1)
        #cnodePath.show()
        self.banana.reparentTo(render)

        # bring some configuration parameters into memory, so we don't need to
        # reload the config file multiple times, also allows us to change these
        # variables dynamically
        self.numBeeps = config['numBeeps']
        #print config['trainingDirection']
        # for bananas, changing the angle from avatar to banana, so left is negative
        # right is positive.
        if config['trainingDirection'] == 'Right':
            self.trainDir = 'turnRight'
            self.multiplier = 1
        elif config['trainingDirection'] == 'Left':
            self.trainDir = 'turnLeft'
            self.multiplier = -1
        elif config['trainingDirection'] == 'Forward':
            self.trainDir = 'moveForward'
        #print('multiplier', self.multiplier)
        # not changing now, but may eventually...
        self.x_alpha = config['xHairAlpha']
        self.training = config['training']
        print self.training
        # variable used to notify when changing direction of new target
        self.new_dir = None
        # variable to notify when changing levels
        self.change_level = False

        if self.training > 1:
            # goal is to move to put banana under crosshair
            # need to load banana
            #print('banana position', self.banana_pos)
            #print('banana', self.banana_models.bananaModels[0].getPos())
            base.cTrav = CollisionTraverser()
            self.collHandler = CollisionHandlerQueue()
            #avatar = Avatar.getInstance()
            #print 'avatar'
            #print avatar.retrNodePath().getChild(0).node().getFromCollideMask()
            #print avatar.retrNodePath().getChild(0).node().getIntoCollideMask()
            #pointerNode = avatar.retrNodePath().attachNewNode('CrossHairRay')
            pointerNode = self.base.camera.attachNewNode(CollisionNode('CrossHairRay'))
            # ray that comes straight out from the camera
            raySolid = CollisionRay(0, 0, 0, 0, 1, 0)
            mainAimingNP = self.makeCollisionNodePath(pointerNode, raySolid)
            mainAimingNode = mainAimingNP.node()
            mainAimingNode.setIntoCollideMask(0)

            print 'ray'
            print mainAimingNode.getFromCollideMask()
            print mainAimingNode.getIntoCollideMask()
            base.cTrav.addCollider(mainAimingNP, self.collHandler)
            #base.cTrav.showCollisions(render)
            mainAimingNP.show()
            self.js_check = 0
            self.js_pos = None
            self.js_override = False
            if self.training >= 3:
                pass
                #self.fullForwardSpeed = config['fullForwardSpeed']
            elif self.training >= 2:
                self.avatar_h = 1
                #avatar.setH(self.multiplier * self.avatar_h)
                #self.fullTurningSpeed = config['fullTurningSpeed']
            self.avatar_pos = Point3(0, 0, 1)
            self.base.camera.setH(self.multiplier * self.avatar_h)
            # crosshair is always in center, but
            # need it to be in same place as collisionRay is, but it appears that center is
            # at the bottom left of the collisionRay, and the top right of the text, so they
            # don't have center in the same place. Makes more sense to move text than ray.
            # These numbers were scientifically determined. JK, moved around until the cross looked
            # centered on the ray
            #self.x_start_p = Point3(0, 0, 0)
            #self.x_start_p = Point3(-0.043, 0, 0.051)
            crosshair_pos = Point3(-0.07, 0, -0.05)
            self.collide_banana = False
            self.hold_aim = 0
            self.goal = 500  # number of frames to hold aim
        self.x_start_c = Point4(1, 1, 1, self.x_alpha)
        self.x_stop_c = Point4(1, 0, 0, self.x_alpha)
        self.crosshair = TextNode('crosshair')
        self.crosshair.setText('+')
        textNodePath = aspect2d.attachNewNode(self.crosshair)
        textNodePath.setScale(0.2)
        #print textNodePath.getPos()
        textNodePath.setPos(crosshair_pos)
        self.setup_inputs()
        self.delay_start = False
        self.yay_reward = False
        self.reward_delay = False
        self.reward_time = config['pulseInterval']  # usually 200ms
        self.reward_override = False
        self.reward_on = True
        self.delay = 1  # number of frames to wait for new "trial"
        self.t_delay = 0  # keeps track of frames waiting for new "trial"
        self.reward_count = 0
        self.frameTask.delay = 0
        self.x_mag = 0
        self.y_mag = 0
        self.slow_factor = 0.05  # factor to slow down movement of joystick
        self.moving = True

        # set up reward system
        if config['reward'] and PYDAQ_LOADED:
            self.reward = pydaq.GiveReward()
            print 'pydaq'
        else:
            self.reward = None
        #print Camera.defaultInstance.getFov()

    def frame_loop(self, task):
        # delay_start means we just gave reward and need to set wait time
        if self.delay_start:
            task.delay = task.time + self.reward_time
            #print('time now', task.time)
            #print('delay until', task.delay)
            self.delay_start = False
            #self.reward_delay = True
            return task.cont
        if task.time > task.delay:
            # check for reward
            if self.yay_reward and self.reward_count < self.numBeeps:
                #print 'reward'
                self.reward_count += 1
                self.give_reward()
                return task.cont
            elif self.yay_reward and self.reward_count == self.numBeeps:
                self.banana.stash()
                # hide the banana
                self.restart_bananas()
                return task.cont
            # check to see if we are moving
            if self.moving:
                self.base.camera.setH(self.base.camera.getH() + (self.x_mag * self.slow_factor * -self.multiplier))
                # check for collision:
                if self.training >= 3:
                    self.check_y_banana()
                elif self.training >= 2:
                    self.check_x_banana()
        return task.cont

    def give_reward(self):
        print('beep')
        if self.reward:
            self.reward.pumpOut()
        self.delay_start = True

    def check_x_banana(self):
        # check to see if crosshair is over banana, if so, stop turning, give reward
        # next stage is just slowing down after crosshair changes color, so he can go
        # past and has to turn back.
        if self.collHandler.getNumEntries() > 0:
            # the only object we can be running into is the banana, so there you go...
            self.collide_banana = True
            #print self.collHandler.getEntries()
        if self.collide_banana:
            #print 'collision'
            #posibilities after colliding with banana:
            # automatically just re-plots bananas (2)
            # requires subject to let go of joystick before re-plotting
            # subject has to line up crosshair to banana for min. time,
            # (optional, yet to be implemented, slows down if goes past banana)
            # stop moving
            self.moving = False
            # move to center
            if self.base.camera.getH != 0:
                #print 'moved camera'
                self.base.camera.setH(0)
            #print 'change xhair color to red'
            self.x_change_color(self.x_stop_c)
            self.yay_reward = True

    def check_y_banana(self):
        # This is checked every fricking frame, which means we go through this loop
        # many times per collision, except when I want it to. :/
        # check to see if crosshair is over banana, if so, stop turning, move it to centered, give reward
        # if self.collHandler.getNumEntries() > 0:
        #     # the only object we can be running into is the banana, so there you go...
        #     self.collide_banana = True
        #     #print self.collHandler.getEntries()
        # if self.collide_banana:
        #     #print 'collide'
        #     self.collide_banana = False
        if self.banana_models.beeps is None:
            return

        # Still here? Give reward!
        #print 'still here?'
        #print self.banana_models.beeps
        if self.reward_count < self.numBeeps:
            self.x_change_color(self.x_stop_c)
            #print 'reward'
            self.yay_reward = True
        elif self.reward_count == self.numBeeps:
            # banana disappears
            self.trial_num = self.banana_models.goneBanana(self.trial_num)
            # avatar can move
            #Avatar.getInstance().setMaxTurningSpeed(self.fullTurningSpeed)
            self.x_change_color(self.x_start_c)
            Avatar.getInstance().setPos(Point3(0, 0, 1))
            Avatar.getInstance().setH(0)
            Avatar.getInstance().setMaxForwardSpeed(self.fullForwardSpeed)
            # reward is over
            self.banana_models.beeps = None
            self.yay_reward = False
            self.reward_count = 0

    def restart_bananas(self):
        #print 'restarted'
        #self.banana_models.replenishBananas()
        # reset a couple of variables
        self.yay_reward = False
        self.t_delay = 0
        self.reward_count = 0
        self.collide_banana = False
        self.js_override = False
        #print self.trainDir
        #print self.multiplier
        # check to see if we are switching the banana to the other side
        if self.new_dir is not None:
            if self.new_dir == 1:
                # banana on left side, x = negative
                self.trainDir = 'turnRight'
                self.multiplier = -1
            elif self.new_dir == -1:
                # banana on right side, x = positive
                self.trainDir = 'turnLeft'
                self.multiplier = 1
            else:
                self.trainDir = 'moveForward'
            self.new_dir = None
            #print('change direction')
            #print('old position', self.banana_pos)
            #print('actual position', self.banana_models.bananaModels[0].getPos())
            #self.banana_pos[0] = abs(self.banana_pos[0]) * self.multiplier

        self.x_change_color(self.x_start_c)
        if self.change_level:
            print 'change level'
            self.training = self.change_level
            self.change_level = False
        #if self.multiplier == 1:
        #    self.banana_models.bananaModels[0].setH(280)
        #else:
        #    self.banana_models.bananaModels[0].setH(290)
        print('rotate avatar back so at correct angle:', self.avatar_h)
        self.base.camera.setH(self.multiplier * self.avatar_h)
        #Avatar.getInstance().setPos(self.avatar_pos)
        #Avatar.getInstance().setH(self.multiplier * self.avatar_h)
        print('avatar heading', self.base.camera.getH())
        # make sure banana in correct position
        # banana does not move, avatar moves or rotates
        #self.banana_models.bananaModels[0].setPos(self.banana_pos)
        # unhide banana
        self.banana.unstash()
        #print Avatar.getInstance().getPos()
        #print Camera.defaultInstance.getFov()
        #print self.banana_models.bananaModels[0].getPos()
        #print self.banana_models.bananaModels[0].getH()
        #print 'avatar can move again'
        self.moving = True
        #Avatar.getInstance().setMaxTurningSpeed(self.fullTurningSpeed)

    def x_change_color(self, color):
        #print self.crosshair.getColor()
        self.crosshair.setTextColor(color)
        #self.cross.setColor(Point4(1, 0, 0, 1))

    def move(self, js_dir, js_input):
        #print(js_dir, js_input)
        if abs(js_input) < 0.1:
            js_input = 0
        if js_dir == 'x':
            self.x_mag = js_input
            if self.training == 2:
                #print js_input
                if js_input * self.multiplier < 0:
                    #print 'no'
                    self.x_mag = 0
        else:
            self.y_mag = js_input

    def pause(self, inputEvent):
        # if we are less than the usual delay (so in delay or delay is over),
        # make it a giant delay,
        # otherwise end the delay period.
        if self.t_delay < self.delay:
            self.t_delay = 1000000
        else:
            self.t_delay = 0

    def inc_distance(self):
        if self.training == 2:
            print 'increase angle'
            #print('old pos', self.avatar_h)
            #self.avatar_h[0] = self.avatar_h[0] * 1.5
            self.avatar_h *= 1.5
            if abs(self.avatar_h) > 30:
                self.avatar_h = 30
            # y is always going to be positive
            #self.avatar_h[1] = sqrt(25 - self.avatar_h[0] ** 2)
            print('new heading', self.avatar_h)

    def dec_distance(self):
        if self.training == 2:
            print 'decrease angle'
            #print('old pos', self.avatar_h)
            self.avatar_h /= 1.5
            if abs(self.avatar_h) < 0.3:
                self.avatar_h = 0.3
            #self.banana_pos[0] = x_sign * (abs(self.banana_pos[0]) - 1)
            #self.banana_pos[1] = sqrt(25 - self.banana_pos[0] ** 2)
            print('new heading', self.avatar_h)

    def inc_reward(self):
        self.numBeeps += 1

    def dec_reward(self):
        self.numBeeps -= 1

    def inc_level(self):
        # cannot change into or out of level 1, only higher levels,
        # currently level 3 is highest
        if self.training == 1 or self.training == 3:
            self.change_level = self.training
            print 'cannot increase level'
        else:
            self.change_level = self.training + 1
        print('new level', self.change_level)

    def dec_level(self):
        if self.training == 1 or self.training == 2:
            self.change_level = self.training
            print 'cannot decrease level'
        else:
            self.change_level = self.training - 1
        print('new level', self.change_level)

    def inc_interval(self):
        self.delay += 1
        print('new delay', self.delay)

    def dec_interval(self):
        self.delay -= 1
        print('new delay', self.delay)

    def change_left(self):
        self.new_dir = 1
        print('new dir: left')

    def change_right(self):
        self.new_dir = -1
        print('new dir: right')

    def change_forward(self):
        self.new_dir = 0
        print('new dir: forward')

    def start_extra_reward(self):
        self.reward_override = True
        print('reward is: ', self.reward_override)

    def stop_extra_reward(self):
        self.reward_override = False
        print('reward is: ', self.reward_override)

    def makeCollisionNodePath(self, nodepath, solid):
        '''
        Creates a collision node and attaches the collision solid to the
        supplied NodePath. Returns the nodepath of the collision node.

        '''
        # Creates a collision node named after the name of the NodePath.
        collNode = CollisionNode("%s c_node" % nodepath.getName())
        collNode.addSolid(solid)
        collisionNodepath = nodepath.attachNewNode(collNode)
        # Show the collision node, which makes the solids show up.
        # actually, it appears to do nothing...
        collisionNodepath.show()
        return collisionNodepath

    def close(self):
        sys.exit()

    def setup_inputs(self):
        self.accept('x_axis', self.move, ['x'])
        self.accept('y_axis', self.move, ['y'])
        self.accept('arrow_right', self.move, ['x', 0.1])
        self.accept('arrow_left', self.move, ['x', -0.1])
        self.accept('q', self.close)
        self.accept('e', self.inc_distance)
        self.accept('d', self.dec_distance)
        self.accept('f', self.change_forward)
        self.accept('r', self.change_right)
        self.accept('l', self.change_left)
        self.accept('space', self.start_extra_reward)
        self.accept('space-up', self.stop_extra_reward)

unittest = False
if __name__ == '__main__':
    #print 'main?'
    TB = TrainingBananas()
    run()
else:
    unittest = True
