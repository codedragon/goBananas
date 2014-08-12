from direct.showbase.ShowBase import ShowBase
from joystick import JoystickHandler
from panda3d.core import LineSegs, Vec4
import sys

class TestJoystick(JoystickHandler):
    def __init__(self):
        joystick = True
        self.base = ShowBase()
        if joystick:
            JoystickHandler.__init__(self)
        self.setup_inputs()
        self.frameTask = self.base.taskMgr.add(self.frame_loop, "frame_loop")
        self.frameTask.last = 0
        # determines how much offset between x and y plots
        self.offset = 5
        # determines how much to increase gain to see the plots better
        self.gain = 3
        self.x_mag = self.offset
        self.y_mag = -self.offset
        self.old_x = self.offset
        self.old_y = -self.offset
        # time zero would be in the middle of the screen; what we really want
        # is the left end of the screen.
        self.time = -20
        self.plot = []

    def frame_loop(self, task):
        dt = task.time - task.last
        task.last = task.time
        plot_x = LineSegs()
        plot_x.setThickness(2.0)
        plot_x.setColor(Vec4(1, 1, 0, 1))
        plot_x.moveTo(self.time, 55, self.old_x)
        plot_y = LineSegs()
        plot_y.setThickness(2.0)
        plot_y.moveTo(self.time, 55, self.old_y)
        self.time += dt
        plot_x.drawTo(self.time, 55, self.x_mag)
        plot_y.drawTo(self.time, 55, self.y_mag)
        self.old_x = self.x_mag
        self.old_y = self.y_mag
        node = render.attachNewNode(plot_x.create())
        self.plot.append(node)
        node = render.attachNewNode(plot_y.create())
        self.plot.append(node)
        if self.time > 20:
            self.clear_plot()
        return task.cont

    def move(self, js_dir, js_input):
        print(js_dir, js_input)
        # separate the plots, and increase the gain
        if js_dir == 'x':
            self.x_mag = (js_input * self.gain) + self.offset
            #print('new x', self.x_mag)
        else:
            self.y_mag = -((js_input * self.gain) + self.offset)
            #print('new y', self.y_mag)

    def key_move(self, js_dir):
        #print(js_dir)
        if js_dir == 'x_left':
            self.x_mag -= 0.05
        elif js_dir == 'x_right':
            self.x_mag += 0.05
        elif js_dir == 'y_up':
            self.y_mag -= 0.05
        else:
            self.y_mag += 0.05

    def clear_plot(self):
        for seg in self.plot:
            seg.removeNode()
        self.plot = []
        self.time = -20

    def setup_inputs(self):
        self.accept('x_axis', self.move, ['x'])
        self.accept('y_axis', self.move, ['y'])
        self.accept('arrow_left', self.key_move, ['x_left'])
        self.accept('arrow_right', self.key_move, ['x_right'])
        self.accept('arrow_up', self.key_move, ['y_up'])
        self.accept('arrow_down', self.key_move, ['y_down'])
        self.accept('space', self.clear_plot)
        self.accept('q', self.close)

    def close(self):
        sys.exit()

if __name__ == "__main__":
    TestJoystick()
    run()