import unittest
from trainingBananas import TrainingBananas
from direct.showbase.MessengerGlobal import messenger
from panda3d.core import loadPrcFileData
from direct.task.TaskManagerGlobal import taskMgr
import sys

# joystick only sends signal when it has moved, so if holding in one place,
# self.x_mag stays the same until a new signal is given
# many tests are going to be exactly the same for each training, just
# making sure stuff doesn't that shouldn't change doesn't when switching levels


class TrainingBananaTestsT2(unittest.TestCase):
    """
    training 2, move crosshair to banana, left/right, opposite direction does nothing,
    banana always appears in the same place, unless moved by keypress. Does not have
    to let go to get new banana, does not have to leave the crosshair over the banana
    for any particular length of time, just get it there.
    """

    @classmethod
    def setUpClass(cls):
        loadPrcFileData("", "window-type offscreen")
        #print 'about to load world'
        training = 2
        cls.tb = TrainingBananas()
        cls.tb.set_level_variables(training)

    def setUp(self):
        # this will reset x_mag to zero, clearing any joystick pushes,
        # as well resetting other things
        self.tb.reset_variables()
        # make sure at correct training level
        #self.tb.set_level_variables(2)
        # reset banana - this is often done in the test, if we want
        # to ensure a certain direction, but not necessarily
        self.tb.restart_bananas()

    #def test_purposely_fails(self):
    #    self.assertTrue(False)

    def test_move_joystick_right_moves_crosshair_right(self):
        """
        when the banana is to the right, test that moving the joystick
        to the right turns the camera to the right, so that it appears
        that the crosshair is moving towards the banana. Only using
        this test when random is off, since random overrides the direction
        keys. Training 2 and 2.1
        """
        if self.tb.training < 2.2:
            self.tb.trainDir = 'turnRight'
            self.tb.multiplier = 1
            # if we change direction, have to restart bananas
            self.tb.restart_bananas()
            before = abs(self.tb.base.camera.getH())
            #print before
            # step once to get past 0 time
            taskMgr.step()
            messenger.send('x_axis', [2])
            taskMgr.step()
            # if moving closer to center, getH is getting smaller
            after = abs(self.tb.base.camera.getH())
            #print after
            self.assertTrue(after < before)
            return lambda func: func
        return unittest.skip('skipped test, training > 2.1')

    def test_cannot_move_joystick_left_if_training_right(self):
        """
        test that cannot move joystick to the left if training to the right.
        This test is true if free_move is false, but we can only using this
        test when random is off, since random overrides the keys.
        (training 2 and 2.1)
        """
        if self.tb.training < 2.2:
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
            return lambda func: func
        return unittest.skip('skipped test, training > 2.1')

    def test_move_joystick_left_moves_crosshair_left(self):
        """
        when the banana is to the left, test that moving the joystick
        to the left turns the camera to the left, so that it appears
        that the crosshair is moving towards the banana. Only using
        this test when random is off, since random overrides the direction
        keys. Training 2 and 2.1
        """
        if self.tb.training < 2.2:
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
            return lambda func: func
        return unittest.skip('skipped test, training > 2.1')

    def test_cannot_move_joystick_right_if_training_left(self):
        """
        test that cannot move joystick to the right if training to the left
        This test is true if free_move is false (training 2 through 2.2), but
        once again, can only test if random is False, so 2 and 2.1
        """
        if self.tb.training < 2.2:
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
            return lambda func: func
        return unittest.skip('skipped test, training > 2.1')

    def test_cannot_go_past_crosshair(self):
        """
         test that even if we move past the crosshair, the camera stops
         true if require_aim is False, training 2 through 2.3
        """
        if self.tb.training < 2.4:
            # get to zero, then try to go a few steps further
            messenger.send('x_axis', [2 * self.tb.multiplier])
            while abs(self.tb.base.camera.getH()) > 0:
                taskMgr.step()
            # keep trying...
            for i in range(10):
                taskMgr.step()
            # make sure we were really trying to move
            self.assertTrue(abs(self.tb.x_mag) == 2)
            # make sure we didn't go past
            self.assertTrue(self.tb.base.camera.getH() >= 0)
            return lambda func: func
        return unittest.skip('skipped test, training > 2.3')

    def test_after_changing_side_joystick_is_no_longer_allowed_to_go_original_direction(self):
        """
        test that can only move towards center, even if side changes (right to left)
        This test is true if free_move is false. This is tested with a different test
        if random_bananas is true, so good for training 2 and 2.1)
        """
        print self.tb.training
        if self.tb.training < 2.2:
            self.tb.trainDir = 'turnRight'
            self.tb.multiplier = 1
            old_dir = 1
            self.tb.restart_bananas()
            before = self.tb.base.camera.getH()
            print before
            messenger.send('l')
            print self.tb.base.camera.getH()
            # go until last reward
            messenger.send('x_axis', [self.tb.multiplier * 2])
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
            self.assertTrue(self.tb.multiplier == -old_dir)
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
            return lambda func: func
        return unittest.skip('skipped test, training > 2.1')

    def test_after_changing_side_joystick_is_no_longer_allowed_to_go_original_direction_left(self):
        """
        test that can only move towards center, even if side changes (left to right)
        This test is true if free_move is false. This is tested with a different test
        if random_bananas is true, so good for training 2 and 2.1)
        """
        if self.tb.training < 2.2:
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
            return lambda func: func
        return unittest.skip('skipped test, training > 2.1')

    def test_does_not_have_to_let_go_of_joystick_for_new_banana(self):
        """
        test that we get a new banana even if we continue to hold the joystick
        True if must_release is false, just training = 2
        """
        if self.tb.training == 2:
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
            return lambda func: func
        return unittest.skip('skipped test, training > 2')

    def test_reward_when_crosshair_over_banana(self):
        """
        test that rewarded when crosshair is over banana.
        True if require_aim is false, in which case is possible
        to cross over banana too quickly to get a reward.
        Training 2 through 2.3
        """
        if self.tb.training < 2.4:
            messenger.send('x_axis', [self.tb.multiplier * 2])
            while abs(self.tb.base.camera.getH()) > 0:
                taskMgr.step()
            self.assertTrue(self.tb.yay_reward)
            return lambda func: func
        return unittest.skip('skipped test, training > 2.3')

    def test_new_banana_same_side_same_distance(self):
        """
        test that we are always putting the banana back in the same
        place. True if random_banana is False, 2 and 2.1 training levels
        """
        if self.tb.training < 2.2:
            #print 'new non-random banana test'
            before = self.tb.base.camera.getH()
            #print before
            # get reward, then should be in new position
            messenger.send('x_axis', [self.tb.multiplier * 2])
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
            return lambda func: func
        return unittest.skip('skipped test, training > 2.1')

    @classmethod
    def tearDownClass(cls):
        print 'tear down'
        #cls.tb.close()


