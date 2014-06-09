import unittest
from trainingBananas import TrainingBananas
from direct.showbase.MessengerGlobal import messenger
from panda3d.core import loadPrcFileData
from direct.task.TaskManagerGlobal import taskMgr

# joystick only sends signal when it has moved, so if holding in one place,
# self.x_mag stays the same until a new signal is given
# many tests are going to be exactly the same for each training, just
# making sure stuff doesn't that shouldn't change doesn't when switching levels


class TrainingBananaTestsT2(unittest.TestCase):
    # training 2, move crosshair to banana, left/right, opposite direction does nothing

    @classmethod
    def setUpClass(cls):
        loadPrcFileData("", "window-type offscreen")
        #print 'about to load world'
        cls.tb = TrainingBananas()

    def setUp(self):
        # this will reset x_mag to zero, clearing any joystick pushes,
        # as well resetting other things
        self.tb.reset_variables()
        # make sure at correct training level
        self.tb.set_level_variables(2)
        # reset banana - this is often done in the test, if we want
        # to ensure a certain direction, but not necessarily
        self.tb.restart_bananas()

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
        # step once to get past 0 time
        taskMgr.step()
        messenger.send('x_axis', [2])
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
        # step once to get past 0 time
        taskMgr.step()
        messenger.send('x_axis', [-2])
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
        # step once to get past 0 time
        taskMgr.step()
        messenger.send('x_axis', [-2])
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
        # step once to get past 0 time
        taskMgr.step()
        messenger.send('x_axis', [2])
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
        messenger.send('x_axis', [2])
        while abs(self.tb.base.camera.getH()) > 0:
            taskMgr.step()
        self.assertTrue(self.tb.yay_reward)

    def test_cannot_go_past_crosshair(self):
        """
         test that even if we move past the crosshair, the camera stops
        """
        # get to zero, then try to go a few steps further
        messenger.send('x_axis', [2 * self.tb.multiplier])
        while abs(self.tb.base.camera.getH()) > 0:
            taskMgr.step()
        for i in range(10):
            taskMgr.step()
        # make sure we were really trying to move
        self.assertTrue(abs(self.tb.x_mag) == 2)
        # make sure we didn't go past
        self.assertTrue(self.tb.base.camera.getH() >= 0)

    def test_after_changing_side_joystick_is_no_longer_allowed_to_go_original_direction(self):
        """
        test that can only move towards center, even if side changes (right to left)
        """
        self.tb.trainDir = 'turnRight'
        self.tb.multiplier = 1
        self.tb.restart_bananas()
        before = self.tb.base.camera.getH()
        print before
        messenger.send('l')
        print self.tb.base.camera.getH()
        # go until last reward
        messenger.send('x_axis', [2])
        while self.tb.reward_count < self.tb.num_beeps:
            taskMgr.step()
        print self.tb.base.camera.getH()
        # keep going while banana still in center.
        # since in center, send zero signal
        # to make sure trial restarts for certain training levels
        messenger.send('x_axis', [0])
        while self.tb.base.camera.getH() == 0:
            taskMgr.step()
        # should be on left side now.
        print 'banana on new side now'
        self.assertTrue(self.tb.multiplier == -1)
        # should be same distance, but opposite side
        self.assertTrue(self.tb.base.camera.getH() / before == -1)
        before = self.tb.base.camera.getH()
        print before
        print self.tb.x_mag
        # now make sure that going right does not move the banana
        messenger.send('x_axis', [2])
        for i in range(10):
            taskMgr.step()
            print self.tb.base.camera.getH()
        self.assertTrue(self.tb.base.camera.getH() == before)

    def test_after_changing_side_joystick_is_no_longer_allowed_to_go_original_direction_left(self):
        """
        test that can only move towards center, even if side changes (left to right)
        """
        self.tb.trainDir = 'turnLeft'
        self.tb.multiplier = -1
        self.tb.restart_bananas()
        before = self.tb.base.camera.getH()
        print before
        messenger.send('r')
        print self.tb.base.camera.getH()
        # go until last reward
        messenger.send('x_axis', [-2])
        while self.tb.reward_count < self.tb.num_beeps:
            taskMgr.step()
        print self.tb.base.camera.getH()
        # keep going while banana still in center
        # since in center, send zero signal
        # to make sure trial restarts for certain training levels
        messenger.send('x_axis', [0])
        while self.tb.base.camera.getH() == 0:
            taskMgr.step()
        # should be on right side now.
        print 'banana on new side now'
        self.assertTrue(self.tb.multiplier == 1)
        # should be same distance, but opposite side
        self.assertTrue(self.tb.base.camera.getH() / before == -1)
        before = self.tb.base.camera.getH()
        print before
        print self.tb.x_mag
        # now make sure that going right does not move the banana
        messenger.send('x_axis', [-2])
        for i in range(10):
            taskMgr.step()
            print self.tb.base.camera.getH()
        self.assertTrue(self.tb.base.camera.getH() == before)

    def test_new_banana_same_side_same_distance(self):
        print 'new banana test'
        before = self.tb.base.camera.getH()
        print before
        # get reward, then should be in new position
        messenger.send('x_axis', [2])
        while self.tb.reward_count < self.tb.num_beeps:
            taskMgr.step()
        # make sure don't move camera after reset
        messenger.send('x_axis', [0])
        print(self.tb.x_mag)
        # now go until banana has been reset
        while not self.tb.moving:
            taskMgr.step()
        print self.tb.base.camera.getH()
        self.assertTrue(self.tb.base.camera.getH() == before)

    def test_do_not_have_let_go_of_joystick_for_new_banana(self):
        """
        test that we get a new banana even if we contintue to hold the joystick
        """
        self.tb.trainDir = 'turnRight'
        self.tb.multiplier = 1
        self.tb.restart_bananas()
        # get to zero, then keep sending joystick
        # signal while checking for new banana
        messenger.send('x_axis', [2])
        while abs(self.tb.base.camera.getH()) > 0:
            taskMgr.step()
        # now go until reward is over
        while self.tb.reward_count < self.tb.num_beeps:
            # still at center
            self.assertTrue(self.tb.base.camera.getH() == 0)
            taskMgr.step()
        #print 'got reward'
        # step to set delay
        taskMgr.step()
        # now go until delay is over
        while self.tb.frameTask.time < self.tb.frameTask.delay:
            taskMgr.step()
        # step to reset banana
        taskMgr.step()
        self.assertTrue(abs(self.tb.base.camera.getH()) > 0)

    @classmethod
    def tearDownClass(cls):
        print 'tear down'
        cls.tb.close()


