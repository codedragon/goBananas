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

    def move(self, js_input, js_dir):
        print js_dir
        print js_input

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