class TrainingBananaTestsT2_1(unittest.TestCase):
    """ Training 2.1, self.must_release is now true, so test that we are letting go
    of the joystick before we get a new banana
    """

    @classmethod
    def setUpClass(cls):
        loadPrcFileData("", "window-type offscreen")
        #print 'about to load world'
        training = 2.1
        cls.tb = TrainingBananas()
        cls.tb.set_level_variables(training)

    def setUp(self):
        # this will reset x_mag to zero, clearing any joystick pushes,
        # as well resetting other things
        self.tb.reset_variables()
        # make sure at correct training level
        #self.tb.set_level_variables(2)
        # reset banana - makes sure correct training level, avatar
        # heading, etc.
        self.tb.restart_bananas()

    def test_must_let_go_of_joystick_for_new_banana(self):
        """
        test that we have to let go of the joystick before a new banana will appear
        True if must_release is true, training 2.1 and higher
        """
        print self.tb.training
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
        print 'got reward'
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


class TrainingBananaTestsT2_2(TrainingBananaTestsT2, unittest.TestCase):
    """Training 2.2, random is now True. This means we have to change the tests for
    moving the crosshair, since we cannot control which direction we are going. Randomly
    it should hit both directions, assuming we test frequently, so shouldn't be a big
    deal. Also have test to change that random is really happening.
    """

    @classmethod
    def setUpClass(cls):
        loadPrcFileData("", "window-type offscreen")
        #print 'about to load world'
        training = 2.2
        cls.tb = TrainingBananas()
        cls.tb.set_level_variables(training)

    def setUp(self):
        # this will reset x_mag to zero, clearing any joystick pushes,
        # as well resetting other things
        self.tb.reset_variables()
        # make sure at correct training level
        #self.tb.set_level_variables(2)
        # reset banana - this is often done in the test, if we want
        # to ensure a certain direction, but not necessarily
        self.tb.restart_bananas()

    def test_can_move_joystick_in_direction_of_banana(self):
        """
        if the training direction is to the right, the banana is on the right,
        and moving the joystick to the left will move the crosshair to the banana
        True for all training levels, but testing explicitly each direction when
        random is not true
        """
        print self.tb.training
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

    def test_cannot_move_joystick_in_direction_opposite_of_banana(self):
        """
        if the training direction is to the right, the banana is on the right,
        and moving the joystick to the left will move the crosshair to the banana
        True for all training levels, but testing explicitly each direction when
        random is not true.
        """
        print self.tb.training
        before = abs(self.tb.base.camera.getH())
        print before
        # step once to get past 0 time
        taskMgr.step()
        messenger.send('x_axis', [self.tb.multiplier * -2])
        taskMgr.step()
        # since moving opposite direction of multiplier, should
        # not be moving anywhere
        after = abs(self.tb.base.camera.getH())
        print after
        self.assertTrue(after == before)

    def test_new_banana_not_same_side_same_distance(self):
        """
        Test that banana is put down randomly. True if
        random_banana is False, training 2.2 and higher
        """
        print self.tb.training
        # test self.random_bananas = True has effect should have
        print 'new random banana test'
        print self.tb.random_banana
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


