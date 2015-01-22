# cringe #
from pandaepl.common import *
from panda3d.core import WindowProperties
from panda3d.core import TextNode
from load_models import PlaceModels, load_models
from fruit import Fruit
import datetime
import sys
# only load pydaq if it's available
try:
    sys.path.insert(1, '../pydaq')
    import pydaq
    LOADED_PYDAQ = True
    # print 'loaded PyDaq'
except ImportError:
    LOADED_PYDAQ = False
    print 'Not using PyDaq'


class GoBananas:
    def __init__(self):
        """
        Initialize the experiment
        """
        # Get experiment instance.
        # print 'init'
        exp = Experiment.getInstance()
        # exp.setSessionNum(0)
        # Set session to today's date and time
        exp.setSessionNum(datetime.datetime.now().strftime("%y_%m_%d_%H_%M"))
        print exp.getSessionNum()
        # I should go ahead and make config a class variable. Is in memory, because
        # it is a class variable in fruit, so doubling many variables here.
        self.config = Conf.getInstance().getConfig()  # Get configuration dictionary.
        print self.config['environ']
        # print config['training']
        # print 'load testing', config['testing']
        # bring some configuration parameters into memory, so we don't need to
        # reload the config file multiple times, also allows us to change these
        # variables dynamically
        # base.setFrameRateMeter(True)
        # Models must be attached to self
        self.env_models = []
        # num_beeps keeps track of reward for fruit we just ran into
        self.num_beeps = 0
        # in case we haven't set reward for different fruit, make reward same for all fruit
        reward_list = self.config.get('num_beeps', 3 * len(self.config['fruit']))
        if len(reward_list) == 1:
            reward_list = self.config['num_beeps'] * len(self.config['fruit'])
        elif len(self.config['fruit']) != len(reward_list):
            raise Exception("Fix the length of num_beeps!")
        self.beep_dict = dict(zip(self.config['fruit'], reward_list))
        self.config.setdefault('go_alpha', None)
        # print self.beep_dict
        # cross_hair gets changed, so go ahead and make a new variable
        self.cross_hair = self.config['crosshair']
        self.x_start_c = None
        self.x_stop_c = None
        if self.cross_hair:
            self.x_alpha = 1
        # get rid of cursor
        win_props = WindowProperties()
        # print win_props
        win_props.setCursorHidden(True)
        # win_props.setOrigin(20, 20)  # make it so windows aren't on top of each other
        # win_props.setSize(800, 600)  # normal panda window
        # base is global, used by pandaepl from panda3d
        # would be great to load this so it isn't just a global from nowhere,
        # but pandaepl makes it impossible
        base.win.requestProperties(win_props)
        # print base.win.requestProperties(win_props)
        # base.setFrameRateMeter(True)

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
        vr = Vr.getInstance()
        # vr.cTrav.showCollisions(render)

        # Register Custom Log Entries
        # This one corresponds to colliding with a banana
        Log.getInstance().addType("Yummy", [("Banana", basestring)],
                                  False)
        # Reward
        Log.getInstance().addType('Beeps', [('Reward', int)],
                                  False)
        # Done getting reward, banana disappears
        Log.getInstance().addType("Finished", [("Banana", basestring)],
                                  False)
        # New Trial
        Log.getInstance().addType("NewTrial", [("Trial", int)],
                                  False)
        # Aborted Trial
        Log.getInstance().addType("Aborted", ["Aborted"], True)
        # Eye data
        Log.getInstance().addType("EyeData",
                                  [("X", float), ("Y", float)],
                                  False)
        # If a trial is a repeat configuration
        Log.getInstance().addType("RepeatTrial", [("Repeat", int)],
                                  False)
        # log if a banana is alpha
        Log.getInstance().addType("Alpha", [("Alpha", basestring)],
                                  False)
        # initialize fruit_models
        self.fruit = None

        # initialize trial number
        self.trial_num = 0
        # Handle keyboard events
        vr.inputListen('close', self.close)
        vr.inputListen("increase_reward", self.increase_reward)
        vr.inputListen("decrease_reward", self.decrease_reward)
        vr.inputListen("increase_bananas", self.increase_bananas)
        vr.inputListen("decrease_bananas", self.decrease_bananas)
        vr.inputListen("override_alpha", self.override_alpha)
        vr.inputListen("extra_reward", self.extra_reward)
        vr.inputListen("restart", self.restart)
        # set up task to be performed between frames, checks at interval of pump
        vr.addTask(Task("check_reward",
                        lambda task_info:
                        self.check_reward(),
                        self.config['pulseInterval']))

        if self.config['go_alpha']:
            self.find_alpha = True
            vr.addTask(Task("check_alpha",
                            lambda task_info:
                            self.alpha_frame_loop()))

        # send avatar position to blackrock/plexon
        if self.config['sendData'] and LOADED_PYDAQ:
            vr.addTask(Task("sendAvatar",
                            lambda task_info:
                            self.avatar_frame_loop()))

        # set up reward system
        if self.config['reward'] and LOADED_PYDAQ:
            self.reward = pydaq.GiveReward()
        else:
            self.reward = None

        # start recording eye position
        if self.config['eyeData'] and LOADED_PYDAQ:
            # gain and offset can be changed in the program
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
            self.send_events = pydaq.OutputEvents()
            self.send_strobe = pydaq.StrobeEvents()
            # self.send_events = None
        else:
            self.send_pos_task = None
            self.send_events = None

    def alpha_frame_loop(self):
        # check to see if subject has found the alpha fruit yet this trial
        if self.find_alpha:
            #print 'find the alpha banana'
            dist_to_banana = self.fruit.check_distance_to_fruit(self.fruit.alpha_fruit)
            if dist_to_banana <= self.config.get('distance_goal', 1):
                # turn on banana to full
                #print 'change alpha'
                self.fruit.change_alpha_fruit('on', self.fruit.alpha_fruit)
                self.find_alpha = False

    def avatar_frame_loop(self):
        avatar = Avatar.getInstance()
        # max voltage is 5 volts. Kiril's courtyard is not actually square,
        # 10 in one direction, 11 in the other, so multiply avatar position by 0.4
        # to send voltage
        self.send_x_pos_task.send_signal(avatar.getPos()[0] * 0.2)
        self.send_y_pos_task.send_signal(avatar.getPos()[1] * 0.2)

    def check_reward(self):
        # Runs every 200ms
        # checks to see if we are giving reward (beeps is not None).
        # If we are, there was a collision, and avatar can't move and
        # banana hasn't disappeared yet.
        # After last reward, banana disappears and avatar can move.
        current_fruit = self.fruit.current_fruit
        if self.fruit.beeps is None:
            return
        elif self.fruit.beeps == 0:
            # just ran into it, log which banana
            VLQ.getInstance().writeLine("Yummy", [current_fruit])
            # log if alpha was turned on
            if self.fruit.fruit_models[current_fruit].retrNodePath().getTransparency():
                # print 'alpha'
                alpha = self.fruit.fruit_models[current_fruit].retrNodePath().getColorScale()[3]
                VLQ.getInstance().writeLine("Alpha", [current_fruit + ' ' + str(alpha)])
            # print('yummy', current_fruit)
            # print('banana pos', self.fruit.bananaModels[int(current_fruit[-2:])].getPos())
            if self.send_events:
                self.send_events.send_signal(200)
                self.send_strobe.send_signal()
            # determine how much reward we are giving
            self.num_beeps = self.get_reward_level(current_fruit)

        # Still here? Give reward!
        if self.reward:
            self.reward.pumpOut()
            # print('beep', self.fruit.beeps)
        else:
            print('beep', self.fruit.beeps)
        VLQ.getInstance().writeLine('Beeps', [int(self.fruit.beeps)])
        if self.send_events:
            self.send_events.send_signal(201)
            self.send_strobe.send_signal()
        # increment reward
        self.fruit.beeps += 1
        # If done, get rid of banana
        # print 'beeps', self.fruit.beeps
        # print 'extra', self.extra
        # print 'stashed', self.fruit.stashed
        if self.fruit.beeps == self.num_beeps:
            # banana disappears
            self.fruit.disappear_fruit()
            # if the list is empty, new trial
            if not self.fruit.fruit_list:
                self.trial_num += 1
                if self.config['go_alpha']:
                    self.find_alpha = True
                self.fruit.setup_gobananas_trial(self.trial_num)
                # logging for new trial
                self.log_new_trial()
            # avatar can move
            Avatar.getInstance().setMaxTurningSpeed(self.config['fullTurningSpeed'])
            Avatar.getInstance().setMaxForwardSpeed(self.config['fullForwardSpeed'])
            # reward is over
            self.fruit.beeps = None

    def get_reward_level(self, current_fruit):
        # current_fruit is going to have a number representation at the end to make it unique,
        # so don't use last three indices
        # print current_fruit
        # proof we can increase reward for alpha...
        # if self.fruit.fruit_models[current_fruit].retrNodePath().getTransparency():
            # print 'alpha'
        reward = self.beep_dict[current_fruit[:-3]]
        if len(self.fruit.fruit_list) == 1:
            # last fruit
            reward *= self.config['extra']
        return reward

    def get_eye_data(self, eye_data):
        # pydaq calls this function every time it calls back to get eye data
        VLQ.getInstance().writeLine("EyeData",
                                    [((eye_data[0] * self.gain[0]) - self.offset[0]),
                                     ((eye_data[1] * self.gain[1]) - self.offset[1])])

    def log_new_trial(self):
        # print('new trial', self.trial_num)
        if self.send_events:
            self.send_events.send_signal(1000 + self.trial_num)
            self.send_strobe.send_signal()
            for model in self.fruit.fruit_models.itervalues():
                # can't send negative numbers or decimals, so
                # need to translate the numbers
                translate_b = [int((model.getPos()[0] - self.config['min_x']) * 1000),
                               int((model.getPos()[1] - self.config['min_y']) * 1000)]
                self.send_events.send_signal(translate_b[0])
                self.send_strobe.send_signal()
                self.send_events.send_signal(translate_b[1])
                self.send_strobe.send_signal()
            if self.fruit.repeat:
                self.send_events.send_signal(300)
                self.send_strobe.send_signal()
                self.send_events.send_signal(self.fruit.repeat_list[2])
                self.send_strobe.send_signal()

    def load_environment(self, config):
        load_models()
        # print config['environ']
        for item in PlaceModels._registry:
            # print item.group
            # print item.name
            if config['environ'] in item.group:
                # print item.name
                item.model = config['path_models'] + item.model
                # print item.model
                model = Model(item.name, item.model, item.location)
                if item.callback is not None:
                    # print 'not none'
                    model.setCollisionCallback(eval(item.callback))
                    # white wall is bright, and sometimes hard to see bananas,
                    # quick fix.
                    # model.nodePath.setColor(0.8, 0.8, 0.8, 1.0)
                model.setScale(item.scale)
                model.setH(item.head)
                self.env_models.append(model)

        if self.cross_hair:
            # Cross hair
            # color changes for cross_hair
            # to get it to change color, will need to implement a ray
            self.x_start_c = Point4(1, 1, 1, self.x_alpha)
            self.x_stop_c = Point4(1, 0, 0, self.x_alpha)
            self.cross_hair = TextNode('cross_hair')
            self.cross_hair.setText('+')
            text_node_path = base.aspect2d.attachNewNode(self.cross_hair)
            text_node_path.setScale(0.2)
            # cross_hair is always in center, but
            # need it to be in same place as collisionRay is, but it appears that center is
            # at the bottom left of the collisionRay, and the top right of the text, so they
            # don't have center in the same place. Makes more sense to move text than ray.
            # These numbers were scientifically determined. JK, moved around until the cross looked
            # centered on the ray
            # cross_hair_pos = Point3(0, 0, 0)
            # cross_hair_pos = Point3(-0.07, 0, -0.05)
            cross_hair_pos = Point3(-0.055, 0, -0.03)

            # print text_node_path.getPos()
            text_node_path.setPos(cross_hair_pos)

    def increase_reward(self, input_event):
        # increase all rewards by one
        self.beep_dict = {key: value + 1 for key, value in self.beep_dict.items()}

    def decrease_reward(self, input_event):
        # decrease all rewards by one
        self.beep_dict = {key: value - 1 for key, value in self.beep_dict.items()}

    def increase_bananas(self, input_event):
        pass

    def decrease_bananas(self, input_event):
        pass

    def override_alpha(self, input_event):
        # make alpha banana brighter
        self.fruit.change_alpha_fruit('on', self.fruit.alpha_fruit)

    def restart(self, input_event):
        # print 'current trial aborted, new trial started'
        self.trial_num += 1
        self.fruit.setup_gobananas_trial(self.trial_num)

    def extra_reward(self, input_event):
        # print 'yup'
        if self.reward:
            self.reward.pumpOut()

    def start(self):
        """
        Start the experiment.
        """
        # print 'start'
        # load the environment
        config = Conf.getInstance().getConfig()  # Get configuration dictionary.
        self.load_environment(config)
        self.fruit = Fruit(config)
        all_fruit = config['fruit']
        num_fruit = config['num_fruit']
        if len(num_fruit) == 1:
            num_fruit = config['num_fruit'] * len(all_fruit)
            #print('new', num_fruit)
        num_fruit_dict = dict(zip(all_fruit, num_fruit))
        self.fruit.create_fruit(num_fruit_dict)
        self.fruit.setup_gobananas_trial(self.trial_num)
        self.log_new_trial()
        Experiment.getInstance().start()

    def close(self, input_event):
        if self.eye_task:
            self.eye_task.close()
        if self.send_events:
            self.send_events.close()
            self.send_strobe.close()
        if self.reward:
            self.reward.close()
        Experiment.getInstance().stop()

if __name__ == '__main__':
    GoBananas().start()
