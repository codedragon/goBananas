import unittest
from mock import patch
import mock
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

        self.config = {}
        execfile('testing_config.py', self.config)

    def test_move_joystick_right(self):
        """
        test that gets reward for pushing the joystick
        """
        #with patch.object(self.cb, 'check_js') as mock:
        messenger.send('js_right', [1])
        #mock.assert_called_with(42)
        self.assertTrue()

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
