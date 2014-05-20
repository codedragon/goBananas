import unittest
from trainingBananas import TrainingBananas
from direct.showbase.MessengerGlobal import messenger
from panda3d.core import loadPrcFileData
from direct.task.TaskManagerGlobal import taskMgr


class TrainingBananaTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        loadPrcFileData("", "window-type offscreen")
        #print 'about to load world'
        cls.tb = TrainingBananas()

    def setUp(self):
        pass
        # re-initialize variables before each test
        #self.tb.reset_variables()
        #self.config = {}
        #execfile('testing_config.py', self.config)

    def test_move_joystick_right_gets_reward(self):
        """
        test that gets reward for pushing the joystick
        """
        messenger.send('x_axis', [1])
        self.assertTrue(self.tb.reward_on)

    def test_hold_joystick_right(self):
        """
        test that if required to hold for reward, actually requires hold
        """
        self.tb.inc_js_goal()
        messenger.send('x_axis', [1])
        self.assertFalse(self.tb.reward_on)
        messenger.send('x_axis', [1])
        self.assertTrue(self.tb.reward_on)

    def test_hold_release_joystick_no_reward(self):
        """
        test that if we are required to hold, but don't hold long enough,
        and release instead, no reward.
        """
        # make goal longer
        self.tb.inc_js_goal()
        messenger.send('x_axis', [1])
        self.assertFalse(self.tb.reward_on)
        messenger.send('x_axis', [0])
        self.assertFalse(self.tb.reward_on)
        messenger.send('x_axis', [1])
        self.assertFalse(self.tb.reward_on)

    @classmethod
    def tearDownClass(cls):
        taskMgr.remove('Joystick Polling')
        cls.tb.close()
        del cls.tb
        print 'tore down'

if __name__ == "__main__":
    unittest.main(verbosity=2)
