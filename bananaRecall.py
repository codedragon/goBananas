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
    # print 'loaded PyDaq'
except ImportError:
    pydaq = None
    LOADED_PYDAQ = False
    print 'Not using PyDaq'


def check_timer(timer, goal):
    # print goal
    # print('time elapsed', time.clock() - timer)
    if time.clock() - timer >= goal:
        # print 'goal', goal
        # print timer
        # print time.clock()
        # print('time up', time.clock() - timer)
        return True
    return False


class BananaRecall:
    def __init__(self):
        """
        Initialize the experiment
        """
        # Get experiment instance.
        # print 'init'

        exp = Experiment.getInstance()
        # Set session to today's date and time
        exp.setSessionNum(datetime.datetime.now().strftime("%y_%m_%d_%H_%M"))
        print exp.getSessionNum()
        self.config = Conf.getInstance().getConfig()  # Get configuration dictionary.
        # raise an exception here, because config is probably wrong on several accounts
        # if fruit to remember is none when trying to run bananaRecall
        if self.config['fruit_to_remember'] is None:
            raise Exception("fruit_to_remember in config file must have a value")
        # if on auto-pilot, make sure other configs make sense.
        if self.config['auto_pilot']:
            self.config['manual'] = False
            self.config['repeat_recall_fruit'] = False
            self.config['subarea'] = 10
        # print config['training']
        # print 'load testing', config['testing']
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
        self.new_alpha = None
        # variable to change distance goal for invisible recall fruit
        self.distance_goal = self.config['distance_goal'][1]
        # get rid of cursor
        # Models must be attached to self
        self.env_models = []
        win_props = WindowProperties()
        # print win_props
        win_props.setCursorHidden(True)
        # base is global, used by pandaepl from panda3d
        # would be great to load this so it isn't just a global from nowhere,
        # but pandaepl makes it impossible
        base.win.requestProperties(win_props)

        # Get vr environment object
        vr = Vr.getInstance()
        # vr.cTrav.showCollisions(render)

        # Get avatar object, seems I can't actually see the collision node, ever
        # avatar = Avatar.getInstance()
        # collisionNode = avatar.retrNodePath().find('**/+CollisionNode')
        # collisionNode.show()
        # collisionNode.setTwoSided(True)

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
        # Repeat Trial (only recall fruit is repeated)
        # If a trial is a repeat configuration
        Log.getInstance().addType("RepeatTrial", [("Repeat", int)],
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
        vr.inputListen("override_alpha", self.override_alpha)
        vr.inputListen("toggle_repeat", self.toggle_repeat)
        vr.inputListen("toggle_manual", self.toggle_manual)
        vr.inputListen("increase_dist_goal", self.change_goal)
        vr.inputListen("decrease_dist_goal", self.change_goal)
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

        vr.addTask(Task("frame_loop",
                        lambda task_info:
                        self.frame_loop(),
                        ))
        # send avatar position to blackrock/plexon
        if self.config['sendData'] and LOADED_PYDAQ:
            vr.addTask(Task("sendAvatar",
                            lambda task_info:
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
        # self.find_recall_fruit means it is time to remember the position of the
        # fruit. The recall fruit might be visible at low alpha, or invisible,
        # either way, becomes fully visible when within distance_goal
        if self.find_recall_fruit:
            if self.fruit.alpha > 0:
                recall_dist = self.config['distance_goal'][0]
            else:
                recall_dist = self.distance_goal
            dist_to_banana = self.fruit.check_distance_to_fruit(self.config['fruit_to_remember'])
            # print('dist to banana', dist_to_banana)
            if dist_to_banana <= recall_dist:
                # print dist_to_banana
                # print 'found it!'
                self.found_banana()
            elif self.recall_timer:
                # print 'check recall timer', self.config['time_to_recall']
                # check timer for looking for fruit
                if check_timer(self.recall_timer, self.config['time_to_recall']):
                    self.recall_timer = 0
                    # if time is up, no longer checking to see if close to fruit
                    self.find_recall_fruit = None
                    # if flashing fruit, go for it, otherwise start over
                    if self.config['time_to_flash']:
                        print('flash fruit')
                        self.flash_fruit()
                    else:
                        # when we time out, want to skip the banana, and go directly to
                        # cherries.
                        print('time up')
                        self.fruit.fruit_models[self.config['fruit_to_remember']].setStashed(True)
                        self.fruit.fruit_list.remove(self.config['fruit_to_remember'])
                        self.fruit.get_next_fruit()
        elif self.flash_timer:
            # if we flashed the fruit to show where it was, check to see if it
            # is time to turn it off.
            if check_timer(self.flash_timer, self.config['time_to_flash']):
                self.new_trial()
        # check to see if reward timer is on, otherwise safe to give reward
        if self.reward_timer and check_timer(self.reward_timer, self.config['pulseInterval'] / 1000.0):
            self.reward_timer = 0
        if not self.reward_timer and self.fruit.beeps >= 0:
            # we can give reward, since there is currently no reward timer going
            self.give_reward()

    def give_reward(self):
        # print 'give reward'
        # set reward timer
        self.reward_timer = time.clock()
        if self.reward:
            # print('beep', self.fruit.beeps)
            self.reward.pumpOut()
        else:
            print('beep', self.fruit.beeps)
        # if this is first reward, log that
        if self.fruit.beeps == 0:
            VLQ.getInstance().writeLine("Yummy", [self.fruit.current_fruit])
            # print('logged', self.fruit.byeBanana)
            # print('fruit pos', self.fruit.fruitModels[int(self.fruit.byeBanana[-2:])].getPos())
            if self.daq_events:
                self.daq_events.send_signal(200)
                self.daq_strobe.send_signal()
            # amount of reward can vary
            if self.fruit.current_fruit == self.fruit.config['fruit_to_remember'] and self.remembered_location:
                # extra reward
                # print self.fruit.current_fruit
                # print 'yes!'
                self.num_beeps = self.beep_list[0]
            else:
                # print self.beep_list[1]
                # print 'small reward'
                self.num_beeps = self.beep_list[1]
        # log which reward we are on
        VLQ.getInstance().writeLine('Beeps', [int(self.fruit.beeps)])
        if self.daq_events:
            self.daq_events.send_signal(201)
            self.daq_strobe.send_signal()
        # increment reward
        self.fruit.beeps += 1
        # if that was last reward
        if self.fruit.beeps == self.num_beeps:
            # reward is over
            # print 'reward over'
            self.fruit.beeps = None
            # if fruit visible, fruit disappears
            # new trial if we are out of fruit
            # or if we found recall fruit and are moving to location
            # for random, may want to check if this was an alpha or not?
            new_trial = False
            if self.find_recall_fruit is None:
                # print('either found alpha or remembered')
                # print('check to see if we are moving')
                self.fruit.change_alpha_fruit('off')
                self.remembered_location = False
                # after finding recall fruit, we may be re-starting,
                # if key press for new subarea or if not repeating
                if self.fruit.new_subarea_key or not self.fruit.repeat:
                    new_trial = True

            self.fruit.disappear_fruit()
            # avatar can move
            Avatar.getInstance().setMaxTurningSpeed(self.config['fullTurningSpeed'])
            Avatar.getInstance().setMaxForwardSpeed(self.config['fullForwardSpeed'])

            # new fruit appears, either starting over or next fruit in stack
            if not self.fruit.fruit_list or new_trial:
                self.new_trial()
            else:
                self.fruit.get_next_fruit()

    def found_banana(self):
        # VLQ.getInstance().writeLine("Remembered", [dist_to_banana])
        # change fruit alpha (make visible), and move so directly in front of avatar
        if self.fruit.alpha == 0:
            self.fruit.move_recall_fruit_to_avatar()
        self.fruit.change_alpha_fruit('on')
        self.remembered_location = True
        # no longer checking location
        self.find_recall_fruit = None

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
            self.daq_events.send_signal(translate_b[0])
            self.daq_strobe.send_signal()
            self.daq_events.send_signal(translate_b[1])
            self.daq_strobe.send_signal()

    def new_trial(self):
        # print self.fruit.fruit_area
        # print 'new trial'
        self.flash_timer = 0
        self.trial_num += 1
        # can change alpha now
        # print('alpha in recall', self.new_alpha)
        if self.new_alpha is not None:
            self.fruit.alpha = self.new_alpha
            self.new_alpha = None
        self.find_recall_fruit = self.fruit.start_recall_trial(self.trial_num)
        # print('time to remember', self.find_recall_fruit)
        if self.find_recall_fruit:
            # this will only matter if there is fruit to remember
            self.recall_timer = time.clock()
            # print 'set timer', self.recall_timer
        # print('new trial', self.trial_num)
        if self.daq_events:
            self.send_new_trial_daq()

    def load_environment(self):
        load_models()
        # print self.config['environ']
        for item in PlaceModels._registry:
            # print item.group
            # print item.name
            if self.config['environ'] in item.group:
                # print item.name
                item.model = self.config['path_models'] + item.model
                # print item.model
                model = Model(item.name, item.model, item.location)
                if item.callback is not None:
                    # print 'not none'
                    model.setCollisionCallback(eval(item.callback))

                model.setScale(item.scale)
                model.setH(item.head)
                self.env_models.append(model)

    def flash_fruit(self):
        # print 'flash fruit'
        # flash where banana was, full alpha
        # turn on timer for flash
        self.fruit.change_alpha_fruit('on')
        self.flash_timer = time.clock()

    def increase_reward(self, inputEvent):
        self.beep_list = [x+1 for x in self.beep_list]
        print('increase reward, now:', self.beep_list)

    def decrease_reward(self, inputEvent):
        self.beep_list = [x-1 for x in self.beep_list]
        print('decrease reward, now:', self.beep_list)

    def extra_reward(self, inputEvent=None):
        # print 'yup'
        if self.reward:
            self.reward.pumpOut()

    def toggle_repeat(self, input_event):
        # toggle repeat
        self.fruit.repeat = not self.fruit.repeat
        # which is the opposite of repeat...
        print "Fruit is repeat:", self.fruit.repeat

    def toggle_manual(self, input_event):
        # toggle manual
        self.fruit.manual = not self.fruit.manual
        # if we are manually choosing fruit, always repeat
        # until a new place is chosen.
        if self.fruit.manual:
            self.fruit.repeat = True
        print "Fruit is manual:", self.fruit.manual

    def change_alpha(self, input_event):
        # print('change alpha')
        print input_event.eventName
        # print self.new_alpha
        if self.new_alpha is None:
            # print 'get alpha', self.new_alpha
            self.new_alpha = self.fruit.alpha
        if input_event.eventName == 'increase_alpha':
            self.new_alpha += 0.05
        else:
            self.new_alpha -= 0.05
        if self.new_alpha > 1.0:
            self.new_alpha = 1.0
        elif self.new_alpha < 0.05:
            self.new_alpha = 0
        print 'new alpha', self.new_alpha

    def override_alpha(self, input_event):
        # make alpha banana brighter
        self.fruit.change_alpha_fruit('on')

    def change_goal(self, input_event):
        # print('change alpha')
        print input_event.eventName
        if input_event.eventName == 'increase_dist_goal':
            self.distance_goal += 0.5
        else:
            self.distance_goal -= 0.5
        if self.distance_goal < 0.5:
            self.distance_goal = 0
        print 'new distance goal', self.distance_goal

    def change_subarea(self, input_event):
        print('change subarea')
        # print input_event
        print input_event.eventName
        # print input_event.eventName[-1]
        # send this to fruit, to update position or subarea
        self.fruit.choose_recall_position(int(input_event.eventName[-1]))
        # print('banana', self.fruit.fruit_area)

    def start(self):
        """
        Start the experiment.
        """
        # Load environment
        self.load_environment()
        self.fruit = Fruit(self.config)
        # print self.fruit
        # fruit not remembering
        all_fruit = self.config['fruit']
        all_fruit.insert(0, self.config['fruit_to_remember'])
        num_fruit = self.config['num_fruit']
        num_fruit.insert(0, 1)
        num_fruit_dict = dict(zip(all_fruit, num_fruit))
        self.fruit.create_fruit(num_fruit_dict)
        self.new_trial()
        # print 'start'
        Experiment.getInstance().start()

    def close(self, inputEvent):
        if self.eye_task:
            self.eye_task.StopTask()
            self.eye_task.ClearTask()
        Experiment.getInstance().stop()

if __name__ == '__main__':
    BananaRecall().start()
