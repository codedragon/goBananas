import unittest
from environment import Environment
from direct.directbase.DirectStart import base
from panda3d.core import LVecBase4f, ConfigVariableString

class TestEnvironment(unittest.TestCase):

    def test_training(self):
        """
        Test that background is black when in training.
        """
        config = {}
        config['environ'] = 'training'
        ConfigVariableString("window-type", "none").setValue("none")
        Environment(config)
        # print base.getBackgroundColor()
        self.assertEquals(LVecBase4f(0, 0, 0, 0), base.getBackgroundColor())

    def test_original(self):
        """
        Test that proper background is loaded for original environment
        """
        print 'Still have not figured out how to test stuff using pandaepl. meh.'
        config = {}
        execfile('config.py', config)
        config['environ'] = 'original'
        ConfigVariableString("window-type", "none").setValue("none")
        #TestEnvironment = Environment(config)
        #self.assertEqual(TestEnvironment.skyModel.getScale, config['skyScale'])

if __name__ == "__main__":
    unittest.main()