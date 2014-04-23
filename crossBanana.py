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
        config = {}
        execfile('testing_config.py', config)
        print('Subject is', config['subject'])
        self.training = config['training']
        if self.training == 0:
            self.x_start_p = Point3(0, 0, 0)
        else:
            self.cross_pos = config['xStartPos']
        self.cross_move = config['xHairDist']
        JoystickHandler.__init__(self)
        self.setup_inputs()
        # variables for counting how long to hold joystick
        self.js_count = 0
        # eventually may want start goal in config file
        self.js_goal = 1  # start out just have to hit joystick
        # default is to reward for backward movement. May want
        # to make this a configuration option instead.
        self.backward = True
        self.delay = 1  # number of updates to wait for new "trial" (200ms per update)
        self.t_delay = 0  # keeps track of updates waiting for new "trial"
        # set up reward system
        if config['reward'] and PYDAQ_LOADED:
            self.reward = pydaq.GiveReward()
            print 'pydaq'
        else:
            self.reward = None

        #self.frameTask = self.base.taskMgr.add(self.frame_loop, "frame_loop")
        print 'ok then'

    def check_js(self, direction):
        # not moving crosshair, just push joystick to get reward,
        # longer and longer intervals
        # delay determines how long before cross re-appears
        #print 'in check_js'
        if self.t_delay == self.delay:
            js_good = False
            if self.backward:
                # if rewarding for backward, then pushing joystick
                # always get reward
                js_good = True
            elif direction == 'backward':
                # if not rewarding for backward, check to see if
                # backward was pushed before rewarding
                js_good = True
            if js_good:
                print 'counts for reward'
                self.js_count += 1
                if self.js_count == self.js_goal:
                    print('reward')
                    #self.x_change_color(self.x_stop_c)
                    self.give_reward()
                    #self.yay_reward = True
                    #print('touched for', self.js_count)
                    self.js_count = 0
                    self.t_delay = 0
            elif self.js_count >= 0:
                #print 'start over'
                #self.x_change_color(self.x_start_c)
                self.js_count = 0
        else:
            self.t_delay += 1

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

    def setup_inputs(self):
        self.accept('js_up', self.go_forward, )
        self.accept('js_down', self.go_backward)
        self.accept('js_left', self.go_left)
        self.accept('js_right', self.go_right)
        self.accept('arrow_up', self.go_forward, [2])
        self.accept('arrow_down', self.go_backward, [2])
        self.accept('arrow_left', self.go_left, [2])
        self.accept('arrow_right', self.go_right, [2])
        self.accept('q', self.close)

    def close(self):
        sys.exit()

if __name__ == "__main__":
    CB = CrossBanana()
    run()