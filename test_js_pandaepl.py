from pandaepl.common import *
from pandaepl import Joystick
from bananas import Bananas
from panda3d.core import WindowProperties

class Test_JS_PandaEPL:
    def __init__(self):
        """
        Initialize the experiment
        """
        # Get experiment instance.
        exp = Experiment.getInstance()
        #exp.setSessionNum(0)
        # Set session to today's date and time
        exp.setSessionNum(datetime.datetime.now().strftime("%y_%m_%d_%H_%M"))
        print exp.getSessionNum()
        config = Conf.getInstance().getConfig()  # Get configuration dictionary.

        # get rid of cursor
        win_props = WindowProperties()
        #print win_props
        win_props.setCursorHidden(True)
        #win_props.setOrigin(20, 20)  # make it so windows aren't on top of each other
        #win_props.setSize(800, 600)  # normal panda window
        # base is global, used by pandaepl from panda3d
        base.win.requestProperties(win_props)

        vr = Vr.getInstance()
        self.banana_models = Bananas(config)
        self.js = Joystick.Joystick.getInstance()
        #print self.js
        vr.inputListen("close", self.close)
        # set up task to be performed between frames
        vr.addTask(Task("checkJS",
                            lambda taskInfo:
                            self.check_position()))

    def check_position(self):
        test = self.js.getEvents()
        if test:
            print test
            print test.keys()
        mag_test = test.keys()
        if mag_test:
            print test[mag_test[0]]

    def start(self):
        """
        Start the experiment.
        """
        #print 'start'
        Experiment.getInstance().start()

    def close(self, inputEvent):
        Experiment.getInstance().stop()

if __name__ == '__main__':
    Test_JS_PandaEPL().start()
else:
    pass
