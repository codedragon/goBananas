from pandaepl import VideoLogQueue
from sys import path
from sys import stdout


try:
    path.insert(1, '../pydaq')
    import pydaq
except ImportError:
    pydaq = None
    print 'Not using PyDaq'


class LogFruit:
    def __init__(self, config):
        if config['sendData'] and pydaq:
            self.send_events = pydaq.OutputEvents()
            self.send_strobe = pydaq.StrobeEvents()
            self.daq_dict = {"Yummy": 200,
                             "Beeps": 201,
                             "Repeat": 300,
                             "Alpha": 400}
        else:
            self.send_events = None
        self.go_trial = True
        if config.get('fruit_to_remember', False):
            self.go_trial = False
        self.min_x = config['min_x']
        self.min_y = config['min_y']

    def log_action(self, action, data):
        VideoLogQueue.VideoLogQueue.getInstance().writeLine(action, [data])
        # We may want to send Alpha differently, right now only indicates that there
        # was a change in some alpha, but no idea what that means.
        if self.send_events:
            self.send_events.send_signal(self.daq_dict[action])
            self.send_strobe.send_signal()

    def log_new_trial(self, trial_num, fruit, trial_type):
        # print('new trial', self.trial_num)
        stdout.write('trial number ' + str(trial_num) + '\n')
        self.log_action("NewTrial", trial_num)
        if trial_type == 'new' or 'repeat' in trial_type:
            self.log_action("RepeatTrial", trial_num)
        if self.send_events:
            self.send_events.send_signal(1000 + trial_num)
            self.send_strobe.send_signal()
            for model in fruit.fruit_models.itervalues():
                # can't send negative numbers or decimals, so
                # need to translate the numbers
                translate_b = [int((model.getPos()[0] - self.min_x) * 1000),
                               int((model.getPos()[1] - self.min_y) * 1000)]
                self.send_events.send_signal(translate_b[0])
                self.send_strobe.send_signal()
                self.send_events.send_signal(translate_b[1])
                self.send_strobe.send_signal()
            if fruit.repeat and self.go_trial:
                self.send_events.send_signal(self.daq_dict['Repeat'])
                self.send_strobe.send_signal()
                self.send_events.send_signal(fruit.repeat_list[2])
                self.send_strobe.send_signal()
