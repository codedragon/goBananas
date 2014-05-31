import unittest
from trainingBananas import TrainingBananas
from direct.showbase.MessengerGlobal import messenger
from panda3d.core import loadPrcFileData
from direct.task.TaskManagerGlobal import taskMgr


class TrainingBananaTestsT2(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        loadPrcFileData("", "window-type offscreen")
        #print 'about to load world'
        cls.tb = TrainingBananas()

    def setUp(self):
        self.tb.training = 2
        #self.tb.restart_bananas()
        #pass
        # re-initialize variables before each test
        #self.tb.reset_variables()
        #self.config = {}
        #execfile('testing_config.py', self.config)

    def test_move_joystick_right_moves_banana_left(self):
        """
        test that moving the joystick to the right moves the banana
        from the right towards the crosshair in the center, if
        trainingDirection is right
        """
        self.tb.trainDir = 'turnRight'
        self.tb.multiplier = 1
        # if we change direction, have to restart bananas
        self.tb.restart_bananas()
        before = abs(self.tb.base.camera.getH())
        print before
        messenger.send('x_axis', [2])
        # have to step at least twice for anything to happen
        taskMgr.step()
        taskMgr.step()
        # if moving closer to center, getH is getting smaller
        after = abs(self.tb.base.camera.getH())
        print after
        self.assertTrue(after < before)

    def test_cannot_move_joystick_left_if_training_right(self):
        """
        test that cannot move joystick to the left if training to the right
        """
        self.tb.trainDir = 'turnRight'
        self.tb.multiplier = 1
        self.tb.restart_bananas()
        before = self.tb.base.camera.getH()
        messenger.send('x_axis', [-2])
        # have to step at least twice for anything to happen
        taskMgr.step()
        taskMgr.step()
        # should be in same place, not allowed to move left
        self.assertTrue(self.tb.base.camera.getH() == before)

    def test_move_joystick_left_moves_banana_right(self):
        """
        test that moving the joystick to the left moves the banana
        from the left towards the crosshair in the center, if
        trainingDirection is left
        """
        self.tb.trainDir = 'turnLeft'
        self.tb.multiplier = -1
        self.tb.restart_bananas()
        before = abs(self.tb.base.camera.getH())
        print before
        messenger.send('x_axis', [-2])
        # have to step at least twice for anything to happen
        taskMgr.step()
        taskMgr.step()
        # if moving closer to center, getH is getting smaller
        after = abs(self.tb.base.camera.getH())
        print after
        self.assertTrue(after < before)

    def test_cannot_move_joystick_right_if_training_left(self):
        """
        test that cannot move joystick to the right if training to the left
        """
        self.tb.trainDir = 'turnLeft'
        self.tb.multiplier = -1
        self.tb.restart_bananas()
        before = self.tb.base.camera.getH()
        print before
        messenger.send('x_axis', [2])
        # have to step at least twice for anything to happen
        taskMgr.step()
        taskMgr.step()
        # should be in same place, not allowed to move right
        self.assertTrue(self.tb.base.camera.getH() == before)

    def test_reward_when_crosshair_over_banana(self):
        """
        test that rewarded when crosshair is over banana.
        """
        self.tb.trainDir = 'turnRight'
        self.tb.multiplier = 1
        self.tb.restart_bananas()
        while abs(self.tb.base.camera.getH()) > 0:
            messenger.send('x_axis', [2])
            taskMgr.step()
        self.assertTrue(self.tb.yay_reward)

    def test_cannot_go_past_crosshair(self):
        """
         test that even if we move past the crosshair, the camera stops
        """
        self.tb.trainDir = 'turnRight'
        self.tb.multiplier = 1
        self.tb.restart_bananas()
        # avatar_h is where we start, so go further than this
        move_x = int(self.tb.avatar_h + 2)
        for i in range(move_x):
            messenger.send('x_axis', [i])
            taskMgr.step()
        self.assertTrue(self.tb.base.camera.getH() >= 0)

    @classmethod
    def tearDownClass(cls):
        taskMgr.remove('Joystick Polling')
        cls.tb.close()
        del cls.tb
        print 'tore down'

if __name__ == "__main__":
    unittest.main(verbosity=2)
