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
        self.extra = config['extra']
        #self.fullTurningSpeed = config['fullTurningSpeed']
        #self.fullForwardSpeed = config['fullForwardSpeed']
       #print config['trainingDirection']
        if config['trainingDirection'] == 'Left':
            self.trainDir = 'turnLeft'
            self.multiplier = -1
        elif config['trainingDirection'] == 'Right':
            self.trainDir = 'turnRight'
            self.multiplier = 1
        elif config['trainingDirection'] == 'Forward':
            self.trainDir = 'moveForward'
        #print self.multiplier
        self.cross_move_int = config['xHairDist']
        self.x_alpha = config['xHairAlpha']
        self.training = config['training']
        # variables for counting how long to hold joystick
        self.js_count = 0
        # eventually may want start goal in config file
        self.js_goal = 1  # start out just have to hit joystick
        # default is to reward for backward movement. May want
        # to make this a configuration option instead.
        # zero, all backward allowed
        # one, straight backward not rewarded
        # two, no backward rewarded
        self.backward = 0
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
            self.x_start_p = config['xStartPos']
            self.config_x = config['beginning_x']
            print('start pos', self.x_start_p)
        elif self.training == 2:
            self.banana_pos = config['startBanana']
            self.banana_models = Bananas(config)
            print('banana position', self.banana_pos)
            base.cTrav = CollisionTraverser()
            self.collHandler = CollisionHandlerQueue()

            #self.pointerNode = render.attachNewNode('CrossHairRay')
            #cam = Camera.defaultInstance
            #print cam
            #camNode = Camera.defaultInstance.retrNodePath()
            #print camNode
            #print camNode.getChild()
            #print camNode.retrNodePath()
            #xhairNP = cam.attachNewNode(xhairNode)
            #xhairNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
            avatar = Avatar.getInstance()
            print 'avatar'
            print avatar.retrNodePath().getChild(0).node().setIntoCollideMask(0)
            print avatar.retrNodePath().getChild(0).node().getFromCollideMask()
            print avatar.retrNodePath().getChild(0).node().getIntoCollideMask()
            self.pointerNode = avatar.retrNodePath().attachNewNode('CrossHairRay')
            # ray that comes straight out from the camera
            raySolid = CollisionRay(0, 0, 0, 0, 1, 0)
            mainAimingNP = self.makeCollisionNodePath(self.pointerNode, raySolid)
            self.mainAimingNode = mainAimingNP.node()
            self.mainAimingNode.setIntoCollideMask(0)
            print 'ray'
            print self.mainAimingNode.getFromCollideMask()
            print self.mainAimingNode.getIntoCollideMask()
            base.cTrav.addCollider(mainAimingNP, self.collHandler)
            base.cTrav.showCollisions(render)
            self.fullTurningSpeed = config['fullTurningSpeed']
            #raySolid.setFromLens(lensNode, 0, 0)
            #xhairRay.setFromLens(lensNode, 0, 0)
            #xhairNP.show()
            #self.collTrav.addCollider(xhairNP, self.rayColQueue)
            #self.collTrav.traverse(render)
            # if using crosshair as real crosshair, always in center
            self.x_start_p = Point3(0, 0, 0)
        else:
            self.x_start_p = Point3(0, 0, 0)
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

        # Handle keyboard events
        #vr.inputListen('toggleDebug',
        #               lambda inputEvent:
        #               Vr.getInstance().setDebug(not Vr.getInstance().isDebug * ()))
        vr.inputListen("close", self.close)
        vr.inputListen("reward", self.give_reward)
        vr.inputListen("increaseDist", self.x_inc_start)
        vr.inputListen("decreaseDist", self.x_dec_start)
        vr.inputListen("increaseInt", self.inc_interval)
        vr.inputListen("decreaseInt", self.dec_interval)
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
            self.check_banana()

    def check_js(self):
        # not moving crosshair, just push joystick to get reward,
        # longer and longer intervals
        # delay determines how long before cross re-appears
        #print 'in check_js'
        if self.t_delay == self.delay:
            joy_push = self.js.getEvents()
            js_good = False
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

    def check_banana(self):
        # check to see if crosshair is over banana, if so, stop it, give reward
        #self.rayColQueue.sortEntries()
        #for i in range(self.rayColQueue.getNumEntries()):
        #    entry = self.rayColQueue.getEntry(i)
        #    print entry
        if self.collHandler.getNumEntries() > 0:
            # the only object we can be running into is the banana, so there you go...
            self.yay_reward = True


            #self.collHandler.sortEntries()
            #pickedObj = self.collHandler.getEntry(0).getIntoNodePath()
            #print pickedObj

        #self.collHandler.sortEntries()
        #for i in range(self.collHandler.getNumEntries()):
        #    entry = self.collHandler.getEntry(i)
        #    print entry
            #if 'banana00' in entry:
            #    print 'yes'
        test = self.js.getEvents()
        if self.yay_reward:
            if self.reward_count == self.reward_total:
                self.x_change_color(self.x_start_c)
                if self.t_delay == self.delay:
                    # if let go of joystick, can start over
                    if not test:
                        self.t_delay = 0
                        #print dir(self.banana_models.bananaModels[0])
                        self.banana_models.bananaModels[0].setPos(self.banana_pos)
                        Avatar.getInstance().setMaxTurningSpeed(self.fullTurningSpeed)
                        self.reward_count = 0
                        self.restart()
                else:
                    self.t_delay += 1
                    print self.t_delay
            else:
                # stop the avatar during reward
                Avatar.getInstance().setMaxTurningSpeed(0)
                self.reward_count += 1
                print 'reward'
                self.x_change_color(self.x_stop_c)
                self.give_reward()

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

    def give_reward(self, inputEvent=None):
        # used for task where cross moves
        print('beep')
        if self.reward:
            self.reward.pumpOut()

    def pause(self, inputEvent):
        # if we are less than the usual delay (so in delay or delay is over),
        # make it a giant delay,
        # otherwise end the delay period.
        if self.t_delay < self.delay:
            self.t_delay = 1000000
        else:
            self.t_delay = 0

    def x_inc_start(self, inputEvent):
        print self.config_x
        self.x_start_p[0] *= 2
        if abs(self.x_start_p[0]) > 0.9:
            self.x_start_p[0] = self.multiplier * 0.9
        print('new pos', self.x_start_p)
        print self.config_x

    def x_dec_start(self, inputEvent):
        self.x_start_p[0] *= 0.5
        # don't go too crazy getting infinitely close to zero. :)
        if self.x_start_p[0] < 0.01:
            self.x_start_p[0] = 0.01
        print('new pos', self.x_start_p)

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
        self.new_dir = 1
        print('new dir: left')

    def change_right(self, inputEvent):
        self.new_dir = -1
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
        collisionNodepath.show()

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
                model = Model(item.name, item.model, item.location)
                if item.callback is not None:
                    #print 'not none'
                    model.setCollisionCallback(eval(item.callback))
                    # white wall is bright, and sometimes hard to see bananas,
                    # quick fix.
                    model.nodePath.setColor(0.8, 0.8, 0.8, 1.0)
                model.setScale(item.scale)
                model.setH(item.head)
                self.envModels.append(model)

    def restart(self):
        #print 'restarted'
        #self.banana_models.replenishBananas()
        self.yay_reward = False
        self.t_delay = 0
        if self.new_dir is not None:
            if self.new_dir == 1:
                self.trainDir = 'turnLeft'
                self.multiplier = 1
            elif self.new_dir == -1:
                self.trainDir = 'turnRight'
                self.multiplier = -1
            else:
                self.trainDir = 'moveForward'
            self.new_dir = None
            self.x_start_p[0] = abs(self.x_start_p[0]) * self.multiplier
        print(self.x_start_p)
        self.x_change_position(self.x_start_p)
        self.x_change_color(self.x_start_c)
        if self.change_level:
            print 'change level'
            self.training = self.change_level
            self.change_level = False

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
