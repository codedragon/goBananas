from direct.showbase.ShowBase import ShowBase
from joystick import JoystickHandler
from panda3d.core import WindowProperties
from panda3d.core import CollisionNode, CollisionRay
from panda3d.core import CollisionTraverser, CollisionHandlerQueue
import datetime
import sys
# only load pydaq if it's available
try:
    sys.path.insert(1, '../pydaq')
    import pydaq
    LOADED_PYDAQ = True
    #print 'loaded PyDaq'
except ImportError:
    LOADED_PYDAQ = False
    print 'Not using PyDaq'


class TrainBananas:
    def __init__(self):
        """
        Initialize the experiment
        """
        self.base = ShowBase()
        config = {}
        execfile('train_config.py', config)
        JoystickHandler.__init__(self)
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
            # ray that comes straight out from the camera
            #raySolid = CollisionRay(0, 0, 0, 0, 1, 0)
            #mainAimingNP = self.makeCollisionNodePath(pointerNode, raySolid)
            #mainAimingNode = mainAimingNP.node()
            #mainAimingNode.setIntoCollideMask(0)
            #print 'ray'
            #print mainAimingNode.getFromCollideMask()
            #print mainAimingNode.getIntoCollideMask()
            #base.cTrav.addCollider(mainAimingNP, self.collHandler)
            self.js_check = 0
            self.js_pos = None
            self.js_override = False
            #base.cTrav.showCollisions(render)
            #mainAimingNP.show()
            if self.training >= 3:
                pass
                #self.fullForwardSpeed = config['fullForwardSpeed']
            elif self.training >= 2:
                self.avatar_h = 2
                #avatar.setH(self.multiplier * self.avatar_h)
                #self.fullTurningSpeed = config['fullTurningSpeed']
            self.avatar_pos = Point3(0, 0, 1)
            # crosshair is always in center, but
            # need it to be in same place as collisionRay is, but it appears that center is
            # at the bottom left of the collisionRay, and the top right of the text, so they
            # don't have center in the same place. Makes more sense to move text than ray.
            # These numbers were scientifically determined. JK, moved around until the cross looked
            # centered on the ray
            #self.x_start_p = Point3(0, 0, 0)
            #self.x_start_p = Point3(-0.043, 0, 0.051)
            self.x_start_p = Point3(-0.05, 0, 0.051)
            self.collide_banana = False
            self.hold_aim = 0
            self.goal = 500  # number of frames to hold aim
        self.x_start_c = Point4(1, 1, 1, self.x_alpha)
        self.x_stop_c = Point4(1, 0, 0, self.x_alpha)
        self.cross = TextNode('crosshair')
        self.cross.setText('+')
        textNodePath = aspect2d.attachNewNode(self.cross)
        textNodePath.setScale(0.2)
        self.cross = Text("cross", '+', self.x_start_p, config['instructSize'], self.x_start_c)

        self.delay_start = False
        self.reward_delay = False
        self.reward_time = config['pulseInterval']  # usually 200ms
        self.reward_override = False
        self.reward_on = True
        self.delay = 1  # number of frames to wait for new "trial"
        self.t_delay = 0  # keeps track of frames waiting for new "trial"
        self.reward_count = 0

        # set up reward system
        if config['reward'] and LOADED_PYDAQ:
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
            self.reward_on = True
            # do a bunch of checks, which might turn reward back off
        if self.reward_on:
            self.reward_on = False
        if self.reward_on or self.reward_override:
            # give reward!
            self.crosshair.setTextColor(1, 0, 0, 1)
            self.give_reward()
        else:
            self.crosshair.setTextColor(1, 1, 1, 1)
        #print('doing task', self.training)
        # if self.training >= 3:
        #     self.check_y_banana()
        # elif self.training >= 2:
        #     self.check_x_banana()

    def give_reward(self):
        print('beep')
        if self.reward:
            self.reward.pumpOut()

    def check_x_banana(self):
        # This is checked every fricking frame, which means we go through this loop
        # many times per collision, except when I want it to. :/
        # check to see if crosshair is over banana, if so, stop turning, give reward
        # next stage is just slowing down after crosshair changes color, so he can go
        # past and has to turn back.
        if self.collHandler.getNumEntries() > 0:
            # the only object we can be running into is the banana, so there you go...
            self.collide_banana = True
            #print self.collHandler.getEntries()
        else:
            #print('meh')
            # start over with holding
            self.hold_aim = 0
            self.x_change_color(self.x_start_c)
        if self.collide_banana:
            #print 'collision'
            #posibilities after colliding with banana:
            # automatically just re-plots bananas (2)
            # requires subject to let go of joystick before re-plotting
            # subject has to line up crosshair to banana for min. time,
            # (optional, yet to be implemented, slows down if goes past banana)
            if self.training == 2.1:
                test = self.js.getEvents()
            elif self.training == 2.2 and not self.yay_reward:
                #print 'change xhair color to red'
                self.x_change_color(self.x_stop_c)
                test = False
                if self.hold_aim < self.goal:
                    self.hold_aim += 1
                    #print('keep holding', self.hold_aim)
                    return
            else:
                test = False
            #print test
            #print test.keys()
            #if 'turnRight' in test.keys():
            #print test['turnRight']
            #mag_test = test.keys()
            #print test[mag_test[0]]
            #print test[mag_test[0]]
            if self.reward_count == self.numBeeps:
                print 'change xhair color to white'
                self.x_change_color(self.x_start_c)
                # hide the banana
                self.banana_models.bananaModels[0].setStashed(True)
                if self.t_delay == self.delay:
                    print 'delay over'
                    #print 'please let go of joystick'
                    # if let go of joystick, can start over
                    # pandaepl is doing something screwy, and I sometimes get
                    # signals from the joystick after it has been released, these
                    # are always exactly the same signal over and over, so check
                    # for the same signal for a few frames.
                    #mag_test = test.keys()
                    # meh. how do I just get the number out of this dictionary!
                    # InputEvent: turnRight, mag:0.464705343791
                    # if mag_test:
                    #     print test[mag_test[0]]
                    #     if self.js_pos is test[mag_test[0]]:
                    #         self.js_check += 1
                    #         print 'um, yeah'
                    #     else:
                    #         self.js_pos = test[mag_test[0]]

                    #if not test or self.js_check == 2:
                    if not test or self.js_override:
                        print 'did let go of joystick'
                        self.restart_bananas()
                        #print 'end conditional'
                else:
                    #print 'wait for delay'
                    self.t_delay += 1
                    #print('t_delay', self.t_delay)
            elif not self.yay_reward:
                # will do this else statement until reward finished.
                # stop the avatar during reward
                #print 'stop avatar'
                Avatar.getInstance().setMaxTurningSpeed(0)
                h = Avatar.getInstance().getH()
                print('avatar heading', h)
                if h != 0:
                    Avatar.getInstance().setH(0)
                #Avatar.getInstance().setH(Avatar.getInstance().getH() + avatar_change)
                #print Avatar.getInstance().getH()
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
        #self.yay_reward = False
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
        Avatar.getInstance().setPos(self.avatar_pos)
        Avatar.getInstance().setH(self.multiplier * self.avatar_h)
        print('avatar heading', Avatar.getInstance().getH())
        # make sure banana in correct position
        # banana does not move, avatar moves or rotates
        #self.banana_models.bananaModels[0].setPos(self.banana_pos)
        # unhide banana
        self.banana_models.bananaModels[0].setStashed(False)
        #print Avatar.getInstance().getPos()
        #print Camera.defaultInstance.getFov()
        #print self.banana_models.bananaModels[0].getPos()
        #print self.banana_models.bananaModels[0].getH()
        #print 'avatar can move again'
        Avatar.getInstance().setMaxTurningSpeed(self.fullTurningSpeed)

    def get_eye_data(self, eye_data):
        # pydaq calls this function every time it calls back to get eye data
        VLQ.getInstance().writeLine("EyeData",
                                [((eye_data[0] * self.gain[0]) - self.offset[0]),
                                ((eye_data[1] * self.gain[1]) - self.offset[1])])

    def x_change_position(self, position):
        self.cross.setPos(Point3(position))

    def x_change_color(self, color):
        #print self.cross.getColor()
        self.cross.setColor(color)
        #self.cross.setColor(Point4(1, 0, 0, 1))

    def give_extra_reward(self, inputEvent):
        self.x_change_color(self.x_start_c)
        self.give_reward()
        self.x_change_color(self.x_stop_c)

    def override(self, inputEvent):
        # sometimes we get a signal from the joystick when it is not being touched,
        # this will either stop a reward out of control, or start the next trial, if
        # the program wrongly believes subject is still touching joystick
        self.stop_reward = True
        self.js_override = True

    def pause(self, inputEvent):
        # if we are less than the usual delay (so in delay or delay is over),
        # make it a giant delay,
        # otherwise end the delay period.
        if self.t_delay < self.delay:
            self.t_delay = 1000000
        else:
            self.t_delay = 0

    def x_inc_start(self, inputEvent):
        if self.training == 1:
            #print self.config_x
            self.x_start_p[0] *= 2
            if abs(self.x_start_p[0]) > 0.9:
                self.x_start_p[0] = -self.multiplier * 0.9
            print('new pos', self.x_start_p)
            #print self.config_x
        elif self.training == 2:
            print 'increase angle'
            #print('old pos', self.avatar_h)
            #self.avatar_h[0] = self.avatar_h[0] * 1.5
            self.avatar_h *= 1.5
            if abs(self.avatar_h) > 30:
                self.avatar_h = 30
            # y is always going to be positive
            #self.avatar_h[1] = sqrt(25 - self.avatar_h[0] ** 2)
            print('new heading', self.avatar_h)

    def x_dec_start(self, inputEvent):
        if self.training == 1:
            self.x_start_p[0] *= 0.5
            # don't go too crazy getting infinitely close to zero. :)
            if abs(self.x_start_p[0]) < 0.01:
                self.x_start_p[0] = -self.multiplier * 0.01
            print('new pos', self.x_start_p)
        elif self.training == 2:
            print 'decrease angle'
            #print('old pos', self.avatar_h)
            self.avatar_h /= 1.5
            if abs(self.avatar_h) < 0.3:
                self.avatar_h = 0.3
            #self.banana_pos[0] = x_sign * (abs(self.banana_pos[0]) - 1)
            #self.banana_pos[1] = sqrt(25 - self.banana_pos[0] ** 2)
            print('new heading', self.avatar_h)

    def inc_reward(self, inputEvent):
        self.numBeeps += 1

    def dec_reward(self, inputEvent):
        self.numBeeps -= 1

    def inc_level(self, inputEvent):
        # cannot change into or out of level 1, only higher levels,
        # currently level 3 is highest
        if self.training == 1 or self.training == 3:
            self.change_level = self.training
            print 'cannot increase level'
        else:
            self.change_level = self.training + 1
        print('new level', self.change_level)

    def dec_level(self, inputEvent):
        if self.training == 1 or self.training == 2:
            self.change_level = self.training
            print 'cannot decrease level'
        else:
            self.change_level = self.training - 1
        print('new level', self.change_level)

    def inc_interval(self, inputEvent):
        self.delay += 1
        print('new delay', self.delay)

    def dec_interval(self, inputEvent):
        self.delay -= 1
        print('new delay', self.delay)

    def change_left(self, inputEvent):
        self.new_dir = 1
        print('new dir: left')

    def change_right(self, inputEvent):
        self.new_dir = -1
        print('new dir: right')

    def change_forward(self, inputEvent):
        self.new_dir = 0
        print('new dir: forward')

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
        #collisionNodepath.show()

        return collisionNodepath

    def load_environment(self, config):
        if config['environ'] is None:
            return
        load_models()
        # Models must be attached to self
        self.envModels = []
        for item in PlaceModels._registry:
            if config['environ'] in item.group:
            #if 'better' in item.group:
                #print item.name
                item.model = config['path_models'] + item.model
                #print item.model
                model = Model.Model(item.name, item.model, item.location)
                if item.callback is not None:
                    #print 'not none'
                    model.setCollisionCallback(eval(item.callback))
                    # white wall is bright, and sometimes hard to see bananas,
                    # quick fix.
                    model.nodePath.setColor(0.8, 0.8, 0.8, 1.0)
                model.setScale(item.scale)
                model.setH(item.head)
                self.envModels.append(model)

    def start(self):
        """
        Start the experiment.
        """
        #print 'start'
        Experiment.getInstance().start()

    def close(self, inputEvent):
        if self.task:
            self.task.StopTask()
            self.task.ClearTask()
        Experiment.getInstance().stop()

if __name__ == '__main__':
    #print 'main?'
    TrainBananas().start()
else:
    print 'not main?'
    #import argparse
    #p = argparse.ArgumentParser()
    #p.add_argument('-scrap')
    #import sys
    #sys.argv.extend(['stest'])
    #sys.argv = ['goBananas','-stest']
    #,'--no-eeg','--no-fs']
    #GoBananas().start()
