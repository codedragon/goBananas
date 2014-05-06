from direct.showbase.ShowBase import ShowBase
from joystick import JoystickHandler
from panda3d.core import Point3, TextNode
from math import sqrt
import sys
PYDAQ_LOADED = True
try:
    sys.path.insert(1, '../pydaq')
    import pydaq
except ImportError:
    PYDAQ_LOADED = False
    print 'Not using PyDaq'


class CrossBanana(JoystickHandler):
    def __init__(self):
        self.base = ShowBase()
        config = {}
        execfile('cross_config.py', config)
        JoystickHandler.__init__(self)
        print('Subject is', config['subject'])
        # set up reward system
        if config['reward'] and PYDAQ_LOADED:
            self.reward = pydaq.GiveReward()
            print 'pydaq'
        else:
            self.reward = None
        self.frameTask = self.base.taskMgr.add(self.frame_loop, "frame_loop")
        self.setup_inputs()
        self.x_mag = 0
        self.y_mag = 0
        # variables for counting how long to hold joystick
        self.js_count = 0
        # eventually may want start goal in config file
        self.js_goal = 1  # start out just have to hit joystick
        # (count increases before checking for goal match)
        # default is to reward for backward movement. May want
        # to make this a configuration option instead.
        # zero, all backward allowed
        # one, straight backward not rewarded
        # two, no backward rewarded
        self.backward = config['backward']
        # all kinds of start defaults
        self.delay_start = False
        self.reward_delay = False
        self.reward_time = config['pulseInterval']  # 200 ms
        self.reward_override = False
        self.reward_on = True
        self.current_dir = None
        self.frameTask.delay = 0
        self.crosshair = TextNode('crosshair')
        self.crosshair.setText('+')
        textNodePath = aspect2d.attachNewNode(self.crosshair)
        textNodePath.setScale(0.2)
        print 'initialized'

    def frame_loop(self, task):
        #print task.time
        if self.delay_start:
            task.delay = task.time + self.reward_time
            #print('time now', task.time)
            #print('delay until', task.delay)
            self.delay_start = False
            #self.reward_delay = True
            return task.cont
        if task.time > task.delay:
            self.reward_on = True
            if self.backward > 0:
                #print 'check backward'
                # if we are not allowing backward, need to check y dir.
                # y_mag starts at exactly 0.0, but then zero becomes a slightly
                # negative number
                x_test = -0.2 < self.x_mag < 0.2
                #print x_test
                if self.y_mag == 0.0:
                    pass
                    #print 'nope'
                elif self.y_mag > -0.102:
                    #print 'check backward'
                    # 1 means only straight backward not rewarded, so if x is
                    if self.backward == 1 and x_test:
                        self.reward_on = False
                    elif self.backward == 2:
                        self.reward_on = False
                    #print 'backward'
                    #print self.y_mag

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

    def setup_inputs(self):
        self.accept('x_axis', self.move, ['x'])
        self.accept('y_axis', self.move, ['y'])
        self.accept('arrow_up', self.move, [2, 'up'])
        self.accept('arrow_down', self.move, [2, 'down'])
        self.accept('arrow_left', self.move, [2, 'left'])
        self.accept('arrow_right', self.move, [2, 'right'])
        self.accept('q', self.close)
        self.accept('e', self.inc_js_goal)
        self.accept('d', self.dec_js_goal)
        self.accept('b', self.allow_backward)
        self.accept('space', self.start_reward)
        self.accept('space-up', self.stop_reward)

    def close(self):
        sys.exit()

if __name__ == "__main__":
    CB = CrossBanana()
    run()