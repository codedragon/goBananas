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
    #print 'loaded'
except:
    pass


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
        self.fullTurningSpeed = config['fullTurningSpeed']
        self.fullForwardSpeed = config['fullForwardSpeed']
        if config['trainingDirection'] == 'Left':
            self.trainDir = 'turnLeft'
        elif config['trainingDirection'] == 'Right':
            self.trainDir = 'turnRight'
        elif config['trainingDirection'] == 'Forward':
            self.trainDir = 'moveForward'

        # get rid of cursor
        win_props = WindowProperties()
        #print win_props
        win_props.setCursorHidden(True)
        #win_props.setOrigin(20, 20)  # make it so windows aren't on top of each other
        #win_props.setSize(800, 600)  # normal panda window
        # base is global, used by pandaepl from panda3d
        base.win.requestProperties(win_props)
        #print base.win.requestProperties(win_props)

        # window2 = base.openWindow()
        # win_props.setOrigin(800, 200)  # make it so windows aren't on top of each other
        # win_props.setSize(800, 600)  # if no resolution given, assume normal panda window
        # window2.requestProperties(win_props)
        #
        # camera = base.camList[0]
        # camera.reparentTo(render)
        #
        # camera2 = base.camList[1]
        # camera.reparentTo(render)


        # Get vr environment object
        print Vr
        print Options
        options = Options.getInstance()
        print Joystick
        print options.__dict__.keys()
        print options.option_list
        print options.values
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
        #self.load_environment(config)

        #self.banana_models = Bananas(config)
        self.x_start_p = config['xStartPos']
        self.x_alpha = config['xHairAlpha']
        self.x_start_c = (1, 0, 0, self.x_alpha)
        self.cross = Text("cross", '+', Point3(self.x_start_p), config['instructSize'], Point4(self.x_start_c))
        #self.cross = Model("cross", "smiley", Point3(self.x_start_p))
        self.x_stop_p = (0, 0, 0)

        # Handle keyboard events
        vr.inputListen('toggleDebug',
                       lambda inputEvent:
                       Vr.getInstance().setDebug(not Vr.getInstance().isDebug * ()))
        vr.inputListen('close', self.close)
        vr.inputListen('space', self.reward.pumpOut)
        vr.inputListen("upTurnSpeed", self.upTurnSpeed)
        vr.inputListen("downTurnSpeed", self.downTurnSpeed)
        #vr.inputListen("increaseBananas", self.banana_models.increaseBananas)
        #vr.inputListen("decreaseBananas", self.banana_models.decreaseBananas)
        vr.inputListen("restart", self.restart)
        # set up task to be performed between frames
        vr.addTask(Task("checkReward",
                        lambda taskInfo:
                        self.check_reward(),
                        config['pulseInterval']))

        # set up reward system
        if config['reward']:
            self.reward = pydaq.GiveReward()
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

    def check_reward(self):
        # Runs every 200 ms
        # check to see if crosshair is in center, if so, stop it, give reward

        # move the crosshair
        old_pos = self.cross.getPos()
        old_pos[0] += 1
        self.cross.setPos(old_pos)
        test = self.js.getEvents()
        if test:
            print test.keys()

        if self.trainDir in test.keys():
            self.reward.pumpOut()
            print 'reward'

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

    def load_environment(self, config):
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
