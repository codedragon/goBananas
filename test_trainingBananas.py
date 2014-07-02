import unittest
from trainingBananas import TrainingBananas
from direct.showbase.MessengerGlobal import messenger
from panda3d.core import loadPrcFileData
from direct.task.TaskManagerGlobal import taskMgr
import sys
import time

# joystick only sends signal when it has moved, so if holding in one place,
# self.x_mag stays the same until a new signal is given
# many tests are going to be exactly the same for each training, just
# making sure stuff doesn't that shouldn't change doesn't when switching levels

# These are not all strictly unittests. Some are definitely more functional in
# nature, but I didn't see any reason to separate them out.


def is_int_string(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


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
        # make defaults so stuff tests as fast as possible, overrides config file
        cls.tb.reward_time = 0.01
        cls.tb.num_beeps = 1
        cls.tb.avatar_h = 1.5

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
            # make sure going to the right
            messenger.send('r')
            # if we change direction, have to restart bananas
            self.tb.restart_bananas()
            before = abs(self.tb.base.camera.getH())
            #print before
            messenger.send('x_axis', [self.tb.multiplier * 2])
            # have to step twice, can't move on the first frame
            taskMgr.step()
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
            #print('training', self.tb.training)
            # make sure going to the right
            messenger.send('r')
            # if we change direction, have to restart bananas
            self.tb.restart_bananas()
            before = self.tb.base.camera.getH()
            # send opposite direction in
            messenger.send('x_axis', [self.tb.multiplier * -2])
            # have to step twice, can't move on the first frame
            taskMgr.step()
            taskMgr.step()
            # should be in same place, not allowed to move left
            #print('should be in same place', self.tb.base.camera.getH())
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
            # make sure going to the right
            messenger.send('l')
            # if we change direction, have to restart bananas
            self.tb.restart_bananas()
            before = abs(self.tb.base.camera.getH())
            #print before
            messenger.send('x_axis', [self.tb.multiplier * 2])
            # have to step twice, can't move on the first frame
            taskMgr.step()
            taskMgr.step()
            # if moving closer to center, getH is getting smaller
            after = abs(self.tb.base.camera.getH())
            #print after
            self.assertTrue(after < before)
            return lambda func: func
        return unittest.skip('skipped test, training > 2.1')

    def test_cannot_move_joystick_right_if_training_left(self):
        """
        test that cannot move joystick to the right if training to the left
        This test is true if free_move is None (training 2 through 2.2), but
        once again, can only test if random is False, so 2 and 2.1
        """
        if self.tb.training < 2.2:
            # make sure going to the left
            messenger.send('l')
            # if we change direction, have to restart bananas
            self.tb.restart_bananas()
            before = self.tb.base.camera.getH()
            # send in opposite direction
            messenger.send('x_axis', [self.tb.multiplier * -2])
            # have to step twice, can't move on the first frame
            taskMgr.step()
            taskMgr.step()
            # should be in same place, not allowed to move right
            self.assertTrue(self.tb.base.camera.getH() == before)
            return lambda func: func
        return unittest.skip('skipped test, training > 2.1')

    def test_cannot_go_past_banana(self):
        """
         test that even if we move past the banana with the crosshiar,
         the camera stops. True if require_aim is False, training 2 through 2.4
        """
        if self.tb.training < 2.5:
            # get to zero, then try to go a few steps further
            before = self.tb.base.camera.getH()
            messenger.send('x_axis', [2 * self.tb.multiplier])
            while abs(self.tb.base.camera.getH()) > 0:
                taskMgr.step()
            # make sure we got reward, and then kept trying
            while self.tb.reward_count < self.tb.num_beeps:
                taskMgr.step()
            # now keep trying for a bit
            for i in range(50):
                taskMgr.step()
            # make sure we didn't go to other side
            # if we were on pos, should still be pos,
            # if we were on neg, should still be neg.
            # so multiplying old and new should be a pos. number or zero
            self.assertTrue(self.tb.base.camera.getH() * before >= 0)
            return lambda func: func
        return unittest.skip('skipped test, training > 2.3')

    def test_after_changing_side_joystick_is_no_longer_allowed_to_go_original_direction(self):
        """
        test that can only move towards center, even if side changes (right to left)
        This test is true if free_move is false. This is tested with a different test
        if random_bananas is true, so good for training 2 and 2.1)
        """
        #print self.tb.training
        if self.tb.training < 2.2:
            messenger.send('r')
            self.tb.restart_bananas()
            old_dir = self.tb.multiplier
            before = self.tb.base.camera.getH()
            #print before
            messenger.send('l')
            #print self.tb.base.camera.getH()
            # go until last reward
            messenger.send('x_axis', [self.tb.multiplier * 2])
            while self.tb.reward_count < self.tb.num_beeps:
                taskMgr.step()
            #print self.tb.base.camera.getH()
            # keep going while banana still in center.
            # since in center, send zero signal
            # to make sure trial restarts for certain training levels
            messenger.send('x_axis', [0])
            while self.tb.base.camera.getH() == 0:
                taskMgr.step()
            # should be on left side now.
            #print 'banana on new side now'
            self.assertTrue(self.tb.multiplier == -old_dir)
            # should be same distance, but opposite side
            self.assertTrue(self.tb.base.camera.getH() / before == -1)
            before = self.tb.base.camera.getH()
            #print before
            #print self.tb.x_mag
            # now make sure that going right does not move the banana
            messenger.send('x_axis', [2])
            for i in range(10):
                taskMgr.step()
            #print self.tb.base.camera.getH()
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
            messenger.send('l')
            self.tb.restart_bananas()
            old_dir = self.tb.multiplier
            before = self.tb.base.camera.getH()
            #print before
            messenger.send('r')
            #print self.tb.base.camera.getH()
            # go until last reward
            messenger.send('x_axis', [-2])
            while self.tb.reward_count < self.tb.num_beeps:
                taskMgr.step()
            #print self.tb.base.camera.getH()
            # keep going while banana still in center
            # since in center, send zero signal
            # to make sure trial restarts for certain training levels
            messenger.send('x_axis', [0])
            while self.tb.base.camera.getH() == 0:
                taskMgr.step()
            # should be on right side now.
            #print 'banana on new side now'
            self.assertTrue(self.tb.multiplier == -old_dir)
            # should be same distance, but opposite side
            self.assertTrue(self.tb.base.camera.getH() / before == -1)
            before = self.tb.base.camera.getH()
            #print before
            #print self.tb.x_mag
            # now make sure that going right does not move the banana
            messenger.send('x_axis', [-2])
            for i in range(5):
                taskMgr.step()
            #print self.tb.base.camera.getH()
            self.assertTrue(self.tb.base.camera.getH() == before)
            return lambda func: func
        return unittest.skip('skipped test, training > 2.1')

    def test_does_not_have_to_let_go_of_joystick_for_new_banana(self):
        """
        test that we get a new banana even if we continue to hold the joystick
        True if must_release is false, just training = 2
        """
        if self.tb.training == 2:
            # right is positive multiplier
            self.tb.multiplier = 1
            self.tb.restart_bananas()
            # get to zero, then keep sending joystick
            # signal while checking for new banana
            messenger.send('x_axis', [2])
            while abs(self.tb.base.camera.getH()) > 0:
                taskMgr.step()
            #print('should be at center', self.tb.base.camera.getH())
            #print('check reward count', self.tb.reward_count)
            # now go until reward is over
            while self.tb.reward_count < self.tb.num_beeps:
                taskMgr.step()
            # step to set delay
            taskMgr.step()
            # now go until delay is over
            while self.tb.frameTask.time < self.tb.frameTask.delay:
                taskMgr.step()
            # step to reset banana
            taskMgr.step()
            # we never changed the amount we were sending to the joystick
            # to zero, so if camera moved, it moved despite us continuing
            # to push on the joystick
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
            #print(self.tb.x_mag)
            # now go until banana has been reset
            while not self.tb.moving:
                taskMgr.step()
            #print self.tb.base.camera.getH()
            self.assertTrue(self.tb.base.camera.getH() == before)
            return lambda func: func
        return unittest.skip('skipped test, training > 2.1')

    @classmethod
    def tearDownClass(cls):
        print 'tear down'
        #cls.tb.close()


class TrainingBananaTestsT2_1(TrainingBananaTestsT2, unittest.TestCase):
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
        # make defaults so stuff tests as fast as possible, overrides config file
        cls.tb.reward_time = 0.01
        cls.tb.num_beeps = 1
        cls.tb.avatar_h = 1.5

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
        True if must_release is true, training 2.1 and higher. Test somewhat meaningless
        after training 2.3, since require aiming, and have already checked for holding
        crosshair over banana for x time.
        """
        if self.tb.training < 2.4:
            #print self.tb.training
            #print 'let go for new banana'
            #print('let go', self.tb.must_release)
            # get to zero, then keep sending joystick
            # signal while checking for new banana
            messenger.send('x_axis', [2 * self.tb.multiplier])
            # I would use absolute, but then can't tell when we cross over
            # zero
            camera_h = self.tb.base.camera.getH()
            #print camera_h
            if camera_h > 0:
                while self.tb.base.camera.getH() > 0:
                    #print('camera head', self.tb.base.camera.getH())
                    taskMgr.step()
            else:
                while self.tb.base.camera.getH() < 0:
                    #print('camera head', self.tb.base.camera.getH())
                    taskMgr.step()
            #print 'first loop over'
            # now go until reward is over
            while self.tb.reward_count < self.tb.num_beeps:
                taskMgr.step()
            #print 'got reward'

            # step to set delay
            taskMgr.step()
            # now go until delay is overs
            while self.tb.frameTask.time < self.tb.frameTask.delay:
                taskMgr.step()
            #print 'delay over'
            # go through once to stash the banana
            taskMgr.step()
            # go a few steps while still sending joystick signal
            # to make sure new banana does not appear yet.
            # banana should now be gone
            for i in range(10):
                self.assertTrue(self.tb.banana.isStashed())
                taskMgr.step()
            # now release the joystick
            messenger.send('x_axis', [0])
            taskMgr.step()
            #print self.tb.yay_reward
            self.assertFalse(self.tb.banana.isStashed())
            return lambda func: func
        return unittest.skip('skipped test, training > 2.3')


class TrainingBananaTestsT2_2(TrainingBananaTestsT2_1, unittest.TestCase):
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
        # make defaults so stuff tests as fast as possible, overrides config file
        cls.tb.reward_time = 0.01
        cls.tb.num_beeps = 1
        cls.tb.avatar_h = 1.5
        cls.tb.initial_speed = 1

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
        #print self.tb.training
        #print 'joystick direction banana'
        before = abs(self.tb.base.camera.getH())
        #print before
        messenger.send('x_axis', [self.tb.multiplier * 2])
        # have to step twice, can't move on the first frame
        taskMgr.step()
        taskMgr.step()
        # if moving closer to center, getH is getting smaller
        after = abs(self.tb.base.camera.getH())
        #print after
        self.assertTrue(after < before)

    def test_cannot_move_joystick_in_direction_opposite_of_banana(self):
        """
        if the training direction is to the right, the banana is on the right,
        and moving the joystick to the left will move the crosshair to the banana
        True for all training levels, but testing explicitly each direction when
        random is not true.
        """
        if self.tb.training < 2.2:
            #print self.tb.training
            before = abs(self.tb.base.camera.getH())
            #print before
            messenger.send('x_axis', [self.tb.multiplier * -2])
            # have to step twice, can't move on the first frame
            taskMgr.step()
            taskMgr.step()
            # since moving opposite direction of multiplier, should
            # not be moving anywhere
            after = abs(self.tb.base.camera.getH())
            #print after
            self.assertTrue(after == before)
            return lambda func: func
        return unittest.skip('skipped test, training > 2.2')

    def test_new_banana_not_same_side_same_distance(self):
        """
        Test that banana is put down randomly. True if
        random_banana is False, training 2.2 and higher
        Possible to get banana in same place, by chance, so
        run twice and check all three.
        """
        #print self.tb.training
        # test self.random_bananas = True has effect should have
        #print 'new random banana test'
        #print self.tb.random_banana
        before = self.tb.base.camera.getH()
        # get reward, then should be in new position
        messenger.send('x_axis', [self.tb.multiplier * 2])
        # I would use absolute position, but then can't tell when
        # we cross over zero, at which time we need to stop moving
        camera_h = self.tb.base.camera.getH()
        #print camera_h
        if camera_h > 0:
            while self.tb.base.camera.getH() > 0:
                print('camera head', self.tb.base.camera.getH())
                taskMgr.step()
        else:
            while self.tb.base.camera.getH() < 0:
                #print('camera head', self.tb.base.camera.getH())
                taskMgr.step()
        #print 'first loop over'
        # once at center, don't move camera
        messenger.send('x_axis', [0])
        # get reward
        while self.tb.reward_count < self.tb.num_beeps:
            taskMgr.step()

        #print('check camera', self.tb.base.camera.getH())
        # still in center,
        # now step until banana has been reset
        while not self.tb.moving:
            taskMgr.step()

        next = self.tb.base.camera.getH()
        # Go again, may by chance have been twice in the same place,
        # but if really pseudo-random, highly unlikely three times in
        # the same place.
        messenger.send('x_axis', [self.tb.multiplier * 2])
        camera_h = self.tb.base.camera.getH()
        if camera_h > 0:
            while self.tb.base.camera.getH() > 0:
                #print('camera head', self.tb.base.camera.getH())
                taskMgr.step()
        else:
            while self.tb.base.camera.getH() < 0:
                #print('camera head', self.tb.base.camera.getH())
                taskMgr.step()

        #print 'first loop over again'
        # once at center, don't move camera
        messenger.send('x_axis', [0])
        # get reward
        while self.tb.reward_count < self.tb.num_beeps:
            taskMgr.step()

        #print('check camera', self.tb.base.camera.getH())
        # now step until banana has been reset
        while not self.tb.moving:
            taskMgr.step()

        last = self.tb.base.camera.getH()
        #print('before', before)
        #print('next', next)
        #print('last', last)
        self.assertFalse(last == next == before)


class TrainingBananaTestsT2_3(TrainingBananaTestsT2_2, unittest.TestCase):
    """Training 2.3, banana appears randomly on either side, multiple distances.
    Must let go of joystick to start next trial, both directions now allowed,
    however wrong direction is slower than towards center.
    """

    @classmethod
    def setUpClass(cls):
        loadPrcFileData("", "window-type offscreen")
        #print 'about to load world'
        training = 2.3
        cls.tb = TrainingBananas()
        cls.tb.set_level_variables(training)
        # make defaults so stuff tests as fast as possible, overrides config file
        cls.tb.reward_time = 0.01
        cls.tb.num_beeps = 1
        cls.tb.avatar_h = 1.5

    def setUp(self):
        # this will reset x_mag to zero, clearing any joystick pushes,
        # as well resetting other things
        self.tb.reset_variables()
        # make sure at correct training level
        #self.tb.set_level_variables(2)
        # reset banana - this is often done in the test, if we want
        # to ensure a certain direction, but not necessarily
        self.tb.restart_bananas()

    def test_allowed_to_go_in_direction_opposite_banana(self):
        #print 'opposite direction of banana'
        #print self.tb.training
        before = abs(self.tb.base.camera.getH())
        #print before
        messenger.send('x_axis', [self.tb.multiplier * -2])
        # have to step twice, can't move on the first frame
        taskMgr.step()
        taskMgr.step()
        # opposite direction allowed, so should have moved
        after = abs(self.tb.base.camera.getH())
        self.assertNotEqual(before, after)

    def test_speed_slower_going_away_from_banana(self):
        """
        test that if we go the wrong direction, we go slower.
        """
        if self.tb.training == 2.3:
            # first two frames get messed up for timing, so go two steps
            print self.tb.free_move
            taskMgr.step()
            taskMgr.step()
            messenger.send('x_axis', [2 * -self.tb.multiplier])
            camera_h = self.tb.base.camera.getH()
            #print camera_h
            # go a few steps, see how long it takes
            start = time.time()
            for i in range(30):
                print self.tb.speed
                taskMgr.step()
            first_time = time.time() - start
            first_dist = camera_h - self.tb.base.camera.getH()
            #print('dist', first_dist)
            first_speed = abs(first_dist/first_time)
            # now stop so speed resets.
            messenger.send('x_axis', [0])
            taskMgr.step()
            print('before', self.tb.speed)
            # now go towards center, see how long it takes
            # this should be much faster
            messenger.send('x_axis', [2 * self.tb.multiplier])
            avatar_h = self.tb.base.camera.getH()
            #print avatar_h
            start = time.time()
            for i in range(30):
                print self.tb.speed
                taskMgr.step()
            second_time = time.time() - start
            #print('time', second_time)
            #print self.tb.base.camera.getH()
            second_dist = avatar_h - self.tb.base.camera.getH()
            #print('dist', second_dist)
            second_speed = abs(second_dist / second_time)
            #print('first', first_speed)
            #print('second', second_speed)
            self.assertTrue(first_speed < second_speed)
            return lambda func: func
        return unittest.skip('skipped test, training != 2.3')


class TrainingBananaTestsT2_4(TrainingBananaTestsT2_3, unittest.TestCase):
    """Training 2.3, banana appears randomly on either side, multiple distances.
    Must let go of joystick to start next trial, both directions now allowed,
    and speed is the same in both directions.
    """

    @classmethod
    def setUpClass(cls):
        loadPrcFileData("", "window-type offscreen")
        #print 'about to load world'
        training = 2.4
        cls.tb = TrainingBananas()
        cls.tb.set_level_variables(training)
        # make defaults so stuff tests as fast as possible, overrides config file
        cls.tb.reward_time = 0.01
        cls.tb.num_beeps = 1
        cls.tb.avatar_h = 1.5

    def setUp(self):
        # this will reset x_mag to zero, clearing any joystick pushes,
        # as well resetting other things
        self.tb.reset_variables()
        # make sure at correct training level
        #self.tb.set_level_variables(2)
        # reset banana - this is often done in the test, if we want
        # to ensure a certain direction, but not necessarily
        self.tb.restart_bananas()

    def test_allowed_to_go_in_direction_opposite_banana(self):
        #print 'opposite direction of banana'
        #print self.tb.training
        before = abs(self.tb.base.camera.getH())
        #print before
        messenger.send('x_axis', [self.tb.multiplier * -2])
        # have to step twice, can't move on the first frame
        taskMgr.step()
        taskMgr.step()
        # opposite direction allowed, so should have moved
        after = abs(self.tb.base.camera.getH())
        self.assertNotEqual(before, after)

    def test_speed_same_going_away_from_banana(self):
        """
        test that if we go the wrong direction, we go slower.
        """
        # first two frames get messed up for timing, so go two steps
        print self.tb.free_move
        taskMgr.step()
        taskMgr.step()
        # we are randomly placing banana. if close to center, go away from center first
        # if close to wall, go towards center first
        if self.tb.base.camera.getH() < 10:
            first_direction = 2 * -self.tb.multiplier
        else:
            first_direction = 2 * self.tb.multiplier
        print first_direction
        messenger.send('x_axis', [first_direction])
        camera_h = self.tb.base.camera.getH()
        print camera_h
        # go a few steps, see how long it takes
        start = time.time()
        for i in range(30):
            print self.tb.speed
            taskMgr.step()
        first_time = time.time() - start
        first_dist = camera_h - self.tb.base.camera.getH()
        print('dist', first_dist)
        first_speed = abs(first_dist/first_time)
        # now stop so speed resets.
        messenger.send('x_axis', [0])
        taskMgr.step()
        taskMgr.step()
        print('before', self.tb.speed)
        # now go towards center, see how long it takes
        # this should be much faster
        messenger.send('x_axis', [-first_direction])
        avatar_h = self.tb.base.camera.getH()
        print avatar_h
        start = time.time()
        for i in range(30):
            print self.tb.speed
            taskMgr.step()
        second_time = time.time() - start
        print('time', second_time)
        print self.tb.base.camera.getH()
        second_dist = avatar_h - self.tb.base.camera.getH()
        print('dist', second_dist)
        second_speed = abs(second_dist / second_time)
        print('first', first_speed)
        #print('second', second_speed)
        self.assertTrue(abs(first_speed - second_speed) < 0.5)


class TrainingBananaTestsT2_5(TrainingBananaTestsT2_4, unittest.TestCase):
    """Training 2.5, subject has to line up crosshair to banana (not go past)
    for min. time, slows down if goes past banana, both directions allowed
    """

    @classmethod
    def setUpClass(cls):
        loadPrcFileData("", "window-type offscreen")
        #print 'about to load world'
        training = 2.5
        cls.tb = TrainingBananas()
        cls.tb.set_level_variables(training)
        # make defaults so stuff tests as fast as possible, overrides config file
        cls.tb.reward_time = 0.01
        cls.tb.num_beeps = 1
        cls.tb.avatar_h = 1.5

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
        """
         test that even if we move past the banana, the camera continues
         to move, true if require_aim is True, training 2.4 and higher
        """
        #print 'go past banana'
        # get to zero, then try to go a few steps further
        messenger.send('x_axis', [2 * self.tb.multiplier])
        # I would use absolute, but then can't tell when we cross over
        # zero
        camera_h = self.tb.base.camera.getH()
        #print camera_h
        if camera_h > 0:
            while self.tb.base.camera.getH() > 0:
                #print('camera head', self.tb.base.camera.getH())
                taskMgr.step()
        else:
            while self.tb.base.camera.getH() < 0:
                #print('camera head', self.tb.base.camera.getH())
                taskMgr.step()
        #print 'first loop over'
        #print('camera head', self.tb.base.camera.getH())
        # now go past banana
        for i in range(10):
            taskMgr.step()
        # make sure we were really trying to move
        self.assertTrue(abs(self.tb.x_mag) == 2)
        # make sure we were able to go past. if original camera was positive,
        # heading should now be negative, and vise-versa.
        #print self.tb.base.camera.getH()
        if camera_h > 0:
            self.assertTrue(self.tb.base.camera.getH() < 0)
        else:
            self.assertTrue(self.tb.base.camera.getH() > 0)

    def test_max_speed_slows_down_after_passing_banana(self):
        """
        test that after we go past the banana, we go slower.
        """
        # first two frames get messed up for timing, so go two steps
        taskMgr.step()
        taskMgr.step()
        messenger.send('x_axis', [2 * self.tb.multiplier])
        # I would use absolute, but then can't tell when we cross over
        # zero
        camera_h = self.tb.base.camera.getH()
        #print camera_h
        # go a few steps, see how long it takes
        start = time.time()
        for i in range(30):
            taskMgr.step()
        first_time = time.time() - start
        #print('time', first_time)
        #print self.tb.base.camera.getH()
        first_dist = camera_h - self.tb.base.camera.getH()
        #print('dist', first_dist)
        first_speed = abs(first_dist/first_time)
        #print 'first test over'
        #print('camera head', self.tb.base.camera.getH())
        # now go to center
        if camera_h > 0:
            while self.tb.base.camera.getH() > 0:
                #print('camera head', self.tb.base.camera.getH())
                taskMgr.step()
        else:
            while self.tb.base.camera.getH() < 0:
                #print('camera head', self.tb.base.camera.getH())
                taskMgr.step()
        #print 'first loop over'
        #print('camera head', self.tb.base.camera.getH())
        # now go past banana
        while abs(self.tb.base.camera.getH()) < 1:
            #print('camera head', self.tb.base.camera.getH())
            taskMgr.step()
        #print('camera head', self.tb.base.camera.getH())
        # and test again
        #print 'test again'
        # and now we can test moving again, first send 2 steps,
        # this puts us starting at the same slow_factor as for
        # the first run
        taskMgr.step()
        taskMgr.step()
        avatar_h = self.tb.base.camera.getH()
        #print avatar_h
        start = time.time()
        for i in range(30):
            taskMgr.step()
        second_time = time.time() - start
        #print('time', second_time)
        #print self.tb.base.camera.getH()
        second_dist = avatar_h - self.tb.base.camera.getH()
        #print('dist', second_dist)
        second_speed = abs(second_dist / second_time)
        #print('first', first_speed)
        #print('second', second_speed)
        self.assertTrue(first_speed > second_speed)

    def test_speed_returns_to_normal_after_reward(self):
        """
        test that after we go past the banana, we go slower.
        """
        # first two frames get messed up for timing, so go two steps
        taskMgr.step()
        taskMgr.step()
        messenger.send('x_axis', [2 * self.tb.multiplier])
        # I would use absolute, but then can't tell when we cross over
        # zero
        camera_h = self.tb.base.camera.getH()
        #print camera_h
        # go a few steps, see how long it takes
        #print 'test'
        start = time.time()
        for i in range(30):
            #print('i', i)
            taskMgr.step()
        first_time = time.time() - start
        #print('time', first_time)
        #print self.tb.base.camera.getH()
        first_dist = camera_h - self.tb.base.camera.getH()
        #print('dist', first_dist)
        first_speed = abs(first_dist/first_time)
        #print 'first test over'
        #print('camera head', self.tb.base.camera.getH())
        # now go to center
        if camera_h > 0:
            while self.tb.base.camera.getH() > 0:
                #print('camera head', self.tb.base.camera.getH())
                taskMgr.step()
        else:
            while self.tb.base.camera.getH() < 0:
                #print('camera head', self.tb.base.camera.getH())
                taskMgr.step()
        #print 'first loop over'
        #print('camera head', self.tb.base.camera.getH())
        # now go past banana
        while abs(self.tb.base.camera.getH()) < 1:
            #print('camera head', self.tb.base.camera.getH())
            taskMgr.step()
        # and now return to banana for reward,
        # go the other way until we get to center again
        messenger.send('x_axis', [2 * -self.tb.multiplier])
        while abs(self.tb.base.camera.getH()) > 0.1:
            taskMgr.step()
        # get reward
        messenger.send('x_axis', [0])
        while self.tb.reward_count < self.tb.num_beeps:
            taskMgr.step()
        # now step until banana has been reset
        while not self.tb.moving:
            taskMgr.step()
        # and now we can test moving again, first send two steps,
        # this puts us starting at the same slow_factor as for
        # the first run
        taskMgr.step()
        taskMgr.step()
        messenger.send('x_axis', [2 * -self.tb.multiplier])
        avatar_h = self.tb.base.camera.getH()
        #print avatar_h
        #print 'test again'
        start = time.time()
        for i in range(30):
            #print('i', i)
            taskMgr.step()
        second_time = time.time() - start
        #print('time', second_time)
        #print self.tb.base.camera.getH()
        second_dist = avatar_h - self.tb.base.camera.getH()
        #print('dist', second_dist)
        second_speed = abs(second_dist / second_time)
        #print('first', first_speed)
        #print('second', second_speed)
        self.assertTrue(abs(first_speed - second_speed) < 0.5)


class TrainingBananaTestsT3(unittest.TestCase):
    """Training 2.5, subject has to line up crosshair to banana (not go past)
    for min. time, slows down if goes past banana, both directions allowed
    """

    @classmethod
    def setUpClass(cls):
        loadPrcFileData("", "window-type offscreen")
        #print 'about to load world'
        training = 3
        cls.tb = TrainingBananas()
        cls.tb.set_level_variables(training)
        # make defaults so stuff tests as fast as possible, overrides config file
        cls.tb.reward_time = 0.01
        cls.tb.num_beeps = 1

    def setUp(self):
        # this will reset x_mag to zero, clearing any joystick pushes,
        # as well resetting other things
        self.tb.reset_variables()
        # make sure at correct training level
        #self.tb.set_level_variables(2)
        # reset banana - this is often done in the test, if we want
        # to ensure a certain direction, but not necessarily
        self.tb.restart_bananas()

    def test_can_move_forward(self):
        # test can now move forward
        before = self.tb.base.camera.getPos()
        print before
        messenger.send('y_axis', [2])
        # have to step twice, can't move on the first frame
        taskMgr.step()
        taskMgr.step()
        # opposite direction allowed, so should have moved
        after = self.tb.base.camera.getPos()
        self.assertNotEqual(before, after)


class TrainingBananaTestKeys(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        loadPrcFileData("", "window-type offscreen")
        #print 'about to load world'
        cls.tb = TrainingBananas()
        # make defaults so stuff tests as fast as possible, overrides config file
        cls.tb.reward_time = 0.01
        cls.tb.num_beeps = 1
        cls.tb.avatar_h = 1.5

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
        # right is positive multiplier
        self.tb.multiplier = 1
        # if we change direction, have to restart bananas
        self.tb.restart_bananas()
        before = abs(self.tb.base.camera.getH())
        #print before
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
        #print after
        self.assertTrue(after < before)

    def test_move_using_left_arrow_key(self):
        """
        test that moving the joystick to the left moves the banana
        from the left towards the crosshair in the center, if
        trainingDirection is left
        """
        # left is negative multiplier
        self.tb.multiplier = -1
        self.tb.restart_bananas()
        before = abs(self.tb.base.camera.getH())
        #print before
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
        #print after
        self.assertTrue(after < before)

    def test_e_increases_banana_distance(self):
        """
        test that e key increases the distance from banana to crosshair
        """
        # right is positive multiplier
        self.tb.multiplier = 1
        self.tb.restart_bananas()
        before = self.tb.base.camera.getH()
        #print before
        messenger.send('e')
        self.tb.restart_bananas()
        # should be further out now
        after = self.tb.base.camera.getH()
        #print after
        self.assertTrue(after > before)

    def test_d_decreases_banana_distance(self):
        """
        test that d key decreases the distance from banana to crosshair
        """
        # right is positive multiplier
        self.tb.multiplier = 1
        self.tb.restart_bananas()
        before = self.tb.base.camera.getH()
        #print before
        messenger.send('d')
        self.tb.restart_bananas()
        self.assertTrue(self.tb.base.camera.getH() < before)

    def test_w_increases_reward(self):
        """
        test that w key increases reward
        """
        before = self.tb.num_beeps
        #print before
        messenger.send('w')
        self.tb.restart_bananas()
        after = self.tb.num_beeps
        #print after
        self.assertTrue(after > before)
        # let's make sure this actually translates to new number of beeps

    def test_s_decreases_reward(self):
        """
        test that s key decreases reward
        """
        before = self.tb.num_beeps
        #print before
        messenger.send('s')
        self.tb.restart_bananas()
        after = self.tb.num_beeps
        #print after
        self.assertTrue(after < before)
        # let's make sure this actually translates to new number of beeps

    def test_l_changes_banana_to_left_side(self):
        """
        test that l key changes the direction the subject is going to left
        """
        # right is positive multiplier
        self.tb.multiplier = 1
        self.tb.restart_bananas()
        before = self.tb.base.camera.getH()
        #print before
        messenger.send('l')
        self.tb.restart_bananas()
        # should be on left side now.
        self.assertTrue(self.tb.multiplier == -1)
        # should be same distance, but opposite side
        self.assertTrue(self.tb.base.camera.getH() / before == -1)

    def test_r_changes_banana_to_right_side(self):
        """
        test that r key changes the direction the subject is going to right
        """
        # left is negative multiplier
        self.tb.multiplier = -1
        self.tb.restart_bananas()
        before = self.tb.base.camera.getH()
        #print before
        messenger.send('r')
        self.tb.restart_bananas()
        # should be on left side now
        self.assertTrue(self.tb.multiplier == 1)
        # should be same distance, but opposite side
        self.assertTrue(self.tb.base.camera.getH() / before == -1)

    def test_f_changes_banana_to_forward(self):
        """
        test that f key changes the direction the subject is going to forward
        """
        # left is negative multiplier
        self.tb.multiplier = -1
        self.tb.restart_bananas()
        before = self.tb.base.camera.getH()
        #print before
        messenger.send('f')
        self.tb.restart_bananas()
        # should be on left side now
        self.assertTrue(self.tb.multiplier == 0)
        # should be in the middle, far away
        #self.assertTrue(self.tb.base.camera.getH() / before == -1)

    #def test_purposely_fails(self):
    #    self.assertTrue(False)

if __name__ == "__main__":
    # Need to actually shut down python between runs, because the ShowBase instance
    # does not get completely destroyed with just deleting it or the various other
    # tricks I've tried (was not designed for this, see this discussion:
    # https://www.panda3d.org/forums/viewtopic.php?t=10867
    # To get around this, calling a different suite, depending on which number sent
    # in as a sys.argv
    #print sys.argv
    #print len(sys.argv)
    if len(sys.argv) == 2 and is_int_string(sys.argv[1]):
        #print 'argument worked'
        if int(sys.argv[1]) == 0:
            #print 'first suite'
            suite = unittest.TestLoader().loadTestsFromTestCase(TrainingBananaTestsT2)
        elif int(sys.argv[1]) == 1:
            suite = unittest.TestLoader().loadTestsFromTestCase(TrainingBananaTestsT2_1)
        elif int(sys.argv[1]) == 2:
            suite = unittest.TestLoader().loadTestsFromTestCase(TrainingBananaTestsT2_2)
        elif int(sys.argv[1]) == 3:
            suite = unittest.TestLoader().loadTestsFromTestCase(TrainingBananaTestsT2_3)
        elif int(sys.argv[1]) == 4:
            suite = unittest.TestLoader().loadTestsFromTestCase(TrainingBananaTestsT2_4)
        elif int(sys.argv[1]) == 5:
            suite = unittest.TestLoader().loadTestsFromTestCase(TrainingBananaTestKeys)
        #print 'run suite'
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