# cringe #
from pandaepl.common import *
from pandaepl import Joystick
from pandaepl import Model, ModelBase
#noinspection PyUnresolvedReferences
from panda3d.core import WindowProperties
from panda3d.core import CollisionNode, CollisionRay, GeomNode
from panda3d.core import CollisionTraverser, CollisionHandlerQueue, BitMask32
from load_models import load_models
from environment import PlaceModels
from bananas import Bananas
from math import sqrt
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
        # Get experiment instance.
        #print 'init'
        exp = Experiment.getInstance()
        #exp.setSessionNum(0)
        # Set session to today's date and time
        exp.setSessionNum(datetime.datetime.now().strftime("%y_%m_%d_%H_%M"))
        print exp.getSessionNum()
        config = Conf.getInstance().getConfig()  # Get configuration dictionary.
        #print config['training']
        #print 'load testing', config['testing']
        # bring some configuration parameters into memory, so we don't need to
        # reload the config file multiple times, also allows us to change these
        # variables dynamically
        self.numBeeps = config['numBeeps']
        #print config['trainingDirection']
        if config['trainingDirection'] == 'Left':
            self.trainDir = 'turnLeft'
            self.multiplier = -1
        elif config['trainingDirection'] == 'Right':
            self.trainDir = 'turnRight'
            self.multiplier = 1
        elif config['trainingDirection'] == 'Forward':
            self.trainDir = 'moveForward'
        #print('multiplier', self.multiplier)
        # not changing now, but may eventually...
        self.x_alpha = config['xHairAlpha']
        self.training = config['training']
        # should we reward backward pulls?
        self.backward = config['backward']
        # variable used to notify when changing direction of new target
        self.new_dir = None
        # variable to notify when changing levels
        self.change_level = False
        # get rid of cursor
        win_props = WindowProperties()
        #print win_props
        win_props.setCursorHidden(True)
        #win_props.setOrigin(20, 20)  # make it so windows aren't on top of each other
        #win_props.setSize(800, 600)  # normal panda window
        # base is global, used by pandaepl from panda3d
        base.win.requestProperties(win_props)

        vr = Vr.getInstance()

        self.js = Joystick.Joystick.getInstance()
        #print self.js

        # Register Custom Log Entries
        # This one corresponds to colliding with a banana
        Log.getInstance().addType("Yummy", [("BANANA", basestring)],
                                  False)
        # Reward
        Log.getInstance().addType('Beeps', [('Reward', int)],
                                            False)
        # Done getting reward, banana disappears
        Log.getInstance().addType("Finished", [("BANANA", basestring)],
                                  False)
        # New Trial
        Log.getInstance().addType("NewTrial", [("Trial", int)],
                                  False)
        # Log First Trial
        self.trial_num = 1
        VLQ.getInstance().writeLine("NewTrial", [self.trial_num])

        Log.getInstance().addType("EyeData", [("X", float),
                                              ("Y", float)],
                                              False)
        # Load environment
        self.load_environment(config)

        if self.training == 1:
            self.cross_move_int = config['xHairDist']
            self.x_start_p = config['xStartPos']
            self.config_x = config['beginning_x']
            #print('start pos', self.x_start_p)
        elif self.training > 1:
            self.banana_pos = config['startBanana']
            self.banana_models = Bananas(config)
            #print('banana position', self.banana_pos)
            #print('banana', self.banana_models.bananaModels[0].getPos())
            base.cTrav = CollisionTraverser()
            self.collHandler = CollisionHandlerQueue()
            avatar = Avatar.getInstance()
            avatar.retrNodePath().getChild(0).node().setIntoCollideMask(0)
            #print avatar.retrNodePath().getChild(0).node().getFromCollideMask()
            #print avatar.retrNodePath().getChild(0).node().getIntoCollideMask()
            pointerNode = avatar.retrNodePath().attachNewNode('CrossHairRay')
            # ray that comes straight out from the camera
            raySolid = CollisionRay(0, 0, 0, 0, 1, 0)
            mainAimingNP = self.makeCollisionNodePath(pointerNode, raySolid)
            mainAimingNode = mainAimingNP.node()
            mainAimingNode.setIntoCollideMask(0)
            #print 'ray'
            #print mainAimingNode.getFromCollideMask()
            #print mainAimingNode.getIntoCollideMask()
            base.cTrav.addCollider(mainAimingNP, self.collHandler)
            #base.cTrav.showCollisions(render)
            #mainAimingNP.show()
            if self.training == 2:
                self.fullTurningSpeed = config['fullTurningSpeed']
            else:
                self.fullForwardSpeed = config['fullForwardSpeed']
            # if using crosshair as real crosshair, always in center
            self.x_start_p = Point3(0, 0, 0)
            self.collide_banana = False
        else:
            self.x_start_p = Point3(0, 0, 0)
            # variables for counting how long to hold joystick
            self.js_count = 0
            # eventually may want start goal in config file
            self.js_goal = 1  # start out just have to hit joystick
            self.stop_reward = False
            self.old_joy = False
        self.x_start_p[0] *= self.multiplier
        self.x_start_c = Point4(1, 1, 1, self.x_alpha)
        self.x_stop_c = Point4(1, 0, 0, self.x_alpha)
        self.cross = Text("cross", '+', self.x_start_p, config['instructSize'], self.x_start_c)
        #self.cross = Model("cross", "smiley", Point3(self.x_start_p))
        #print(dir(self.cross))
        self.x_stop_p = Point3(0, 0, 0)

        self.yay_reward = False
        self.delay = 1  # number of updates to wait for new "trial" (200ms per update)
        self.t_delay = 0  # keeps track of updates waiting for new "trial"
        self.reward_count = 0
        self.reward_total = config['numBeeps']
        # set up reward system
        if config['reward'] and LOADED_PYDAQ:
            self.reward = pydaq.GiveReward()
            print 'pydaq'
        else:
            self.reward = None

        # start recording eye position
        if config['eyeData'] and LOADED_PYDAQ:
            self.gain = config['gain']
            self.offset = config['offset']
            self.task = pydaq.EOGTask()
            self.task.SetCallback(self.get_eye_data)
            self.task.StartTask()
        else:
            self.task = False

        #print Camera.defaultInstance.getFov()
        #Avatar.getInstance().getH()
        # Handle keyboard events
        #vr.inputListen('toggleDebug',
        #               lambda inputEvent:
        #               Vr.getInstance().setDebug(not Vr.getInstance().isDebug * ()))
        vr.inputListen("close", self.close)
        vr.inputListen("reward", self.give_extra_reward)
        vr.inputListen("increaseDist", self.x_inc_start)
        vr.inputListen("decreaseDist", self.x_dec_start)
        vr.inputListen("increaseInt", self.inc_interval)
        vr.inputListen("decreaseInt", self.dec_interval)
        vr.inputListen("increaseReward", self.inc_reward)
        vr.inputListen("decreaseReward", self.dec_reward)
        vr.inputListen("changeLeft", self.change_left)
        vr.inputListen("changeRight", self.change_right)
        vr.inputListen("changeForward", self.change_forward)
        vr.inputListen("allowBackward", self.allow_backward)
        # Can't change levels, since that involves changing the task,
        # may eventually be able to do this, if end up using same time
        # increment for tasks.
        vr.inputListen("increaseLevel", self.inc_level)
        vr.inputListen("decreaseLevel", self.dec_level)
        #vr.inputListen("increaseBananas", self.banana_models.increaseBananas)
        #vr.inputListen("decreaseBananas", self.banana_models.decreaseBananas)
        vr.inputListen("override", self.override)
        vr.inputListen("restart", self.restart)
        vr.inputListen("pause", self.pause)
        vr.inputListen("increaseTouch", self.inc_js_goal)
        vr.inputListen("decreaseTouch", self.dec_js_goal)
        # set up task to be performed between frames, do at reward interval
        # set by pump. This ends up to be pretty good. currently 200 ms
        vr.addTask(Task("checkJS",
                            lambda taskInfo:
                            self.tasks(),
                            config['pulseInterval']))
        if self.training == 2:
            vr.addTask(Task("checkCollisions",
                            lambda taskInfo:
                            self.check_collisions()))

        # vr.addTask(Task("checkReward",
        #                 lambda taskInfo:
        #                 self.check_reward(),
        #                 config['pulseInterval']))

    def tasks(self):
        #print('doing task', self.training)
        if self.training == 0:
            #print 'check_js'
            self.check_js()
        elif self.training == 1:
            self.check_position()
        else:
            self.check_reward()

    def check_js(self):
        # not moving crosshair, just push joystick to get reward,
        # longer and longer intervals
        # delay determines how long before cross re-appears
        #print 'in check_js'
        if self.t_delay == self.delay:
            joy_push = self.js.getEvents()
            js_good = False
            #print joy_push.keys()
            #for key in joy_push.keys():
            #    print joy_push[key]
            if self.stop_reward:
                self.x_change_color(self.x_start_c)
                #print 'stop'
                # if we are exactly the same as last time, we are still getting false positives.
                test = False
                for key in joy_push.keys():
                    now_key = joy_push[key]
                    try:
                        old_keys = self.old_joy
                        #print old_keys[key]
                        old_key = old_keys[key]
                    except KeyError:
                        old_key = None
                    #print now_key
                    #print old_key
                    try:
                        test = now_key == old_key
                    except AttributeError:
                        test = False
                        #print 'test true'
                if test:
                    self.old_joy = joy_push
                    joy_push = None
                else:
                    self.stop_reward = False
            else:
                self.old_joy = joy_push
            if joy_push:
                keys = joy_push.keys()
                size_test = len(keys)
                #print 'pushed'
                back = 'moveBackward' in keys
                print keys
                #print back
                if self.backward == 0:
                    # if rewarding for backward, then pushing joystick
                    # always get reward
                    js_good = True
                elif self.backward == 1:
                    if not back or size_test > 1:
                        # if not rewarding for straight backward, check to see if
                        # backward was (only) pushed before rewarding
                        js_good = True
                elif self.backward == 2 and not back:
                    js_good = True
            if js_good:
                print 'counts for reward'
                #print joy_push.keys()
                self.js_count += 1
                if self.js_count == self.js_goal:
                    self.x_change_color(self.x_stop_c)
                    self.give_reward()
                    #self.yay_reward = True
                    #print('touched for', self.js_count)
                    self.js_count = 0
                    self.t_delay = 0
            elif self.js_count >= 0:
                #print 'start over'
                self.x_change_color(self.x_start_c)
                self.js_count = 0
        else:
            self.t_delay += 1

    def check_position(self):
        # move crosshair
        # check to see if crosshair is in center, if so, stop it, give reward
        # if touches the joystick, move the crosshair,
        # multiply by the multiplier to get the absolute value,
        # so we can test if we are at the stopping position.
        # will have to change this when the stopping position is
        # no longer zero...
        # check for joystick movement
        test = self.js.getEvents()
        old_pos = self.cross.getPos()[0]
        old_pos *= self.multiplier
        #print old_pos
        stop_x = abs(self.x_stop_p[0])
        #if test:
            #print self.trainDir
            #print test.keys()
        #print('old', old_pos)
        #print('greater than', self.x_stop_p[0])
        if old_pos <= stop_x:
            self.yay_reward = True
            # if this is the original distance,
            # only one push of the joystick gets
            # us to center, no matter how far we are
        elif self.trainDir in test.keys():
            #print old_pos
            #print abs(self.config_x[0])
            #print round(old_pos, 2)
            if round(old_pos, 2) == abs(round(self.config_x[0], 2)) == abs(round(self.x_start_p[0], 2)):
                print('jump!')
                self.cross.setPos(Point3(0, 0, 0))
                self.yay_reward = True
            else:
                print('move')
                # move closer to zero
                old_pos -= self.cross_move_int
                # go back to original direction
                old_pos *= self.multiplier
                # now change the position
                new_pos = self.cross.getPos()
                new_pos[0] = old_pos
                #print('new', new_pos)
                self.cross.setPos(new_pos)
        # Runs every 200ms, same rate as pump rate
        # check to see if crosshair is in center, if so, stop it, give reward
        #if self.training == 0:
        #    self.check_js()
        #elif self.training == 1:
        # once delay is over, makes sure not touching joystick
        # before new trial
        if self.yay_reward:
            #print 'yay_reward is true'
            #print self.reward_count
            if self.reward_count == self.reward_total:
                # reward over
                self.x_change_color(self.x_start_c)
                # delay before next trial?
                if self.t_delay == self.delay:
                    # if let go of joystick, can start over
                    if not test:
                        self.t_delay = 0
                        self.reward_count = 0
                        self.restart()
                else:
                    self.t_delay += 1
                    #print self.t_delay
            else:
                # giving reward
                self.reward_count += 1
                #print 'reward'
                self.x_change_color(self.x_stop_c)
                self.give_reward()

    def check_collisions(self):
        # This is checked every fricking frame, which means we go through this loop
        # many times per collision, except when I want it to. :/
        # check to see if crosshair is over banana, if so, stop turning, move it to centered, give reward
        if self.collHandler.getNumEntries() > 0:
            # the only object we can be running into is the banana, so there you go...
            self.collide_banana = True
            #print self.collHandler.getEntries()
        if self.collide_banana:
            test = self.js.getEvents()
            if self.reward_count == self.reward_total:
                #print 'change xhair color to white'
                self.x_change_color(self.x_start_c)
                if self.t_delay == self.delay:
                    #print 'delay over'
                    #print 'please let go of joystick'
                    # if let go of joystick, can start over
                    if not test:
                        #print 'did let go of joystick'
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
                #print Avatar.getInstance().getH()
                #print('mulitplier', self.multiplier)
                if self.multiplier == 1:
                    # left
                    avatar_change = -0.5
                else:
                    #right
                    avatar_change = 3
                Avatar.getInstance().setH(Avatar.getInstance().getH() + avatar_change)
                #print Avatar.getInstance().getH()
                #print 'change xhair color to red'
                self.x_change_color(self.x_stop_c)
                self.yay_reward = True

    def check_reward(self):
        if self.yay_reward and self.reward_count < self.reward_total:
            #print 'reward'
            self.reward_count += 1
            self.give_reward()

    def restart(self):
        #print 'restarted'
        #self.banana_models.replenishBananas()
        self.yay_reward = False
        self.t_delay = 0
        if self.new_dir is not None:
            if self.new_dir == 1:
                self.trainDir = 'turnRight'
                self.multiplier = 1
            elif self.new_dir == -1:
                self.trainDir = 'turnLeft'
                self.multiplier = -1
            else:
                self.trainDir = 'moveForward'
            self.new_dir = None
            self.x_start_p[0] = abs(self.x_start_p[0]) * self.multiplier
        print('xhair position', self.x_start_p)
        self.x_change_position(self.x_start_p)
        self.x_change_color(self.x_start_c)
        if self.change_level:
            print 'change level'
            self.training = self.change_level
            self.change_level = False

    def restart_bananas(self):
        #print 'restarted'
        # first hide the banana
        self.banana_models.bananaModels[0].setStashed(True)
        #self.banana_models.replenishBananas()
        # reset a couple of variables
        self.yay_reward = False
        self.t_delay = 0
        self.reward_count = 0
        self.collide_banana = False
        #print self.trainDir
        #print self.multiplier
        # check to see if we are switching the banana to the other side
        if self.new_dir is not None:
            if self.new_dir == 1:
                # banana on left side, x = negative
                self.trainDir = 'turnRight'
                self.multiplier = 1
            elif self.new_dir == -1:
                # banana on right side, x = positive
                self.trainDir = 'turnLeft'
                self.multiplier = -1
            else:
                self.trainDir = 'moveForward'
            self.new_dir = None
            #print('change direction')
            #print('old position', self.banana_pos)
            #print('actual position', self.banana_models.bananaModels[0].getPos())
            self.banana_pos[0] = abs(self.banana_pos[0]) * self.multiplier
            #self.x_start_p[0] = abs(self.x_start_p[0]) * self.multiplier
        #print('xhair position', self.x_start_p)
        #print('banana position', self.banana_pos)
        #self.x_change_position(self.x_start_p)
        self.x_change_color(self.x_start_c)
        if self.change_level:
            print 'change level'
            self.training = self.change_level
            self.change_level = False
        if self.multiplier == 1:
            self.banana_models.bananaModels[0].setH(280)
        else:
            self.banana_models.bananaModels[0].setH(290)
        #print 'move avatar back to center, facing original direction'
        Avatar.getInstance().setPos(Point3(0, 0, 1))
        Avatar.getInstance().setH(0)

        # make sure banana in correct position
        self.banana_models.bananaModels[0].setPos(self.banana_pos)
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

    def give_reward(self):
        # used for task where cross moves (or anytime single reward is wanted)
        print('beep')
        if self.reward:
            self.reward.pumpOut()

    def give_extra_reward(self, inputEvent):
        self.x_change_color(self.x_start_c)
        self.give_reward()
        self.x_change_color(self.x_stop_c)

    def override(self, inputEvent):
        # sometimes we get a signal from the joystick when it is not being touched
        self.stop_reward = True

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
                self.x_start_p[0] = self.multiplier * 0.9
            print('new pos', self.x_start_p)
            #print self.config_x
        elif self.training == 2:
            print 'increase distance'
            #print('old pos', self.banana_pos)
            #self.banana_pos[0] = self.banana_pos[0] * 1.5
            self.banana_pos[0] *= 1.5
            if abs(self.banana_pos[0]) > 2:
                self.banana_pos[0] = self.multiplier * 2
            # y is always going to be positive
            self.banana_pos[1] = sqrt(25 - self.banana_pos[0] ** 2)
            print('new pos', self.banana_pos)

    def x_dec_start(self, inputEvent):
        if self.training == 1:
            self.x_start_p[0] *= 0.5
            # don't go too crazy getting infinitely close to zero. :)
            if self.x_start_p[0] < 0.01:
                self.x_start_p[0] = 0.01
            print('new pos', self.x_start_p)
        elif self.training == 2:
            print 'decrease distance'
            #print('old pos', self.banana_pos)
            self.banana_pos[0] /= 1.5
            if abs(self.banana_pos[0]) < 0.5:
                self.banana_pos[0] = self.multiplier * 0.5
            #self.banana_pos[0] = x_sign * (abs(self.banana_pos[0]) - 1)
            self.banana_pos[1] = sqrt(25 - self.banana_pos[0] ** 2)
            print('new pos', self.banana_pos)

    def inc_reward(self, inputEvent):
        self.reward_total += 1

    def dec_reward(self, inputEvent):
        self.reward_total -= 1

    def inc_level(self, inputEvent):
        self.change_level = self.training + 1
        print('new level', self.change_level)

    def dec_level(self, inputEvent):
        self.change_level = self.training - 1
        if self.change_level < 0:
            self.change_level = 0
        print('new level', self.change_level)

    def inc_js_goal(self, inputEvent):
        self.js_goal += 1
        print('new goal', self.js_goal)

    def dec_js_goal(self, inputEvent):
        self.js_goal -= 1
        print('new goal', self.js_goal)

    def inc_interval(self, inputEvent):
        self.delay += 1
        print('new delay', self.delay)

    def dec_interval(self, inputEvent):
        self.delay -= 1
        print('new delay', self.delay)

    def change_left(self, inputEvent):
        self.new_dir = -1
        print('new dir: left')

    def change_right(self, inputEvent):
        self.new_dir = 1
        print('new dir: right')

    def change_forward(self, inputEvent):
        self.new_dir = 0
        print('new dir: forward')

    def allow_backward(self, inputEvent):
        self.backward += 1
        if self.backward > 2:
            self.backward = 0
        print('backward allowed:', self.backward)

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