class TrainingBananaTestsT2_3(TrainingBananaTestsT2, unittest.TestCase):
    """Training 2.2, random is now True. This means we have to change the tests for
    moving the crosshair, since we cannot control which direction we are going. Randomly
    it should hit both directions, assuming we test frequently, so shouldn't be a big
    deal. Also have test to change that random is really happening.
    """

    @classmethod
    def setUpClass(cls):
        loadPrcFileData("", "window-type offscreen")
        #print 'about to load world'
        training = 2.3
        cls.tb = TrainingBananas()
        cls.tb.set_level_variables(training)

    def setUp(self):
        # this will reset x_mag to zero, clearing any joystick pushes,
        # as well resetting other things
        self.tb.reset_variables()
        # make sure at correct training level
        #self.tb.set_level_variables(2)
        # reset banana - this is often done in the test, if we want
        # to ensure a certain direction, but not necessarily
        self.tb.restart_bananas()

    def test_allowed_to_go_past_banana(self):
        pass

    def test_max_speed_slows_down_after_passing_banana(self):
        pass

    def test_speed_returns_to_normal_after_reward(self):
        pass


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
        # make sure training level is set
        self.tb.restart_bananas()

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
        messenger.send('w')
        self.tb.restart_bananas()
        after = self.tb.num_beeps
        print after
        self.assertTrue(after > before)
        # let's make sure this actually translates to new number of beeps

    def test_s_decreases_reward(self):
        """
        test that s key decreases reward
        """
        before = self.tb.num_beeps
        print before
        messenger.send('s')
        self.tb.restart_bananas()
        after = self.tb.num_beeps
        print after
        self.assertTrue(after < before)
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

    #def test_purposely_fails(self):
    #    self.assertTrue(False)

if __name__ == "__main__":
    # Need to actually shut down python between runs, because the ShowBase instance
    # does not get completely destroyed with just deleting it or the various other
    # tricks I've tried (was not designed for this, see this discussion:
    # https://www.panda3d.org/forums/viewtopic.php?t=10867
    # To get around this, calling a different suite, depending on which number sent
    # in as a sys.argv
    print sys.argv
    print len(sys.argv)
    if len(sys.argv) == 2:
        print 'argument worked'
        print sys.argv[1]
        if int(sys.argv[1]) == 0:
            print 'first suite'
            suite = unittest.TestLoader().loadTestsFromTestCase(TrainingBananaTestsT2)
        elif int(sys.argv[1]) == 1:
            suite = unittest.TestLoader().loadTestsFromTestCase(TrainingBananaTestsT2_1)
        elif int(sys.argv[1]) == 2:
            suite = unittest.TestLoader().loadTestsFromTestCase(TrainingBananaTestsT2_2)
        elif int(sys.argv[1]) == 3:
            suite = unittest.TestLoader().loadTestsFromTestCase(TrainingBananaTestKeys)
        print 'run suite'
        result = unittest.TextTestRunner().run(suite)
        print result
        if not result.wasSuccessful():
            sys.exit(1)
    else:
        unittest.main(verbosity=2)

    #result = unittest.main(verbosity=2)
    #if not result.wasSuccessful():
    #    sys.exit(1)
    #

# because we cannot close down panda3d properly on windows without calling sys.exit,
# the best way to run these classes is from a bash script as separate calls,
# like in test_everything.sh, which is run before every commit.