class TrainingBananaTestsT2_1(unittest.TestCase):
    # training 2.1 now must let go to start next trial
    @classmethod
    def setUpClass(cls):
        loadPrcFileData("", "window-type offscreen")
        #print 'about to load world'
        cls.tb = TrainingBananas()

    def setUp(self):
        # this will reset x_mag to zero, clearing any joystick pushes,
        # as well resetting other things
        self.tb.reset_variables()
        # make sure at correct training level
        self.tb.set_level_variables(2.1)
        # reset banana - this is often done in the test, if we want
        # to ensure a certain direction, but not necessarily
        self.tb.restart_bananas()

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
        # step once to get past 0 time
        taskMgr.step()
        messenger.send('x_axis', [2])
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
        # step once to get past 0 time
        taskMgr.step()
        messenger.send('x_axis', [-2])
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
        # step once to get past 0 time
        taskMgr.step()
        messenger.send('x_axis', [-2])
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
        # step once to get past 0 time
        taskMgr.step()
        messenger.send('x_axis', [2])
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
        messenger.send('x_axis', [2])
        while abs(self.tb.base.camera.getH()) > 0:
            taskMgr.step()
        self.assertTrue(self.tb.yay_reward)

    def test_cannot_go_past_crosshair(self):
        """
         test that even if we move past the crosshair, the camera stops
        """
        # get to zero, then try to go a few steps further
        messenger.send('x_axis', [2 * self.tb.multiplier])
        while abs(self.tb.base.camera.getH()) > 0:
            taskMgr.step()
        for i in range(10):
            taskMgr.step()
        # make sure we were really trying to move
        self.assertTrue(abs(self.tb.x_mag) == 2)
        # make sure we didn't go past
        self.assertTrue(self.tb.base.camera.getH() >= 0)

    def test_after_changing_side_joystick_is_no_longer_allowed_to_go_original_direction(self):
        """
        test that can only move towards center, even if side changes (right to left)
        """
        self.tb.trainDir = 'turnRight'
        self.tb.multiplier = 1
        self.tb.restart_bananas()
        before = self.tb.base.camera.getH()
        print before
        messenger.send('l')
        print self.tb.base.camera.getH()
        # go until last reward
        messenger.send('x_axis', [2])
        while self.tb.reward_count < self.tb.num_beeps:
            taskMgr.step()
        print self.tb.base.camera.getH()
        # keep going while banana still in center.
        # since in center, send zero signal
        # to make sure trial restarts for certain training levels
        messenger.send('x_axis', [0])
        while self.tb.base.camera.getH() == 0:
            taskMgr.step()
        # should be on left side now.
        print 'banana on new side now'
        self.assertTrue(self.tb.multiplier == -1)
        # should be same distance, but opposite side
        self.assertTrue(self.tb.base.camera.getH() / before == -1)
        before = self.tb.base.camera.getH()
        print before
        print self.tb.x_mag
        # now make sure that going right does not move the banana
        messenger.send('x_axis', [2])
        for i in range(10):
            taskMgr.step()
            print self.tb.base.camera.getH()
        self.assertTrue(self.tb.base.camera.getH() == before)

    def test_after_changing_side_joystick_is_no_longer_allowed_to_go_original_direction_left(self):
        """
        test that can only move towards center, even if side changes (left to right)
        """
        self.tb.trainDir = 'turnLeft'
        self.tb.multiplier = -1
        self.tb.restart_bananas()
        before = self.tb.base.camera.getH()
        print before
        messenger.send('r')
        print self.tb.base.camera.getH()
        # go until last reward
        messenger.send('x_axis', [-2])
        while self.tb.reward_count < self.tb.num_beeps:
            taskMgr.step()
        print self.tb.base.camera.getH()
        # keep going while banana still in center
        # since in center, send zero signal
        # to make sure trial restarts for certain training levels
        messenger.send('x_axis', [0])
        while self.tb.base.camera.getH() == 0:
            taskMgr.step()
        # should be on right side now.
        print 'banana on new side now'
        self.assertTrue(self.tb.multiplier == 1)
        # should be same distance, but opposite side
        self.assertTrue(self.tb.base.camera.getH() / before == -1)
        before = self.tb.base.camera.getH()
        print before
        print self.tb.x_mag
        # now make sure that going right does not move the banana
        messenger.send('x_axis', [-2])
        for i in range(10):
            taskMgr.step()
            print self.tb.base.camera.getH()
        self.assertTrue(self.tb.base.camera.getH() == before)

    def test_new_banana_same_side_same_distance(self):
        print 'new banana test'
        before = self.tb.base.camera.getH()
        print before
        # get reward, then should be in new position
        messenger.send('x_axis', [2])
        while self.tb.reward_count < self.tb.num_beeps:
            taskMgr.step()
        # make sure don't move camera after reset
        messenger.send('x_axis', [0])
        print(self.tb.x_mag)
        # now go until banana has been reset
        while not self.tb.moving:
            taskMgr.step()
        print self.tb.base.camera.getH()
        self.assertTrue(self.tb.base.camera.getH() == before)

    def test_must_let_go_of_joystick_for_new_banana(self):
        """
        test that we have to let go of the joystick before a new banana will appear
        """
        # get to zero, then keep sending joystick
        # signal while checking for new banana
        messenger.send('x_axis', [2 * self.tb.multiplier])
        while abs(self.tb.base.camera.getH()) > 0:
            taskMgr.step()
        # now go until reward is over
        while self.tb.reward_count < self.tb.num_beeps:
            # still at center
            self.assertTrue(self.tb.base.camera.getH() == 0)
            taskMgr.step()
        #print 'got reward'
        # step to set delay
        taskMgr.step()
        # now go until delay is over
        while self.tb.frameTask.time < self.tb.frameTask.delay:
            self.assertTrue(self.tb.base.camera.getH() == 0)
            taskMgr.step()
        # go a few steps while still sending joystick signal
        # to make sure new banana does not appear yet.
        for i in range(10):
            self.assertTrue(self.tb.base.camera.getH() == 0)
            taskMgr.step()
        # now release the joystick
        messenger.send('x_axis', [0])
        taskMgr.step()
        #print self.tb.yay_reward
        self.assertTrue(abs(self.tb.base.camera.getH()) > 0)


    @classmethod
    def tearDownClass(cls):
        print 'tear down'
        cls.tb.close()


