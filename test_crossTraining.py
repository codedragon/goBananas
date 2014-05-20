import unittest
from crossTraining import CrossTraining
from direct.showbase.MessengerGlobal import messenger
from panda3d.core import loadPrcFileData
from direct.task.TaskManagerGlobal import taskMgr


class CrossBananaTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        loadPrcFileData("", "window-type offscreen")
        #print 'about to load world'
        cls.cb = CrossBanana()

    def setUp(self):
        # re-initialize variables before each test
        self.cb.reset_variables()
        #self.config = {}
        #execfile('testing_config.py', self.config)

    def test_move_joystick_right(self):
        """
        test that gets reward for pushing the joystick
        """
        messenger.send('x_axis', [1])
        self.assertTrue(self.cb.reward_on)

    def test_hold_joystick_right(self):
        """
        test that if required to hold for reward, actually requires hold
        """
        self.cb.inc_js_goal()
        messenger.send('x_axis', [1])
        self.assertFalse(self.cb.reward_on)
        messenger.send('x_axis', [1])
        self.assertTrue(self.cb.reward_on)

    def test_hold_release_joystick_no_reward(self):
        """
        test that if we are required to hold, but don't hold long enough,
        and release instead, no reward.
        """
        # make goal longer
        self.cb.inc_js_goal()
        messenger.send('x_axis', [1])
        self.assertFalse(self.cb.reward_on)
        messenger.send('x_axis', [0])
        self.assertFalse(self.cb.reward_on)
        messenger.send('x_axis', [1])
        self.assertFalse(self.cb.reward_on)

    @classmethod
    def tearDownClass(cls):
        taskMgr.remove('Joystick Polling')
        cls.cb.close()
        del cls.cb
        print 'tore down'

if __name__ == "__main__":
    unittest.main(verbosity=2)
