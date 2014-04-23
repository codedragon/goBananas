from direct.showbase.ShowBase import ShowBase
from  joystick import JoystickHandler
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
        JoystickHandler.__init__(self)
        config = {}
        execfile('testing_config.py', config)
        print('Subject is', config['subject'])
        # set up reward system
        if config['reward'] and PYDAQ_LOADED:
            self.reward = pydaq.GiveReward()
            print 'pydaq'
        else:
            self.reward = None
        self.frameTask = self.base.taskMgr.add(self.frame_loop, "frame_loop")
        self.setup_inputs()
        self.set_variables()

    def set_variables(self):
        # best to have stuff here that we want to be able to re-initialize if need be.
        # sort of silly to reload the config file, but no need to keep it in memory,
        # so might as well.
        config = {}
        execfile('testing_config.py', config)
        self.training = config['training']
        if self.training == 0:
            self.x_start_p = Point3(0, 0, 0)
        else:
            self.cross_pos = config['xStartPos']
        self.cross_move = config['xHairDist']
        # variables for counting how long to hold joystick
        self.js_count = 0
        # eventually may want start goal in config file
        self.js_goal = 1  # start out just have to hit joystick
        # (count increases before checking for goal match)
        # default is to reward for backward movement. May want
        # to make this a configuration option instead.
        self.backward = True
        #self.delay = 0  # keeps track of updates waiting for new "trial"
        #self.t_delay = 0  # number of updates to wait for new "trial" (200ms per update)
        self.poll_js = True  # start with no delays
        self.yay_reward = False
        self.frameTask.delay = 0
        print 'initialized'

    def frame_loop(self, task):
        if task.time > task.delay:
            self.poll_js = True
        else:
            self.poll_js = False
        return task.cont

    def check_js(self, direction):
        # not moving crosshair, just push joystick to get reward,
        # longer and longer intervals
        # delay determines how long before cross re-appears
        #print 'in check_js'
        self.yay_reward = False
        js_good = False
        if self.backward:
            # if rewarding for backward, then pushing joystick
            # always get reward
            js_good = True
        elif direction != 'backward':
            # if not rewarding for backward, check to see if
            # backward was pushed before rewarding
            js_good = True
        if js_good:
            print 'counts for reward'
            self.js_count += 1
            if self.js_count == self.js_goal:
                print('reward')
                #self.x_change_color(self.x_stop_c)
                self.yay_reward = True
                self.give_reward()
                #print('touched for', self.js_count)
                self.js_count = 0
                self.delay = 0
        elif self.js_count >= 0:
            #print 'start over'
            #self.x_change_color(self.x_start_c)
            self.js_count = 0

    def give_reward(self):
        print('beep')
        if self.reward:
            self.reward.pumpOut()

    def go_left(self, js_input):
        direction = 'left'
        print direction
        print js_input
        self.check_js(direction)

    def go_right(self, js_input):
        direction = 'right'
        print direction
        print js_input
        self.check_js(direction)

    def go_forward(self, js_input):
        direction = 'forward'
        print direction
        print js_input
        self.check_js(direction)

    def go_backward(self, js_input):
        direction = 'backward'
        print direction
        print js_input
        self.check_js(direction)

    def let_go(self, js_input):
        self.js_count = 0

    def pause(self, inputEvent):
        # if we are less than the usual delay (so in delay or delay is over),
        # make it a giant delay,
        # otherwise end the delay period.
        if self.t_delay < self.delay:
            self.t_delay = 1000000
        else:
            self.t_delay = 0

    def inc_x_start(self, inputEvent):
        self.x_start_p[0] *= 1.5
        if abs(self.x_start_p[0]) > 0.9:
            self.x_start_p[0] = self.multiplier * 0.9
        print('new pos', self.x_start_p)

    def dec_x_start(self, inputEvent):
        self.x_start_p[0] *= 0.5
        # don't go too crazy getting infinitely close to zero. :)
        if self.x_start_p[0] < 0.01:
            self.x_start_p[0] = 0.01
        print('new pos', self.x_start_p)

    def inc_level(self, inputEvent):
        self.change_level = self.training + 1
        print('new level', self.change_level)

    def dec_level(self, inputEvent):
        self.change_level = self.training - 1
        if self.change_level < 0:
            self.change_level = 0
        print('new level', self.change_level)

    def inc_js_goal(self, inputEvent=None):
        self.js_goal += 1
        print('new goal', self.js_goal)

    def dec_js_goal(self, inputEvent=None):
        self.js_goal -= 1
        print('new goal', self.js_goal)

    def inc_interval(self, inputEvent):
        self.delay += 1
        print('new delay', self.delay)

    def dec_interval(self, inputEvent):
        self.delay -= 1
        print('new delay', self.delay)

    def change_left(self, inputEvent):
        self.new_dir = 1
        print('new dir: left')

    def change_right(self, inputEvent):
        self.new_dir = -1
        print('new dir: right')

    def change_forward(self, inputEvent):
        self.new_dir = 0
        print('new dir: forward')

    def allow_backward(self, inputEvent):
        self.backward = not self.backward
        print('backward allowed:', self.backward)

    def setup_inputs(self):
        self.accept('js_up', self.go_forward, )
        self.accept('js_down', self.go_backward)
        self.accept('js_left', self.go_left)
        self.accept('js_right', self.go_right)
        self.accept('let_go', self.let_go)
        self.accept('arrow_up', self.go_forward, [2])
        self.accept('arrow_down', self.go_backward, [2])
        self.accept('arrow_left', self.go_left, [2])
        self.accept('arrow_right', self.go_right, [2])
        self.accept('q', self.close)
        self.accept('w', self.inc_x_start)
        self.accept('s', self.dec_x_start)
        self.accept('e', self.inc_js_goal)
        self.accept('d', self.dec_js_goal)
        self.accept('u', self.inc_interval)
        self.accept('j', self.dec_interval)
        self.accept('b', self.allow_backward)
        self.accept('p', self.pause)
        self.accept('space', self.give_reward)

    def close(self):
        sys.exit()

if __name__ == "__main__":
    CB = CrossBanana()
    run()