class TrainingBananaTestsT2_2(unittest.TestCase):
    # training 2.2 now have random bananas. Tests about changing the side the banana is on
    # are meaningless, since bananas are showing up randomly, so not using those
    @classmethod
    def setUpClass(cls):
        loadPrcFileData("", "window-type offscreen")
        #print 'about to load world'
        cls.tb = TrainingBananas()

    def setUp(self):
        # this will reset x_mag to zero, clearing any joystick pushes,
        # as well resetting other things
        self.tb.reset_variables()
        # make sure at correct training level
        self.tb.set_level_variables(2.2)
        # reset banana - this is often done in the test, if we want
        # to ensure a certain direction, but not necessarily
        self.tb.restart_bananas()

    def test_can_move_joystick_direction_of_banana(self):
        """
        if the training direction is to the right, the banana is on the right,
        and moving the joystick to the left will move the crosshair to the banana
        """
        before = abs(self.tb.base.camera.getH())
        print before
        # step once to get past 0 time
        taskMgr.step()
        messenger.send('x_axis', [self.tb.multiplier * 2])
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
        # step once to get past 0 time
        taskMgr.step()
        messenger.send('x_axis', [-2])
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
        # step once to get past 0 time
        taskMgr.step()
        messenger.send('x_axis', [-2])
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
        # step once to get past 0 time
        taskMgr.step()
        messenger.send('x_axis', [2])
        taskMgr.step()
        # should be in same place, not allowed to move right
        self.assertTrue(self.tb.base.camera.getH() == before)

    def test_reward_when_crosshair_over_banana(self):
        """
        test that rewarded when crosshair is over banana.
        """
        messenger.send('x_axis', [self.tb.multiplier * 2])
        while abs(self.tb.base.camera.getH()) > 0:
            taskMgr.step()
        self.assertTrue(self.tb.yay_reward)

    def test_cannot_go_past_crosshair(self):
        """
         test that even if we move past the crosshair, the camera stops
        """
        # get to zero, then try to go a few steps further
        messenger.send('x_axis', [2 * self.tb.multiplier])
        while abs(self.tb.base.camera.getH()) > 0:
            taskMgr.step()
        for i in range(10):
            taskMgr.step()
        # make sure we were really trying to move
        self.assertTrue(abs(self.tb.x_mag) == 2)
        # make sure we didn't go past
        self.assertTrue(self.tb.base.camera.getH() >= 0)

    def test_new_banana_not_same_side_same_distance(self):
        before = self.tb.base.camera.getH()
        # get reward, then should be in new position
        messenger.send('x_axis', [self.tb.multiplier * 2])
        while self.tb.reward_count < self.tb.num_beeps:
            taskMgr.step()
        # make sure don't move camera after reset
        messenger.send('x_axis', [0])
        # now go until banana has been reset
        while not self.tb.moving:
            taskMgr.step()
        #print self.tb.base.camera.getH()
        self.assertFalse(self.tb.base.camera.getH() == before)

    def test_must_let_go_of_joystick_for_new_banana(self):
        """
        test that we have to let go of the joystick before a new banana will appear
        """
        # get to zero, then keep sending joystick
        # signal while checking for new banana
        messenger.send('x_axis', [2 * self.tb.multiplier])
        while abs(self.tb.base.camera.getH()) > 0:
            taskMgr.step()
        # now go until reward is over
        while self.tb.reward_count < self.tb.num_beeps:
            # still at center
            self.assertTrue(self.tb.base.camera.getH() == 0)
            taskMgr.step()
        #print 'got reward'
        # step to set delay
        taskMgr.step()
        # now go until delay is over
        while self.tb.frameTask.time < self.tb.frameTask.delay:
            self.assertTrue(self.tb.base.camera.getH() == 0)
            taskMgr.step()
        # go a few steps while still sending joystick signal
        # to make sure new banana does not appear yet.
        for i in range(10):
            self.assertTrue(self.tb.base.camera.getH() == 0)
            taskMgr.step()
        # now release the joystick
        messenger.send('x_axis', [0])
        taskMgr.step()
        #print self.tb.yay_reward
        self.assertTrue(abs(self.tb.base.camera.getH()) > 0)

    @classmethod
    def tearDownClass(cls):
        print 'tear down'
        cls.tb.close()


