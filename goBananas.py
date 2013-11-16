from direct.directbase.DirectStart import base
from pandaepl.common import *
#noinspection PyUnresolvedReferences
from panda3d.core import WindowProperties
from panda3d.core import CollisionNode, CollisionSphere
from create_environment import Environment
from create_bananas import Bananas
import datetime
import pydaq


class GoBananas:
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

        config = Conf.getInstance().getConfig()  # Get configuration dictionary.
        #print config['training']
        #print 'load testing', config['testing']
        # bring some configuration parameters into memory, so we don't need to
        # reload the config file multiple times, also allows us to change these
        # variables dynamically
        self.numBeeps = config['numBeeps']
        self.extra = config['extra']
        self.fullTurningSpeed = config['fullTurningSpeed']
        self.fullForwardSpeed = config['fullForwardSpeed']

        # get rid of cursor
        win_props = WindowProperties()
        #print win_props
        win_props.setCursorHidden(True)
        base.win.requestProperties(win_props)
        #print base.win.requestProperties(win_props)

        # set up reward system
        if config['reward']:
            self.reward = pydaq.GiveReward()
        else:
            self.reward = None

        # Get vr environment object
        vr = Vr.getInstance()
        #vr.cTrav.showCollisions(render)

        # not using experiment state currently
        #if not exp.getState():
            #bananas = []

        # Get avatar object
        #avatar = Avatar.getInstance()

        # Register Custom Log Entries
        #This one corresponds to colliding with a banana
        Log.getInstance().addType("YUMMY", [("BANANA", basestring)],
                                  False)
        Log.getInstance().addType("NewTrial", [("Trial", int)], False)
        # First Trial
        self.trial_num = 1
        VLQ.getInstance().writeLine("NewTrial", [self.trial_num])
        if config['eyeData']:
            Log.getInstance().addType("EyeData", [("X", float), ("Y", float)], False)
            self.gain = config['gain']
            self.offset = config['offset']

        # Load environment
        self.environ = Environment(config)
        self.banana_models = Bananas(config)

        # Handle keyboard events
        vr.inputListen('toggleDebug',
                       lambda inputEvent:
                       Vr.getInstance().setDebug(not Vr.getInstance().isDebug * ()))
        vr.inputListen("upTurnSpeed", self.upTurnSpeed)
        vr.inputListen("downTurnSpeed", self.downTurnSpeed)
        vr.inputListen("increaseBananas", self.banana_models.increaseBananas)
        vr.inputListen("decreaseBananas", self.banana_models.decreaseBananas)
        vr.inputListen("restart", self.restart)
        # set up task to be performed between frames
        vr.addTask(Task("checkReward",
                        lambda taskInfo:
                        self.check_reward(),
                        config['pulseInterval']))

        # start recording eye position
        if config['eyeData']:
            self.task = pydaq.EOGTask()
            self.task.StartTask()

    def check_reward(self):
        # Runs every flip of screen
        # checks to see if we are giving reward. If we are, there
        # was a collision, and avatar can't move and banana hasn't
        # disappeared yet.
        # After last reward, banana disappears and avatar can move.

        # print 'current beep', self.beeps

        if self.banana_models.beeps is None:
            return
        
        # Still here? Give reward!
        if self.reward:
            self.reward.pumpOut()
        else:
            print 'beep', self.banana_models.beeps
        # increment reward
        self.banana_models.beeps += 1
        
        # If done, get rid of banana
        #print 'beeps', self.banana_models.beeps
        #print 'extra', self.extra
        #print 'stashed', self.banana_models.stashed
        if self.banana_models.beeps == self.numBeeps:
            # check to see if we are doing double reward
            if self.banana_models.stashed == 1 and self.extra > 1:
                #print 'reset'
                self.banana_models.beeps = 0
                self.extra -= 1
            else:
                # banana disappears 
                self.trial_num = self.banana_models.goneBanana(self.trial_num)
                # avatar can move
                Avatar.getInstance().setMaxTurningSpeed(self.fullTurningSpeed)
                Avatar.getInstance().setMaxForwardSpeed(self.fullForwardSpeed)
                # reward is over
                self.banana_models.beeps = None

    def get_eye_data(self):
        eye_data = pydaq.EOGData
        Log.getInstance().writeLine("EyeData",
                                [((eye_data[0] * self.gain[0]) - self.offset[0]),
                                ((eye_data[1] * self.gain[1]) - self.offset[1])])

    def upTurnSpeed(self, inputEvent):
        avatar = Avatar.getInstance()
        self.fullTurningSpeed += 0.1
        if avatar.getMaxTurningSpeed() > 0:
            avatar.setMaxTurningSpeed(self.fullTurningSpeed)
        print("fullTurningSpeed: " + str(self.fullTurningSpeed))

    def downTurnSpeed(self, inputEvent):
        avatar = Avatar.getInstance()
        self.fullTurningSpeed -= 0.1
        if avatar.getMaxTurningSpeed() > 0:
            avatar.setMaxTurningSpeed(self.fullTurningSpeed)
        print("fullTurningSpeed: " + str(self.fullTurningSpeed))

    def restart(self, inputEvent):
        #print 'restarted'
        self.banana_models.replenishBananas()

    def start(self):
        """
        Start the experiment.
        """
        #print 'start'
        Experiment.getInstance().start()

if __name__ == '__main__':
    #print 'main?'
    GoBananas().start()
else:
    print 'not main?'
    #import argparse
    #p = argparse.ArgumentParser()
    #p.add_argument('-scrap')
    #import sys
    #sys.argv.extend(['stest'])
    #sys.argv = ['goBananas','-stest']
    #,'--no-eeg','--no-fs']
    GoBananas().start()
