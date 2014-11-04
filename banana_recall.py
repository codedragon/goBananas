# cringe #
from pandaepl.common import *
from panda3d.core import WindowProperties
from panda3d.core import TextNode
from load_models import PlaceModels, load_models
from fruit import Fruit
from math import sqrt
from moBananas import get_distance
import datetime
import time
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


def check_timer(timer, goal):
        if time.clock() - timer >= goal:
            print('timer up')
            return True
        return False


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
        self.config = Conf.getInstance().getConfig()  # Get configuration dictionary.
        #print config['training']
        #print 'load testing', config['testing']
        # bring some configuration parameters into variables, so can change these
        # variables dynamically
        self.numBeeps = self.config['numBeeps']
        # toggle if got to fruit location
        self.remembered_location = False
        # variable to track if we are checking to see if the avatar is
        # in the position of the remembered banana (ie, time to look for remembered location)
        self.remember_fruit = False
        # variable to keep track of how long subject has to get to remembered fruit location
        self.recall_timer = 0
        # trigger fruit flashing
        self.flash_timer = 0
        # how long since last reward
        self.reward_timer = 0
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
        self.fruit = None
        # initialize trial number
        self.trial_num = 0
        # Handle keyboard events
        vr.inputListen('close', self.close)
        vr.inputListen("increase_reward", self.increase_reward)
        vr.inputListen("decrease_reward", self.decrease_reward)
        vr.inputListen("extra_reward", self.extra_reward)
        vr.inputListen("toggle_random", self.toggle_random)
        vr.inputListen("NewTrial", self.new_trial)
        vr.inputListen("subarea_1", self.change_subarea)
        vr.inputListen("subarea_2", self.change_subarea)
        vr.inputListen("subarea_3", self.change_subarea)
        vr.inputListen("subarea_4", self.change_subarea)
        vr.inputListen("subarea_5", self.change_subarea)
        vr.inputListen("subarea_6", self.change_subarea)
        vr.inputListen("subarea_7", self.change_subarea)
        vr.inputListen("subarea_8", self.change_subarea)
        vr.inputListen("subarea_9", self.change_subarea)
        vr.inputListen("subarea_0", self.change_subarea)

        # set up task to be performed between frames, checks at interval of pump
        #vr.addTask(Task("checkReward",
        #                lambda taskInfo:
        #                self.check_reward(),
        #                self.config['pulseInterval']))
        vr.addTask(Task("frame_loop",
                        lambda taskInfo:
                        self.frame_loop(),
                        ))
        # send avatar position to blackrock/plexon
        if self.config['sendData'] and LOADED_PYDAQ:
            vr.addTask(Task("sendAvatar",
                            lambda taskInfo:
                            self.send_avatar_daq()))

        # set up reward system
        if self.config['reward'] and LOADED_PYDAQ:
            self.reward = pydaq.GiveReward()
        else:
            self.reward = None

        # start recording eye position
        if self.config['eyeData'] and LOADED_PYDAQ:
            self.gain = self.config['gain']
            self.offset = self.config['offset']
            self.eye_task = pydaq.EOGTask()
            self.eye_task.SetCallback(self.get_eye_data)
            self.eye_task.StartTask()
        else:
            self.eye_task = None

        # send digital signals to blackrock or plexon
        if self.config['sendData'] and LOADED_PYDAQ:
            self.send_x_pos_task = pydaq.OutputAvatarXPos()
            self.send_y_pos_task = pydaq.OutputAvatarYPos()
            self.daq_events = pydaq.OutputEvents()
            self.daq_strobe = pydaq.StrobeEvents()
        else:
            self.daq_events = None

    def frame_loop(self):
        # self.remember_fruit means there is an 'invisible' fruit present,
        # that we will not be colliding into, so check distance
        if self.remember_fruit:
            if self.fruit.alpha > 0:
                print 'show fruit at alpha'
                # if fruit is partially visible, will use callback instead of distance,
                # but need to set that this was a remembered trial, so we start over after
                self.remembered_location = True
                self.remember_fruit = False
            dist_to_banana = self.check_distance_to_fruit()
            #print('dist to banana', dist_to_banana)
            if dist_to_banana <= self.config['distance_goal']:
                print 'found it!'
                self.found_banana(dist_to_banana)
            elif self.recall_timer:
                # check timer for looking for fruit
                if check_timer(self.recall_timer, self.config['time_to_recall']):
                    self.recall_timer = 0
                    # if time is up, no longer checking to see if close to fruit
                    self.remember_fruit = False
                    # if flashing fruit, go for it, otherwise start over
                    if self.config['time_to_flash']:
                        self.flash_fruit()
                    else:
                        self.new_trial()
        elif self.flash_timer:
            # if we flashed the fruit to show where it was, check to see if it
            # is time to turn it off.
            if check_timer(self.flash_timer, self.config['time_to_flash']):
                self.new_trial()
        # check to see if reward timer is on, otherwise safe to give reward
        if self.reward_timer:
            if check_timer(self.reward_timer, self.config['pulseInterval']):
                self.reward_timer = 0
        elif self.fruit.beeps >= 0:
            # we can give reward, since there is currently no reward timer going
            self.give_reward()

    def give_reward(self):
        print 'give reward'
        if self.reward:
            self.reward.pumpOut()
        else:
            print('beep', self.fruit.beeps)
        # now set reward timer
        self.reward_timer = time.clock()
        # if this is first reward, log that
        if self.fruit.beeps == 0:
            VLQ.getInstance().writeLine("Yummy", [self.fruit.current_fruit])
            #print('logged', self.fruit.byeBanana)
            #print('fruit pos', self.fruit.fruitModels[int(self.fruit.byeBanana[-2:])].getPos())
            if self.daq_events:
                self.daq_events.send_signal(200)
                self.daq_strobe.send_signal()
        # log which reward we are on
        VLQ.getInstance().writeLine('Beeps', [int(self.fruit.beeps)])
        if self.daq_events:
            self.daq_events.send_signal(201)
            self.daq_strobe.send_signal()
        # increment reward
        self.fruit.beeps += 1
        # if that was last reward
        if self.fruit.beeps == self.numBeeps:
            print 'last reward'
            # if fruit visible, fruit disappears, otherwise new trial
            if self.remembered_location:
                # if alpha is not one, set banana back to full alpha
                if self.fruit.alpha > 0:
                    print 'turn off alpha'
                    self.fruit.flash_recall_fruit(False)
                    self.fruit.reset_collision()
                self.new_trial()
            else:
                self.fruit.disappear_fruit()
                self.remember_fruit = self.fruit.get_next_fruit()
                # remember_fruit is true or false
                print('remember_fruit', self.remember_fruit)
                # this will only matter if there is fruit to remember
                self.recall_timer = time.clock()
            self.remembered_location = False
            # new fruit appears, either starting over or next fruit in stack
            print 'new fruit'

            # avatar can move
            Avatar.getInstance().setMaxTurningSpeed(self.config['fullTurningSpeed'])
            Avatar.getInstance().setMaxForwardSpeed(self.config['fullForwardSpeed'])
            # reward is over
            self.fruit.beeps = None

    def check_distance_to_fruit(self):
        avatar = Avatar.getInstance()
        avatar_pos = (avatar.getPos()[0], avatar.getPos()[1])
        banana = self.fruit.fruit_models[self.fruit.index_fruit_dict[self.config['fruit_to_remember']]]
        banana_pos = (banana.getPos()[0], banana.getPos()[1])
        dist_to_banana = get_distance(avatar_pos, banana_pos)
        return dist_to_banana

    def found_banana(self, dist_to_banana):
        VLQ.getInstance().writeLine("Remembered", [dist_to_banana])
        # note this reward was due to remembering where fruit was
        self.remembered_location = True
        # no longer checking location
        self.remember_fruit = False
        # start giving reward
        self.fruit.beeps = 0

    def get_eye_data(self, eye_data):
        # pydaq calls this function every time it calls back to get eye data
        VLQ.getInstance().writeLine("EyeData",
                                    [((eye_data[0] * self.gain[0]) - self.offset[0]),
                                    ((eye_data[1] * self.gain[1]) - self.offset[1])])

    def send_avatar_daq(self):
        avatar = Avatar.getInstance()
        # max voltage is 5 volts. Kiril's courtyard is not actually square,
        # 10 in one direction, 11 in the other, so multiply avatar position by 0.4
        # to send voltage
        self.send_x_pos_task.send_signal(avatar.getPos()[0] * 0.2)
        self.send_y_pos_task.send_signal(avatar.getPos()[1] * 0.2)

    def send_new_trial_daq(self):
        self.daq_events.send_signal(1000 + self.trial_num)
        self.daq_strobe.send_signal()
        for i in self.fruit.fruitModels:
            # can't send negative numbers or decimals, so
            # need to translate the numbers
            # print i.getPos()
            translate_b = [int((i.getPos()[0] - self.config['minXDistance']) * 1000),
                           int((i.getPos()[1] - self.config['minYDistance']) * 1000)]
            #print foo
            self.daq_events.send_signal(translate_b[0])
            self.daq_strobe.send_signal()
            self.daq_events.send_signal(translate_b[1])
            self.daq_strobe.send_signal()
        if self.fruit.repeat:
            self.daq_events.send_signal(300)
            self.daq_strobe.send_signal()
            self.daq_events.send_signal(self.fruit.now_repeat)
            self.daq_strobe.send_signal()

    def new_trial(self):
        # starting over again with a new banana position,
        # make sure not still checking on old banana
        self.remember_fruit = False
        # stop flash, if flashing
        if self.flash_timer:
            self.fruit.flash_recall_fruit(False)
            self.flash_timer = 0
        self.trial_num += 1
        self.fruit.setup_trial(self.trial_num)
        print('new trial', self.trial_num)
        if self.daq_events:
            self.send_new_trial_daq()

    def load_environment(self):
        load_models()
        # Models must be attached to self
        self.envModels = []
        #print self.config['environ']
        for item in PlaceModels._registry:
            #print item.group
            #print item.name
            if self.config['environ'] in item.group:
            #if 'better' in item.group:
                #print item.name
                item.model = self.config['path_models'] + item.model
                #print item.model
                model = Model(item.name, item.model, item.location)
                if item.callback is not None:
                    #print 'not none'
                    model.setCollisionCallback(eval(item.callback))

                model.setScale(item.scale)
                model.setH(item.head)
                self.envModels.append(model)

    def flash_fruit(self):
        print 'flash fruit'
        # flash where banana was, turn on timer for flash
        self.fruit.flash_recall_fruit(True)
        self.flash_timer = time.clock()

    def increase_reward(self, input_event):
        self.numBeeps += 1

    def decrease_reward(self, input_event):
        self.numBeeps -= 1

    def extra_reward(self, input_event):
        #print 'yup'
        if self.reward:
            self.reward.pumpOut()

    def toggle_random(self, input_event):
        # toggle random
        self.fruit.repeat_recall = not self.fruit.repeat_recall

    def change_subarea(self, input_event):
        print('change subarea')
        print input_event
        print input_event.eventName
        print input_event.eventName[-1]
        # get rid of old location, since setting new one
        self.fruit.pos_list = []
        self.fruit.create_subarea_dict(int(input_event.eventName[-1]))

    def start(self):
        """
        Start the experiment.
        """
        # Load environment
        self.load_environment()
        self.fruit = Fruit(self.config)
        print self.fruit
        # fruit not remembering
        all_fruit = self.config['fruit']
        all_fruit.insert(0, self.config['fruit_to_remember'])
        num_fruit = self.config['num_fruit']
        num_fruit.insert(0, 1)
        num_fruit_dict = dict(zip(all_fruit, num_fruit))
        self.fruit.create_fruit(num_fruit_dict)
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