class TrainingBananaTestsT2_3(unittest.TestCase):
    # training 2.2, banana appears randomly on either side, multiple distances. Must let go
    # of joystick to start next trial, can only move direction towards center
    @classmethod
    def setUpClass(cls):
        loadPrcFileData("", "window-type offscreen")
        #print 'about to load world'
        cls.tb = TrainingBananas()

    def setUp(self):
        # this will reset x_mag to zero, clearing any joystick pushes,
        # as well resetting other things
        self.tb.reset_variables()
        # make sure at correct training level
        self.tb.set_level_variables(2.3)
        # reset banana - this is often done in the test, if we want
        # to ensure a certain direction, but not necessarily
        self.tb.restart_bananas()

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

    def test_can_move_joystick_left_if_training_right(self):
        """
        test that cannot move joystick to the left if training to the right
        """
        self.tb.trainDir = 'turnRight'
        self.tb.multiplier = 1
        self.tb.restart_bananas()
        before = abs(self.tb.base.camera.getH())
        messenger.send('x_axis', [-2])
        # have to step at least twice for anything to happen
        taskMgr.step()
        taskMgr.step()
        # should be in same place, not allowed to move left
        self.assertTrue(abs(self.tb.base.camera.getH()) > before)

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
        before = abs(self.tb.base.camera.getH())
        print before
        messenger.send('x_axis', [2])
        # have to step at least twice for anything to happen
        taskMgr.step()
        taskMgr.step()
        # should be in same place, not allowed to move right
        self.assertTrue(abs(self.tb.base.camera.getH()) > before)

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
        # get to zero, then try to go a few steps further
        while abs(self.tb.base.camera.getH()) > 0:
            messenger.send('x_axis', [2])
            taskMgr.step()
        for i in range(10):
            messenger.send('x_axis', [i])
            taskMgr.step()
        self.assertTrue(self.tb.base.camera.getH() >= 0)

    def test_must_let_go_of_joystick_for_new_banana(self):
        """
         test that even if we move past the crosshair, the camera stops
        """
        self.tb.trainDir = 'turnRight'
        self.tb.multiplier = 1
        self.tb.restart_bananas()
        # get to zero, then keep sending joystick
        # signal while checking for new banana
        while abs(self.tb.base.camera.getH()) > 0:
            messenger.send('x_axis', [2])
            taskMgr.step()
        # once in center can make sure that we stay in the center
        # until reward is over
        while self.tb.reward_count < self.tb.numBeeps:
            # still at center
            self.assertTrue(self.tb.base.camera.getH() == 0)
            messenger.send('x_axis', [2])
            taskMgr.step()
        #print 'got reward'
        # step to set delay
        taskMgr.step()
        # now go until last delay is over, should still stay in center
        while self.tb.frameTask.time < self.tb.frameTask.delay:
            self.assertTrue(self.tb.base.camera.getH() == 0)
            messenger.send('x_axis', [2])
            taskMgr.step()
        # go a few steps while still sending joystick signal
        # to make sure new banana does not appear yet.
        for i in range(10):
            self.assertTrue(self.tb.base.camera.getH() == 0)
            messenger.send('x_axis', [2])
            taskMgr.step()
        #print 'still at center'
        #print self.tb.yay_reward
        # now step without sending joystick signal
        # normally when releasing joystick, there is a
        # zero signal sent, so do this
        messenger.send('x_axis', [0])
        taskMgr.step()
        self.assertTrue(abs(self.tb.base.camera.getH()) > 0)

    @classmethod
    def tearDownClass(cls):
        print 'tear down'
        cls.tb.close()


