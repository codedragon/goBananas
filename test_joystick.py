from direct.showbase.ShowBase import ShowBase
from joystick import JoystickHandler
from panda3d.core import Point3
import sys

class CrossBanana(JoystickHandler):
    def __init__(self):
        self.base = ShowBase()
        # want to see all joystick output
        threshold = 0
        JoystickHandler.__init__(self, threshold)
        self.setup_inputs()
        self.frameTask = self.base.taskMgr.add(self.frame_loop, "frame_loop")
        self.frameTask.delay = 0
        self.delay = False
        self.delay_time = 0.2

    def frame_loop(self, task):
        print task.time
        if self.delay:
            task.delay = task.time + self.delay_time
            self.delay = False
            print('time now', task.time)
            print('delay until', task.delay)
        if task.time > task.delay:
            print "new delay"
            self.delay = True
        else:
            pass
        return task.cont

    def move(self, js_input, js_dir):
        print(js_dir, js_input)
        self.do_somthing_else(js_dir)

    def do_something_else(self, direction):
        if direction == 'backward':
            print 'nope'
        else:
            print 'yup'

    def setup_inputs(self):
        self.accept('js_up', self.move, ['up'])
        self.accept('js_down', self.move, ['down'])
        self.accept('js_left', self.move, ['left'])
        self.accept('js_right', self.move, ['right'])
        self.accept('q', self.close)

    def close(self):
        sys.exit()

if __name__ == "__main__":
    CB = CrossBanana()
    run()