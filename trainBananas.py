# cringe #
from pandaepl.common import *
from pandaepl import Joystick
#from pandaepl import Model, MovingObject
#noinspection PyUnresolvedReferences
from panda3d.core import WindowProperties
#from panda3d.core import CollisionNode, CollisionSphere
from load_models import load_models
from environment import PlaceModels
from bananas import Bananas
import datetime
import sys
# only load pydaq if it's available
try:
    sys.path.insert(1, '../pydaq')
    import pydaq
    #print 'loaded PyDaq'
except ImportError:
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
        if config['trainingDirection'] == 'Left':
            self.trainDir = 'turnLeft'
            self.multiplier = 1
        elif config['trainingDirection'] == 'Right':
            self.trainDir = 'turnRight'
            self.multiplier = -1
        elif config['trainingDirection'] == 'Forward':
            self.trainDir = 'moveForward'
        self.new_dir = None
        # get rid of cursor
        win_props = WindowProperties()
        #print win_props
        win_props.setCursorHidden(True)
        #win_props.setOrigin(20, 20)  # make it so windows aren't on top of each other
        #win_props.setSize(800, 600)  # normal panda window
        # base is global, used by pandaepl from panda3d
        base.win.requestProperties(win_props)

        # Get vr environment object
        #print Vr
        #print Options
        #options = Options.getInstance()
        #print Joystick
        #print options.__dict__.keys()
        #print options.option_list
        #print options.values
        vr = Vr.getInstance()
        #vr.cTrav.showCollisions(render)
        self.js = Joystick.Joystick.getInstance()
        # not using experiment state currently
        #if not exp.getState():
            #bananas = []

        # Get avatar object
        #avatar = Avatar.getInstance()
        #collisionNode = avatar.retrNodePath().find('**/+CollisionNode')
        #collisionNode.show()
        #collisionNode.setTwoSided(True)

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

        #self.banana_models = Bananas(config)
        self.x_start_p = config['xStartPos']
        self.x_start_p[0] *= self.multiplier
        print self.x_start_p
        self.x_alpha = config['xHairAlpha']
        self.x_start_c = Point4(1, 1, 1, self.x_alpha)
        self.x_stop_c = Point4(1, 0, 0, self.x_alpha)
        self.cross = Text("cross", '+', self.x_start_p, config['instructSize'], self.x_start_c)
        #self.cross = Model("cross", "smiley", Point3(self.x_start_p))
        #print(dir(self.cross))
        self.x_stop_p = Point3(0, 0, 0)
        self.cross_move_int = config['xHairDist']
        self.training = config['training']
        self.yay_reward = False
        self.delay = 0  # number of updates to wait for new "trial" (200ms per update)
        self.t_delay = 0
        # set up reward system
        if config['reward']:
            self.reward = pydaq.GiveReward()
            print 'pydaq'
        else:
            self.reward = None

        # start recording eye position
        if config['eyeData']:
            self.gain = config['gain']
            self.offset = config['offset']
            self.task = pydaq.EOGTask()
            self.task.SetCallback(self.get_eye_data)
            self.task.StartTask()
        else:
            self.task = False

        # Handle keyboard events
        vr.inputListen('toggleDebug',
                       lambda inputEvent:
                       Vr.getInstance().setDebug(not Vr.getInstance().isDebug * ()))
        vr.inputListen("close", self.close)
        vr.inputListen("reward", self.give_reward)
        vr.inputListen("increaseDist", self.x_inc_start)
        vr.inputListen("decreaseDist", self.x_dec_start)
        vr.inputListen("increaseInt", self.inc_interval)
        vr.inputListen("decreaseInt", self.dec_interval)
        vr.inputListen("changeLeft", self.change_left)
        vr.inputListen("changeRight", self.change_right)
        vr.inputListen("changeForward", self.change_forward)
        # Can't change levels, since that involves changing the task,
        # may eventually be able to do this, if end up using same time
        # increment for tasks.
        #vr.inputListen("increaseLevel", self.inc_level)
        #vr.inputListen("decreaseLevel", self.dec_level)
        #vr.inputListen("increaseBananas", self.banana_models.increaseBananas)
        #vr.inputListen("decreaseBananas", self.banana_models.decreaseBananas)
        vr.inputListen("restart", self.restart)
        vr.inputListen("pause", self.pause)
        # set up task to be performed between frames
        if self.training == 0:
            vr.inputListen("increaseTouch", self.inc_js_goal)
            vr.inputListen("decreaseTouch", self.dec_js_goal)
            self.js_count = 0
            # eventually may want start goal in config file
            self.js_goal = 1  # start out just have to hit joystick
            vr.addTask(Task("checkJS",
                            lambda taskInfo:
                            self.check_js(),
                            200))
        else:
            vr.addTask(Task("checkReward",
                        lambda taskInfo:
                        self.check_reward(),
                        config['pulseInterval']))

    def check_js(self):
        # not moving crosshair, just push joystick to get reward,
        # longer and longer intervals
        if self.t_delay == self.delay:
            joy_push = self.js.getEvents()
            if joy_push:
                self.js_count += 1
            if self.js_count == 0:
                #print 'ok'
                self.x_change_color(self.x_start_c)
            if self.js_count == self.js_goal:
                #if self.reward_n == self.reward_t:
                self.x_change_color(self.x_stop_c)
                #else:
                self.reward.pumpOut()
                #self.yay_reward = True
                print joy_push.keys()
                self.js_count = 0
                self.t_delay = 0

        else:
            self.t_delay += 1

    def check_reward(self):
        # Runs every 200 ms
        # check to see if crosshair is in center, if so, stop it, give reward

        # move the crosshair, multiply by the multiplier to get the absolute value, essentially
        #print('neg=right', self.multiplier)
        old_pos = self.cross.getPos()[0]
        old_pos *= self.multiplier
        stop_x = self.multiplier * self.x_stop_p[0]

        #print('old', old_pos)
        #print('greater than', self.x_stop_p[0])
        if old_pos <= stop_x:
            self.yay_reward = True
        else:
            old_pos -= self.cross_move_int
            # go back to original direction
            old_pos *= self.multiplier
            new_pos = self.cross.getPos()
            new_pos[0] = old_pos
            #print('new', new_pos)
            self.cross.setPos(new_pos)

        # test joystick direction
        #test = self.js.getEvents()
        #if self.trainDir in test.keys():
        #    self.reward.pumpOut()

        # Runs every 200ms, same rate as pump rate
        # check to see if crosshair is in center, if so, stop it, give reward
        #if self.training == 0:
        #    self.check_js()
        #elif self.training == 1:
        # way it is currently configured, will "give reward" whenever paused
        if self.yay_reward:
            print 'reward'
            self.x_change_color(self.x_stop_c)
            # delay could also be number of reward beeps, if just want to wait for reward,
            # and then restart, or could be a combination of delay and beeps.
            if self.t_delay == self.delay:
                self.restart()
            else:
                self.t_delay += 1
                print self.t_delay
        #if self.trainDir in test.keys():
        #    self.reward.pumpOut()
        #    print 'reward'

        #if self.cross.getPos() == Point3(0, 0, 0):
        #    print 'reward'
        #    self.x_change_position(self.x_star_p)

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

    def give_reward(self, inputEvent):
        print('beep')
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
        self.x_start_p[0] *= 1.5
        if self.x_start_p[0] > 0.9:
            self.x_start_p[0] = 0.9
        print('new pos', self.x_start_p)

    def x_dec_start(self, inputEvent):
        self.x_start_p[0] *= 0.5
        if self.x_start_p[0] < 0:
            self.x_start_p = 0
        print('new pos', self.x_start_p)

    def inc_level(self, inputEvent):
        self.level += 1
        print('new level', self.level)

    def dec_level(self, inputEvent):
        self.level -= 1
        print('new level', self.level)

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
        self.x_change_position(self.x_start_p)
        self.x_change_color(self.x_start_c)
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