class TrainingBananaTestKeys(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        loadPrcFileData("", "window-type offscreen")
        #print 'about to load world'
        cls.tb = TrainingBananas()

    def setUp(self):
        # this will reset x_mag to zero, clearing any joystick pushes,
        # as well resetting other things
        self.tb.reset_variables()
        # make sure at correct training level
        self.tb.set_level_variables(2)

    def test_move_using_right_arrow_key(self):
        """
        test that using the right arrow to the right moves the banana
        from the right towards the crosshair in the center, if
        trainingDirection is right
        """
        self.tb.trainDir = 'turnRight'
        self.tb.multiplier = 1
        # if we change direction, have to restart bananas
        self.tb.restart_bananas()
        before = abs(self.tb.base.camera.getH())
        print before
        # dt is so small, since not actually writing to the screen,
        # that we need to do this a couple of times to actually be
        # a large enough change to register
        taskMgr.step()
        messenger.send('arrow_right')
        taskMgr.step()
        messenger.send('arrow_right')
        taskMgr.step()
        messenger.send('arrow_right')
        taskMgr.step()
        # if moving closer to center, getH is getting smaller
        after = abs(self.tb.base.camera.getH())
        print after
        self.assertTrue(after < before)

    def test_move_using_left_arrow_key(self):
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
        messenger.send('arrow_left')
        # dt is so small, since not actually writing to the screen,
        # that we need to do this a couple of times to actually be
        # a large enough change to register
        taskMgr.step()
        messenger.send('arrow_left')
        taskMgr.step()
        messenger.send('arrow_left')
        taskMgr.step()
        messenger.send('arrow_left')
        taskMgr.step()
        # if moving closer to center, getH is getting smaller
        after = abs(self.tb.base.camera.getH())
        print after
        self.assertTrue(after < before)

    def test_e_increases_banana_distance(self):
        """
        test that e key increases the distance from banana to crosshair
        """
        self.tb.trainDir = 'turnRight'
        self.tb.multiplier = 1
        self.tb.restart_bananas()
        before = self.tb.base.camera.getH()
        print before
        messenger.send('e')
        self.tb.restart_bananas()
        # should be further out now
        after = self.tb.base.camera.getH()
        print after
        self.assertTrue(after > before)

    def test_d_decreases_banana_distance(self):
        """
        test that e key increases the distance from banana to crosshair
        """
        self.tb.trainDir = 'turnRight'
        self.tb.multiplier = 1
        self.tb.restart_bananas()
        before = self.tb.base.camera.getH()
        print before
        messenger.send('d')
        self.tb.restart_bananas()
        self.assertTrue(self.tb.base.camera.getH() < before)

    def test_w_increases_reward(self):
        """
        test that w key increases reward
        """
        before = self.tb.num_beeps
        print before
        messenger.send('e')
        self.tb.restart_bananas()
        after = self.tb.num_beeps
        print after
        self.assertTrue(after > before)
        # let's make sure this actually translates to new number of beeps


    def test_d_decreases_banana_distance(self):
        """
        test that e key increases the distance from banana to crosshair
        """
        self.tb.trainDir = 'turnRight'
        self.tb.multiplier = 1
        self.tb.restart_bananas()
        before = self.tb.base.camera.getH()
        print before
        messenger.send('d')
        self.tb.restart_bananas()
        self.assertTrue(self.tb.base.camera.getH() < before)

    def test_l_changes_banana_to_left_side(self):
        """
        test that e key increases the distance from banana to crosshair
        """
        self.tb.trainDir = 'turnRight'
        self.tb.multiplier = 1
        self.tb.restart_bananas()
        before = self.tb.base.camera.getH()
        print before
        messenger.send('l')
        self.tb.restart_bananas()
        # should be on left side now.
        self.assertTrue(self.tb.multiplier == -1)
        # should be same distance, but opposite side
        self.assertTrue(self.tb.base.camera.getH() / before == -1)

    def test_r_changes_banana_to_right_side(self):
        """
        test that e key increases the distance from banana to crosshair
        """
        self.tb.trainDir = 'turnLeft'
        self.tb.multiplier = -1
        self.tb.restart_bananas()
        before = self.tb.base.camera.getH()
        print before
        messenger.send('r')
        self.tb.restart_bananas()
        # should be on left side now
        self.assertTrue(self.tb.multiplier == 1)
        # should be same distance, but opposite side
        self.assertTrue(self.tb.base.camera.getH() / before == -1)

    @classmethod
    def tearDownClass(cls):
        print 'tear down'
        cls.tb.close()


if __name__ == "__main__":
    # loader = unittest.TestLoader()
    # suite1 = loader.loadTestsFromTestCase(TrainingBananaTestsT2)
    # suite2 = loader.loadTestsFromTestCase(TrainingBananaTestsT2_1)
    # suite3 = loader.loadTestsFromTestCase(TrainingBananaTestKeys)
    # all_suite = unittest.TestSuite([suite1, suite3])
    # print(all_suite.countTestCases())
    # unittest.TextTestRunner(verbosity=2).run(all_suite)
    unittest.main(verbosity=2)
