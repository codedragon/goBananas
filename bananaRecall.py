# cringe #
from pandaepl.common import *
from panda3d.core import WindowProperties
from load_models import PlaceModels, load_models
from fruit import Fruit
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
            #print('timer up')
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
        # raise an exception here, because config is probably wrong on several accounts
        # if fruit to remember is none when trying to run bananaRecall
        if self.config['fruit_to_remember'] is None:
            raise Exception("fruit_to_remember in config file must have a value")
        #print config['training']
        #print 'load testing', config['testing']
        # bring some configuration parameters into variables, so can change these
        # variables dynamically
        # list of all possible rewards
        self.beep_list = self.config['num_beeps']
        # how much reward for current fruit
        self.num_beeps = 0
        # toggle if got to fruit location, True means found fruit when wasn't visible,
        # False means was not looking for fruit
        # None means found fruit by collision (alpha was greater than 0)
        self.remembered_location = False
        # variable to track if we are checking to see if it is time for the avatar
        # to look for remembered location of fruit
        self.find_recall_fruit = False
        # variable to keep track of how long subject has to get to remembered fruit location
        self.recall_timer = 0
        # trigger fruit flashing
        self.flash_timer = 0
        # how long since last reward
        self.reward_timer = 0
        # variable to hold changes in alpha until new trial
        self.new_alpha = self.config['alpha']
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
        # log if a banana is alpha
        Log.getInstance().addType("Alpha", [("Alpha", basestring)],
                                  False)
        # Eye data
        Log.getInstance().addType("EyeData",
                                  [("X", float), ("Y", float)],
                                  False)
        self.fruit = None
        # initialize trial number, in bananaRecall, we are increasing the trial_num at the
        # beginning instead of the end, so start at -1, so trial_num starts at 0
        self.trial_num = -1
        # Handle keyboard events
        vr.inputListen('close', self.close)
        vr.inputListen("increase_reward", self.increase_reward)
        vr.inputListen("decrease_reward", self.decrease_reward)
        vr.inputListen("extra_reward", self.extra_reward)
        vr.inputListen("increase_alpha", self.change_alpha)
        vr.inputListen("decrease_alpha", self.change_alpha)
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
        # self.find_recall_fruit means there is no fruit present, so checking
        # distance to original (remembered) location
        if self.find_recall_fruit:
            dist_to_banana = self.fruit.check_distance_to_fruit(self.config['fruit_to_remember'])
            #print('dist to banana', dist_to_banana)
            if dist_to_banana <= self.config['distance_goal']:
                print 'found it!'
                self.found_banana(dist_to_banana)
            elif self.recall_timer:
                # check timer for looking for fruit
                if check_timer(self.recall_timer, self.config['time_to_recall']):
                    self.recall_timer = 0
                    # if time is up, no longer checking to see if close to fruit
                    self.find_recall_fruit = False
                    # if flashing fruit, go for it, otherwise start over
                    if self.config['time_to_flash']:
                        self.flash_fruit()
                    else:
                        print('time up')
                        self.new_trial()
        elif self.flash_timer:
            # if we flashed the fruit to show where it was, check to see if it
            # is time to turn it off.
            if check_timer(self.flash_timer, self.config['time_to_flash']):
                self.new_trial()
        # check to see if reward timer is on, otherwise safe to give reward
        if self.reward_timer and check_timer(self.reward_timer, self.config['pulseInterval']):
            self.reward_timer = 0
        if not self.reward_timer and self.fruit.beeps >= 0:
            # we can give reward, since there is currently no reward timer going
            self.give_reward()

    def give_reward(self):
        #print 'give reward'
        # set reward timer
        self.reward_timer = time.clock()
        if self.reward:
            print('beep', self.fruit.beeps)
            self.reward.pumpOut()
        else:
            print('beep', self.fruit.beeps)
        # if this is first reward, log that
        if self.fruit.beeps == 0:
            VLQ.getInstance().writeLine("Yummy", [self.fruit.current_fruit])
            #print('logged', self.fruit.byeBanana)
            #print('fruit pos', self.fruit.fruitModels[int(self.fruit.byeBanana[-2:])].getPos())
            if self.daq_events:
                self.daq_events.send_signal(200)
                self.daq_strobe.send_signal()
            # how many rewards are we giving? if fruit was not visible, but found it, bigger reward
            if self.remembered_location:
                #print 'remembered location, bonanza!'
                self.num_beeps = min(self.beep_list) * self.config['extra']
            elif len(self.fruit.fruit_list) == 1:
                # last fruit before remembering gets different reward
                # so knows next will be remembering
                self.num_beeps = max(self.beep_list)
            else:
                self.num_beeps = min(self.beep_list)
        # log which reward we are on
        VLQ.getInstance().writeLine('Beeps', [int(self.fruit.beeps)])
        if self.daq_events:
            self.daq_events.send_signal(201)
            self.daq_strobe.send_signal()
        # increment reward
        self.fruit.beeps += 1
        # if that was last reward
        if self.fruit.beeps == self.num_beeps:
            #print 'last reward'
            # if fruit visible, fruit disappears
            # new trial if we remembered where the fruit was or had an alpha fruit
            # if we didn't remember, we don't get reward, and never make it here
            # technically we could do if self.find_recall_fruit != False, but this
            # seems more intuitive.
            if self.remembered_location or self.find_recall_fruit is None:
                #print('either found alpha or remembered, new trial')
                # if alpha is not one, set banana back to full alpha
                if self.fruit.alpha > 0:
                    #print 'turn off alpha'
                    self.fruit.change_alpha_fruit('off')
                    self.fruit.reset_collision()
                self.new_trial()
                #print 'new trial'
                self.remembered_location = False
            else:
                #print 'did not have to remember location'
                self.fruit.disappear_fruit()
                self.find_recall_fruit = self.fruit.get_next_fruit()
                #print('remembered location again', self.remembered_location)
                # find_recall_fruit is true or false
                #print('find_recall_fruit', self.find_recall_fruit)
                # this will only matter if there is fruit to remember
                self.recall_timer = time.clock()
            #self.remembered_location = False
            # new fruit appears, either starting over or next fruit in stack
            #print 'new fruit appears'

            # avatar can move
            Avatar.getInstance().setMaxTurningSpeed(self.config['fullTurningSpeed'])
            Avatar.getInstance().setMaxForwardSpeed(self.config['fullForwardSpeed'])
            # reward is over
            self.fruit.beeps = None

    def found_banana(self, dist_to_banana):
        VLQ.getInstance().writeLine("Remembered", [dist_to_banana])
        # note this reward was due to remembering where fruit was
        self.remembered_location = True
        # no longer checking location
        self.find_recall_fruit = False
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
        for model in self.fruit.fruit_models.itervalues():
            # can't send negative numbers or decimals, so
            # need to translate the numbers
            # print i.getPos()
            translate_b = [int((model.getPos()[0] - self.config['min_x']) * 1000),
                           int((model.getPos()[1] - self.config['min_y']) * 1000)]
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
        print 'new trial'
        # starting over again with a possible new banana position,
        # make sure not still checking on old banana
        self.find_recall_fruit = False
        # get rid of recall fruit, if we flashed it up
        if self.flash_timer:
            self.fruit.change_alpha_fruit('off')
            self.flash_timer = 0
        self.trial_num += 1
        # can change alpha now
        print('alpha in recall', self.new_alpha)
        self.fruit.alpha = self.new_alpha
        self.fruit.setup_trial(self.trial_num)
        #print('new trial', self.trial_num)
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
        #print 'flash fruit'
        # flash where banana was, full alpha
        # turn on timer for flash
        self.fruit.change_alpha_fruit('on')
        self.flash_timer = time.clock()

    def increase_reward(self, inputEvent):
        self.beep_list = [x+1 for x in self.beep_list]

    def decrease_reward(self, inputEvent):
        self.beep_list = [x-1 for x in self.beep_list]

    def extra_reward(self, input_event):
        #print 'yup'
        if self.reward:
            self.reward.pumpOut()

    def toggle_random(self, input_event):
        # toggle random,
        self.fruit.repeat_recall = not self.fruit.repeat_recall
        # which is the opposite of repeat...
        print "Fruit is random:", not self.fruit.repeat_recall

    def change_alpha(self, input_event):
        # print('change alpha')
        print input_event.eventName
        if input_event.eventName == 'increase_alpha':
            self.new_alpha += 0.1
        else:
            self.new_alpha -= 0.1
        if self.new_alpha > 1:
            self.new_alpha = 1
        elif self.new_alpha < 0.1:
            self.new_alpha = 0
        print 'new alpha', self.new_alpha

    def change_subarea(self, input_event):
        print('change subarea')
        #print input_event
        print input_event.eventName
        #print input_event.eventName[-1]
        # create new corresponding dictionary
        self.fruit.create_fruit_area_dict(int(input_event.eventName[-1]))

    def start(self):
        """
        Start the experiment.
        """
        # Load environment
        self.load_environment()
        self.fruit = Fruit(self.config)
        #print self.fruit
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
