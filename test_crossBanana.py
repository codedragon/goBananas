import unittest
from crossBanana import CrossBanana
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
        self.cb.set_variables()
        #self.config = {}
        #execfile('testing_config.py', self.config)

    def test_move_joystick_right(self):
        """
        test that gets reward for pushing the joystick
        """
        #with patch.object(self.cb, 'check_js') as mock:
        messenger.send('js_right', [1])
        #mock.assert_called_with(42)
        self.assertTrue(self.cb.yay_reward)

    def test_hold_joystick_right(self):
        """
        test that if required to hold for reward, actually requires hold
        """
        self.cb.inc_js_goal()

        messenger.send('js_right', [1])
        self.assertFalse(self.cb.yay_reward)
        messenger.send('js_right', [1])
        self.assertTrue(self.cb.yay_reward)

    def test_hold_release_joystick_no_reward(self):
        """
        test that if we are required to hold, but don't hold long enough,
        and release instead, no reward.
        """
        # make goal longer
        self.cb.inc_js_goal()
        messenger.send('js_right', [1])
        self.assertFalse(self.cb.yay_reward)
        messenger.send('let_go', [0])
        self.assertFalse(self.cb.yay_reward)
        messenger.send('js_right', [1])
        self.assertFalse(self.cb.yay_reward)

    def test_move_crosshair(self):
        """
        test we move the crosshair by direction and amount we expect
        """
        dist = self.config['xHairDist']
        start = self.config['xStartPos']
        # send max from joystick
        messenger.send('js_right', [1])
        t_dist = start[0] + dist
        self.assertEquals(self.cb.xHairPos[0] - start[0], t_dist)

    @classmethod
    def tearDownClass(cls):
        taskMgr.remove('Joystick Polling')
        cls.cb.close()
        del cls.cb
        print 'tore down'

if __name__ == "__main__":
    unittest.main(verbosity=2)
