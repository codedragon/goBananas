# cringe #
from pandaepl.common import *
from panda3d.core import WindowProperties
from panda3d.core import TextNode
from load_models import PlaceModels, load_models
from fruit import Fruit
#from bananas import Bananas
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
        print exp.getSessionNum()
        config = Conf.getInstance().getConfig()  # Get configuration dictionary.
        #print config['training']
        #print 'load testing', config['testing']
        # bring some configuration parameters into memory, so we don't need to
        # reload the config file multiple times, also allows us to change these
        # variables dynamically
        #base.setFrameRateMeter(True)
        # extra is factor to multiply reward by for last fruit
        self.extra = config['extra']
        # num_beeps keeps track of reward for fruit we just ran into
        self.num_beeps = 0
        # in case we haven't set reward for different fruit, make reward same for all fruit
        reward_list = config.get('num_beeps', 3 * len(config['fruit']))
        self.beep_dict = dict(zip(config['fruit'], reward_list))
        # extra_flag is true if extra is not 1
        #self.extra_flag = self.extra[0] > self.numBeeps
        self.full_turn_speed = config['fullTurningSpeed']
        self.full_forward_speed = config['fullForwardSpeed']
        self.min_x = config['min_x']
        self.min_y = config['min_y']
        # self.weighted_bananas = config['weightedBananas']
        self.crosshair = config['crosshair']
        if self.crosshair:
            self.x_alpha = 1
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
        #print base.win.requestProperties(win_props)
        #base.setFrameRateMeter(True)

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
        # Aborted Trial
        Log.getInstance().addType("Aborted", ["Aborted"], True)
        # Eye data
        Log.getInstance().addType("EyeData",
                                  [("X", float), ("Y", float)],
                                  False)
        # If a trial is a repeat configuration
        Log.getInstance().addType("RepeatTrial", [("Repeat", int)],
                                  False)

        # initialize fruit_models
        self.fruit = None

        # initialize trial number
        self.trial_num = 0
        # Handle keyboard events
        vr.inputListen('toggleDebug',
                       lambda inputEvent:
                       Vr.getInstance().setDebug(not Vr.getInstance().isDebug * ()))
        vr.inputListen('close', self.close)
        vr.inputListen("increase_reward", self.increase_reward)
        vr.inputListen("decrease_reward", self.decrease_reward)
        vr.inputListen("increaseBananas", self.increase_bananas)
        vr.inputListen("decreaseBananas", self.decrease_bananas)
        vr.inputListen("extra_reward", self.extra_reward)
        vr.inputListen("restart", self.restart)
        # set up task to be performed between frames, checks at interval of pump
        vr.addTask(Task("checkReward",
                        lambda taskInfo:
                        self.check_reward(),
                        config['pulseInterval']))
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

    def check_reward(self):
        # Runs every 200ms
        # checks to see if we are giving reward (beeps is not None).
        # If we are, there was a collision, and avatar can't move and
        # banana hasn't disappeared yet.
        # After last reward, banana disappears and avatar can move.

        if self.fruit.beeps is None:
            return
        elif self.fruit.beeps == 0:
            # just ran into it?
            VLQ.getInstance().writeLine("Yummy", [self.fruit.current_fruit])
            print('yummy', self.fruit.current_fruit)
            #print('banana pos', self.fruit.bananaModels[int(self.fruit.current_fruit[-2:])].getPos())
            if self.send_events:
                self.send_events.send_signal(200)
                self.send_strobe.send_signal()
            # determine how much reward we are giving
            self.num_beeps = self.get_reward_level(self.fruit.current_fruit)

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
        #print 'beeps', self.fruit.beeps
        #print 'extra', self.extra
        #print 'stashed', self.fruit.stashed
        if self.fruit.beeps == self.num_beeps:
            # banana disappears
            self.fruit.disappear_fruit()
            # if the list is empty, new trial
            if not self.fruit.fruit_list:
                self.trial_num += 1
                self.fruit.setup_trial(self.trial_num)
                # logging for new trial
                self.log_new_trial()
            # avatar can move
            Avatar.getInstance().setMaxTurningSpeed(self.full_turn_speed)
            Avatar.getInstance().setMaxForwardSpeed(self.full_forward_speed)
            # reward is over
            self.fruit.beeps = None

    def get_reward_level(self, current_fruit):
        # current_fruit is going to have a number representation at the end to make it unique,
        # so don't use last three indices
        print current_fruit
        reward = self.beep_dict[current_fruit[:-3]]
        if len(self.fruit.fruit_list) == 1:
            # last fruit
            reward *= self.extra
        return reward

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

    def log_new_trial(self):
        #print('new trial', self.trial_num)
        if self.send_events:
            self.send_events.send_signal(1000 + self.trial_num)
            self.send_strobe.send_signal()
            for model in self.fruit.fruit_models.itervalues():
                # can't send negative numbers or decimals, so
                # need to translate the numbers
                #print i.getPos()
                translate_b = [int((model.getPos()[0] - self.min_x) * 1000),
                       int((model.getPos()[1] - self.min_y) * 1000)]
                #print foo
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
                    # white wall is bright, and sometimes hard to see bananas,
                    # quick fix.
                    #model.nodePath.setColor(0.8, 0.8, 0.8, 1.0)
                model.setScale(item.scale)
                model.setH(item.head)
                self.envModels.append(model)

        if self.crosshair:
            # Cross hair
            # color changes for crosshair
            self.x_start_c = Point4(1, 1, 1, self.x_alpha)
            self.x_stop_c = Point4(1, 0, 0, self.x_alpha)
            self.crosshair = TextNode('crosshair')
            self.crosshair.setText('+')
            text_node_path = base.aspect2d.attachNewNode(self.crosshair)
            text_node_path.setScale(0.2)
            # crosshair is always in center, but
            # need it to be in same place as collisionRay is, but it appears that center is
            # at the bottom left of the collisionRay, and the top right of the text, so they
            # don't have center in the same place. Makes more sense to move text than ray.
            # These numbers were scientifically determined. JK, moved around until the cross looked
            # centered on the ray
            #crosshair_pos = Point3(0, 0, 0)
            #crosshair_pos = Point3(-0.07, 0, -0.05)
            crosshair_pos = Point3(-0.055, 0, -0.03)

            #print text_node_path.getPos()
            text_node_path.setPos(crosshair_pos)

    def increase_reward(self, inputEvent):
        self.numBeeps += 1

    def decrease_reward(self, inputEvent):
        self.numBeeps -= 1

    def increase_bananas(self, inputEvent):
        pass

    def decrease_bananas(self, inputEvent):
        pass

    def restart(self, inputEvent):
        #print 'current trial aborted, new trial started'
        self.trial_num += 1
        self.fruit.setup_trial(self.trial_num)

    def extra_reward(self, inputEvent):
        #print 'yup'
        if self.reward:
            self.reward.pumpOut()

    def start(self):
        """
        Start the experiment.
        """
        #print 'start'
        # load the environment
        config = Conf.getInstance().getConfig()  # Get configuration dictionary.
        self.load_environment(config)
        self.fruit = Fruit(config)
        all_fruit = config['fruit']
        num_fruit = config['num_fruit']
        num_fruit_dict = dict(zip(all_fruit, num_fruit))
        self.fruit.create_fruit(num_fruit_dict)
        self.fruit.setup_trial(self.trial_num)
        self.log_new_trial()
        Experiment.getInstance().start()

    def close(self, inputEvent):
        if self.eye_task:
            self.eye_task.close()
        if self.send_events:
            self.send_events.close()
            self.send_strobe.close()
        if self.reward:
            self.reward.close()
        Experiment.getInstance().stop()

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
    #GoBananas().start()
