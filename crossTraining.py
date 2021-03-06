from direct.showbase.ShowBase import ShowBase
from joystick import JoystickHandler
from panda3d.core import Point3, TextNode, WindowProperties
from math import sqrt
import sys
PYDAQ_LOADED = True
try:
    sys.path.insert(1, '../pydaq')
    import pydaq
except ImportError:
    PYDAQ_LOADED = False
    print 'Not using PyDaq'


class CrossTraining(JoystickHandler):
    def __init__(self):
        self.base = ShowBase()
        config = {}
        execfile('cross_config.py', config)
        if not unittest:
            JoystickHandler.__init__(self)
        self.base.disableMouse()
        print('Subject is', config['subject'])
        # set up reward system
        if config['reward'] and PYDAQ_LOADED:
            self.reward = pydaq.GiveReward()
            print 'pydaq'
        else:
            self.reward = None
        self.frameTask = self.base.taskMgr.add(self.frame_loop, "frame_loop")
        if not unittest:
            wp = WindowProperties()
            wp.setSize(1280, 800)
            wp.setOrigin(0, 0)
            base.win.requestProperties(wp)
        self.crosshair = TextNode('crosshair')
        self.crosshair.setText('+')
        textNodePath = aspect2d.attachNewNode(self.crosshair)
        textNodePath.setScale(0.2)
        self.setup_inputs()
        # starting variables. "suppose" to be initiated here, which makes it silly
        # to then have them again, but kind of necessary to test. Making PyCharm happy ;-)
        self.x_mag = 0
        self.y_mag = 0
        # variables for counting how long to hold joystick
        self.js_count = 0
        # how much to push joystick before reward
        self.js_goal = config['goal']
        # (count increases before checking for goal match)
        # default is to reward for backward movement. May want
        # to make this a configuration option instead.
        # zero, all backward allowed
        # one, straight backward not rewarded
        # two, no backward rewarded
        self.backward = config['backward']
        self.forward = True
        self.right = True
        self.left = True
        # all kinds of start defaults
        self.delay_start = False
        self.reward_delay = False
        self.reward_time = config['pulseInterval']  # 200 ms
        self.reward_override = False
        self.reward_on = True
        self.current_dir = None
        self.frameTask.delay = 0

        print 'initialized'

    def frame_loop(self, task):
        # delay_start means we just gave reward and need to set wait time
        if self.delay_start:
            task.delay = task.time + self.reward_time
            #print('time now', task.time)
            #print('delay until', task.delay)
            self.delay_start = False
            #self.reward_delay = True
            return task.cont
        if task.time > task.delay:
            self.reward_on = True
            if self.backward > 0 or not self.forward:
                #print 'check y axis'
                # if we are not allowing a y dir, also need to check y dir.
                x_test = -0.1 < self.x_mag < 0.1
                #print x_test
                #print self.y_mag
                if self.backward == 1 and self.y_mag > 0 and x_test:
                    # don't allow straight back (within x tolerance)
                    self.reward_on = False
                    #print 'backward'
                    #print self.y_mag
                if self.backward == 2 and self.y_mag > 0.1:
                    print self.y_mag, self.x_mag
                    # don't allow any backward, but make the threshold higher
                    # this way movements to left or right that happen to be slightly
                    # backward still get rewarded, back small amount still nor rewarded,
                    # since we are under the threshold
                    self.reward_on = False
                if self.forward == 1 and self.y_mag < 0.1 and x_test:
                    # if going straight forward (within x tolerance)
                    self.reward_on = False
            if not self.left or not self.right:
                #print 'check x axis'
                # if we are not allowing an x dir, also need to check y dir.
                y_test = -0.1 < self.y_mag < 0.1
                #print y_test
                #print self.x_mag
                if not self.right and self.x_mag > 0 and y_test:
                    # don't allow straight right (within y tolerance)
                    self.reward_on = False
                    #print 'backward'
                    #print self.y_mag
                if not self.left and self.x_mag < 0.1 and y_test:
                    # if going straight left (within y tolerance)
                    self.reward_on = False

            #print dist
            if self.reward_on:
                dist = sqrt(self.x_mag**2 + self.y_mag**2)
                #print dist
                if dist > 0.1:
                    # eligible for reward. if not getting reward,
                    # need to turn on reward_delay so wait proper amount
                    #print 'ok for reward'
                    self.js_count += 1
                    if self.js_count != self.js_goal:
                        self.delay_start = True
                        self.reward_on = False
                        #print 'counts for reward'
                else:
                    #print 'no reward'
                    self.reward_on = False
                    self.js_count = 0
            # actual reward condition
            if self.reward_on or self.reward_override:
                #print 'reward'
                #print self.y_mag
                self.crosshair.setTextColor(1, 0, 0, 1)
                self.give_reward()
                self.js_count = 0
            else:
                self.crosshair.setTextColor(1, 1, 1, 1)
        return task.cont

    def give_reward(self):
        if self.reward:
            self.reward.pumpOut()
        print('beep')
        # must now wait for pump delay.
        self.delay_start = True

    def move(self, js_dir, js_input):
        print('move')
        print(js_dir, js_input)
        if js_dir == 'x':
            self.x_mag = js_input
        else:
            self.y_mag = js_input

    def start_reward(self):
        self.reward_override = True

    def stop_reward(self):
        self.reward_override = False

    def inc_js_goal(self):
        self.js_goal += 1
        print('new goal', self.js_goal)

    def dec_js_goal(self):
        self.js_goal -= 1
        if self.js_goal < 1:
            self.js_goal = 1
        print('new goal', self.js_goal)

    def allow_backward(self):
        self.backward += 1
        if self.backward > 2:
            self.backward = 0
        print('backward allowed:', self.backward)

    def allow_forward(self):
        self.forward = not self.forward
        print('forward allowed:', self.forward)

    def allow_left(self):
        self.left = not self.left
        print('left allowed:')

    def allow_right(self):
        self.right = not self.right
        print('right allowed:')

    def setup_inputs(self):
        self.accept('x_axis', self.move, ['x'])
        self.accept('y_axis', self.move, ['y'])
        self.accept('q', self.close)
        self.accept('e', self.inc_js_goal)
        self.accept('d', self.dec_js_goal)
        self.accept('b', self.allow_backward)
        self.accept('f', self.allow_forward)
        self.accept('r', self.allow_right)
        self.accept('l', self.allow_left)
        self.accept('space', self.start_reward)
        self.accept('space-up', self.stop_reward)

    def reset_variables(self):
        print('reset')
        # reset everything except stuff from config file
        self.x_mag = 0
        self.y_mag = 0
        # variables for counting how long to hold joystick
        self.js_count = 0
        # eventually may want start goal in config file
        # (count increases before checking for goal match)
        self.js_goal = 1  # start out just have to hit joystick
        # all kinds of start defaults
        self.delay_start = False
        self.reward_delay = False
        self.reward_override = False
        self.reward_on = True
        self.current_dir = None
        self.frameTask.delay = 0

    def close(self):
        sys.exit()

unittest = False
if __name__ == "__main__":
    CB = CrossTraining()
    run()
else:
    unittest = True