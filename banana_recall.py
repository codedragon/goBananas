# cringe #
from pandaepl.common import *
from panda3d.core import WindowProperties
from panda3d.core import TextNode
from load_models import PlaceModels, load_models
from fruit import Fruit
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


def get_distance(p0, p1):
    """
    (tuple, tuple) -> float
    Returns the distance between 2 points. p0 is a tuple with (x, y)
    and p1 is a tuple with (x1, y1)
    :rtype : tuple
    """
    dist = sqrt((float(p0[0]) - float(p1[0])) ** 2 + (float(p0[1]) - float(p1[1])) ** 2)
    return dist


class BananaRecall:
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
        self.min_dist = [config['minXDistance'], config['minYDistance']]
        self.distance_goal = config['distance_goal']
        # toggle if got to fruit location
        self.remembered_location = False
        # variable to track if we are checking to see if the avatar is
        # in the position of the remembered banana (ie, time to look for remembered location)
        self.remember_fruit = False
        # get rid of cursor
        win_props = WindowProperties()
        #print win_props
        win_props.setCursorHidden(True)
        #win_props.setOrigin(20, 20)  # make it so windows aren't on top of each other
        #win_props.setSize(800, 600)  # normal panda window
        # base is global, used by pandaepl from panda3d
        # would be great to load this so it isn't just a global from nowhere,
        # but pandaepl makes it impossible
        base.win.requestProperties(win_props)

        # Get vr environment object
        vr = Vr.getInstance()
        #vr.cTrav.showCollisions(render)

        # not using experiment state currently
        #if not exp.getState():
            #bananas = []

        # Get avatar object
        #avatar = Avatar.getInstance()
        #collisionNode = avatar.retrNodePath().find('**/+CollisionNode')
        #collisionNode.show()
        #collisionNode.setTwoSided(True)

        # Register Custom Log Entries
        # This one corresponds to colliding with a fruit
        Log.getInstance().addType("Yummy", [("Fruit", basestring)],
                                  False)
        # Remembered where the banana was
        Log.getInstance().addType("Remembered", [("Distance", float)],
                                  False)
        # Reward
        Log.getInstance().addType('Beeps', [('Reward', int)],
                                  False)
        # Done getting reward, fruit disappears
        Log.getInstance().addType("Finished", [("Fruit", basestring)],
                                  False)
        # New Trial
        Log.getInstance().addType("NewTrial", [("Trial", int)],
                                  False)
        # Eye data
        Log.getInstance().addType("EyeData",
                                  [("X", float), ("Y", float)],
                                  False)
        self.fruit_models = None
        # initialize trial number
        self.trial_num = 0
        # Handle keyboard events
        vr.inputListen('toggleDebug',
                       lambda inputEvent:
                       Vr.getInstance().setDebug(not Vr.getInstance().isDebug * ()))
        vr.inputListen('close', self.close)
        vr.inputListen("increase_reward", self.increase_reward)
        vr.inputListen("decrease_reward", self.decrease_reward)
        vr.inputListen("extra_reward", self.extra_reward)
        vr.inputListen("restart", self.restart)
        vr.inputListen("NewTrial", self.new_trial)
        # set up task to be performed between frames, checks at interval of pump
        vr.addTask(Task("checkReward",
                        lambda taskInfo:
                        self.check_reward(),
                        config['pulseInterval']))
        vr.addTask(Task("rememberBanana",
                        lambda taskInfo:
                        self.check_position(),
                        ))
        # send avatar position to blackrock/plexon
        if config['sendData'] and LOADED_PYDAQ:
            vr.addTask(Task("sendAvatar",
                            lambda taskInfo:
                            self.check_avatar()))

        # set up reward system
        if config['reward'] and LOADED_PYDAQ:
            self.reward = pydaq.GiveReward()
        else:
            self.reward = None

        # start recording eye position
        if config['eyeData'] and LOADED_PYDAQ:
            self.gain = config['gain']
            self.offset = config['offset']
            self.eye_task = pydaq.EOGTask()
            self.eye_task.SetCallback(self.get_eye_data)
            self.eye_task.StartTask()
        else:
            self.eye_task = None

        # send digital signals to blackrock or plexon
        if config['sendData'] and LOADED_PYDAQ:
            self.send_x_pos_task = pydaq.OutputAvatarXPos()
            self.send_y_pos_task = pydaq.OutputAvatarYPos()
            self.send_events = pydaq.OutputEvents()
            self.send_strobe = pydaq.StrobeEvents()
            #self.send_events = None
        else:
            self.send_pos_task = None
            self.send_events = None

        # Log First Trial
        VLQ.getInstance().writeLine("NewTrial", [self.trial_num])
        #self.new_trial()

    def check_reward(self):
        # Runs every 200ms
        # checks to see if we are giving reward (beeps is not None).
        # If we are, there was a collision, and avatar can't move and
        # fruit hasn't disappeared yet.
        # After last reward, fruit disappears and avatar can move.

        # print 'current beep', self.beeps
        if self.fruit_models.beeps is None:
            return
        elif self.remembered_location:
            self.remember_fruit = False
            # is being rewarded for remembering the
            # correct location
            print 'remembered, new banana'
        elif self.fruit_models.beeps == 0:
            # just ran into fruit
            VLQ.getInstance().writeLine("Yummy", [self.fruit_models.got_fruit])
            #print('logged', self.fruit_models.byeBanana)
            #print('fruit pos', self.fruit_models.fruitModels[int(self.fruit_models.byeBanana[-2:])].getPos())
            if self.send_events:
                self.send_events.send_signal(200)
                self.send_strobe.send_signal()

        # Still here? Give reward!
        if self.reward:
            self.reward.pumpOut()
        else:
            print('beep', self.fruit_models.beeps)

        #print MovingObject.getCollisionIdentifier(Vr.getInstance())
        #vr = Vr.getInstance()
        #vr.cTrav.
        #for i in xrange(vr.cQueue.getNumEntries()):
        #    print Vr.getInstance().cQueue.getEntry(i)
        #collisionInfoList[0]
        #byeBanana = collisionInfoList[0].getInto().getIdentifier()
        VLQ.getInstance().writeLine('Beeps', [int(self.fruit_models.beeps)])
        if self.send_events:
            self.send_events.send_signal(201)
            self.send_strobe.send_signal()
        # increment reward
        self.fruit_models.beeps += 1

        # If done, get rid of fruit
        #print 'beeps', self.fruit_models.beeps
        #print 'extra', self.extra
        #print 'stashed', self.fruit_models.stashed
        if self.fruit_models.beeps == self.numBeeps:
            # fruit disappears
            old_trial = self.trial_num
            if self.remembered_location:
                self.new_trial()
                self.remember_fruit = False
            else:
                self.remember_fruit = self.fruit_models.gone_fruit(self.trial_num)
                print('remember_fruit', self.remember_fruit)
            self.remembered_location = False
            # new fruit appears, either starting over or next fruit in stack
            print 'new fruit'

            # avatar can move
            Avatar.getInstance().setMaxTurningSpeed(self.fullTurningSpeed)
            Avatar.getInstance().setMaxForwardSpeed(self.fullForwardSpeed)
            # reward is over
            self.fruit_models.beeps = None

    def check_position(self):
        if self.remember_fruit:
            avatar = Avatar.getInstance()
            avatar_pos = (avatar.getPos()[0], avatar.getPos()[1])
            banana = self.fruit_models.fruit_models[self.fruit_models.fruit_dict[self.fruit_models.fruit_to_remember]]
            banana_pos = (banana.getPos()[0], banana.getPos()[1])
            dist_to_banana = get_distance(avatar_pos, banana_pos)
            print dist_to_banana
            if dist_to_banana <= self.distance_goal:
                print 'found it!'
                VLQ.getInstance().writeLine("Remembered", [dist_to_banana])
                self.remembered_location = True
                self.fruit_models.beeps = 0

    def get_eye_data(self, eye_data):
        # pydaq calls this function every time it calls back to get eye data
        VLQ.getInstance().writeLine("EyeData",
                                [((eye_data[0] * self.gain[0]) - self.offset[0]),
                                ((eye_data[1] * self.gain[1]) - self.offset[1])])

    def check_avatar(self):
        avatar = Avatar.getInstance()
        # max voltage is 5 volts. Kiril's courtyard is not actually square,
        # 10 in one direction, 11 in the other, so multiply avatar position by 0.4
        # to send voltage
        self.send_x_pos_task.send_signal(avatar.getPos()[0] * 0.2)
        self.send_y_pos_task.send_signal(avatar.getPos()[1] * 0.2)

    def new_trial(self):
        # starting over again with a banana,
        # need to remember position of the banana
        self.trial_num += 1
        self.fruit_models.restart_fruit_sequence()
        print('new trial', self.trial_num)
        if self.send_events:
            self.send_events.send_signal(1000 + self.trial_num)
            self.send_strobe.send_signal()
            for i in self.fruit_models.fruitModels:
                # can't send negative numbers or decimals, so
                # need to translate the numbers
                #print i.getPos()
                translate_b = [int((i.getPos()[0] - self.min_dist[0]) * 1000),
                       int((i.getPos()[1] - self.min_dist[1]) * 1000)]
                #print foo
                self.send_events.send_signal(translate_b[0])
                self.send_strobe.send_signal()
                self.send_events.send_signal(translate_b[1])
                self.send_strobe.send_signal()
            if self.fruit_models.repeat:
                self.send_events.send_signal(300)
                self.send_strobe.send_signal()
                self.send_events.send_signal(self.fruit_models.now_repeat)
                self.send_strobe.send_signal()

    def load_environment(self, config):
        load_models()
        # Models must be attached to self
        self.envModels = []
        #print config['environ']
        for item in PlaceModels._registry:
            #print item.group
            #print item.name
            if config['environ'] in item.group:
            #if 'better' in item.group:
                #print item.name
                item.model = config['path_models'] + item.model
                #print item.model
                model = Model(item.name, item.model, item.location)
                if item.callback is not None:
                    #print 'not none'
                    model.setCollisionCallback(eval(item.callback))
                    # white wall is bright, and sometimes hard to see fruits,
                    # quick fix.
                    #model.nodePath.setColor(0.8, 0.8, 0.8, 1.0)
                model.setScale(item.scale)
                model.setH(item.head)
                self.envModels.append(model)

    def increase_reward(self, inputEvent):
        self.numBeeps += 1

    def decrease_reward(self, inputEvent):
        self.numBeeps -= 1

    def restart(self, inputEvent):
        #print 'restarted'
        self.fruit_models.replenish_stashed_fruit()

    def extra_reward(self, inputEvent):
        #print 'yup'
        if self.reward:
            self.reward.pumpOut()

    def start(self):
        """
        Start the experiment.
        """
        # Load environment
        config = Conf.getInstance().getConfig()  # Get configuration dictionary.
        self.load_environment(config)
        self.fruit_models = Fruit(config)
        print self.fruit_models
        # fruit to remember
        fruit_to_remember = config['fruit_to_remember']
        # fruit not remembering
        all_fruit = config['fruit']
        all_fruit.insert(0, fruit_to_remember)
        num_fruit = config['num_fruit']
        num_fruit.insert(0, 1)
        num_fruit_dict = dict(zip(all_fruit, num_fruit))
        self.fruit_models.create_fruit(num_fruit_dict)
        self.new_trial()
        #print 'start'
        Experiment.getInstance().start()

    def close(self, inputEvent):
        if self.eye_task:
            self.eye_task.StopTask()
            self.eye_task.ClearTask()
        Experiment.getInstance().stop()

if __name__ == '__main__':
    #print 'main?'
    BananaRecall().start()
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
