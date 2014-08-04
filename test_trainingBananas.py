import unittest
from trainingBananas import TrainingBananas
from direct.showbase.MessengerGlobal import messenger
from panda3d.core import loadPrcFileData
from direct.task.TaskManagerGlobal import taskMgr
import sys
import time
import random

# joystick only sends signal when it has moved, so if holding in one place,
# self.x_mag stays the same until a new signal is given
# many tests are going to be exactly the same for each training, just
# making sure stuff doesn't that shouldn't change doesn't when switching levels

# These are not all strictly unittests. Some are definitely more functional in
# nature, but I didn't see any reason to separate them out.

# for comparing speeds, I assume frame rate is constant, so presenting the same
# number of frames will take the same amount of time. Need to test frame rate
# separately, and not off-screen as these tests are done.


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
        print cls.tb.training

    def setUp(self):
        print self.tb.training
        # this will reset x_mag to zero, clearing any joystick pushes,
        # as well resetting other things
        self.tb.reset_variables()
        # make sure at correct training level
        #self.tb.set_level_variables(2)
        # reset banana - this is often done in the test, if we want
        # to ensure a certain direction, but not necessarily
        self.tb.restart_bananas()
        print self.tb.training

    #def test_purposely_fails(self):
    #    self.assertTrue(False)

    def move_to_opposite_side(self, before=None):
        # this method is to move the camera to the opposite of the screen that
        # it is currently on (2.5 and above)
        if before is None:
            before = self.tb.base.camera.getH()
        print('before', before)
        # we are moving to the other side, so let's do this quickly
        messenger.send('x_axis', [self.tb.multiplier * abs(before/2)])
        print('sent in', self.tb.multiplier * abs(before/2))
        after = -before
        #print('after will be', after)
        #print self.tb.wrong_speed
        wrong_speed = self.tb.wrong_speed
        self.tb.wrong_speed = self.tb.initial_speed
        #print self.tb.wrong_speed
        # if multiplier is positive, than we are
        # getting close, then slow down
        close = -before/abs(before) * (abs(before) - 2)
        #print close
        if self.tb.multiplier > 0:
            #print 'positive'
            while self.tb.base.camera.getH() > close:
                #print self.tb.base.camera.getH()
                taskMgr.step()
            print('getting close', self.tb.base.camera.getH())
            messenger.send('x_axis', [self.tb.multiplier * 1])
            while self.tb.base.camera.getH() > after:
                #print self.tb.base.camera.getH()
                taskMgr.step()
        else:
            #print 'negative'
            while self.tb.base.camera.getH() < close:
                #print self.tb.base.camera.getH()
                taskMgr.step()
            print('getting close', self.tb.base.camera.getH())
            messenger.send('x_axis', [self.tb.multiplier * 1])
            while self.tb.base.camera.getH() < after:
                #print self.tb.base.camera.getH()
                taskMgr.step()
        # set speed in dir away from banana back
        self.tb.wrong_speed = wrong_speed
        print('after', self.tb.base.camera.getH())

    def move_to_center_for_reward(self, stay=None):
        # only works if we are not allowed to go past center,
        # so less than 2.3
        if self.tb.training > 2.2:
            raise Exception("This method only for training less than 2.3")
        messenger.send('x_axis', [4 * self.tb.multiplier])
        if abs(self.tb.base.camera.getH()) < 4:
            messenger.send('x_axis', [self.tb.multiplier * 2])
        # go until we get reward
        while self.tb.reward_count < self.tb.num_beeps:
            taskMgr.step()
        if stay == 'stay':
            # keep going while banana still in center.
            # since in center, send zero signal
            # to make sure trial restarts for certain training levels
            messenger.send('x_axis', [0])
            while not self.tb.moving:
                taskMgr.step()

    def move_to_center_without_using_reward(self):
        # move to the center, but don't use reward to tell
        # that we are in the center
        #
        # difficulties with how to tell when in 'center':
        # never hit exactly zero, and sometimes
        # stopped by collision slightly before zero.
        # so can't just go until equals zero.
        # easiest way is to see when stops moving,
        # but this only works if there is a forced stop
        # at center (2.5 and above allow going past center)
        # so if below 2.5 look for where camera stops moving
        # and if 2.5 or higher, can just go until changes sign
        # need to move in direction towards center, in any case
        # since we don't know if we are on the original side,
        # don't know if multiplier is in direction of center

        # Timing is affected by printing stuff out, so be careful while
        # troubleshooting!!!
        before = self.tb.base.camera.getH()
        my_move = 6 * before/abs(before)
        if abs(before) < 4:
            my_move = 2 * before/abs(before)
        #print('try this', my_move)
        messenger.send('x_axis', [my_move])
        #print('start position', before)
        #print self.tb.multiplier
        if self.tb.training > 2.4:
            # The further out you start, the faster you go, and the
            # longer it takes to stop, and therefor the more likely
            # you are to stop beyond the zone where there will be a
            # collision, so stop earlier, and slow down before center
            while abs(self.tb.base.camera.getH()) > 1:
                taskMgr.step()
            #print('before fine tuning', self.tb.base.camera.getH())
            if before > 0:
                #print 'positive'
                messenger.send('x_axis', [0.5])
                while self.tb.base.camera.getH() > 0.2:
                    taskMgr.step()
                    #print('camera head', self.tb.base.camera.getH())
            else:
                #print 'negative'
                while self.tb.base.camera.getH() < -0.2:
                    taskMgr.step()
                    #print('camera head', self.tb.base.camera.getH())
            #print('after', self.tb.base.camera.getH())
        else:
            # have to step a couple of times to do initial move
            taskMgr.step()
            taskMgr.step()
            # get close, then slow down, otherwise we overshoot, and
            # going way faster here than could go in the game.
            # step until we don't go anymore
            while abs(self.tb.base.camera.getH()) > 1:
                taskMgr.step()
            messenger.send('x_axis', [self.tb.multiplier])
            while self.tb.base.camera.getH() != before:
                before = self.tb.base.camera.getH()
                taskMgr.step()
                #print self.tb.base.camera.getH()

    def clear_collisions(self):
        # need to clear collisions, if some have happened, but haven't been
        # checked yet (ended trial before reward)
        self.tb.restart_bananas()
        taskMgr.step()
        self.tb.check_banana()

    def test_cannot_move_forward(self):
        """
        For all turning training (2.x), not allowed to go forward
        """
        before = self.tb.base.camera.getPos()
        messenger.send('y_axis', [2])
        for i in range(50):
            taskMgr.step()
        after = self.tb.base.camera.getPos()
        self.assertEqual(before, after)

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
         test that even if we try to move past the banana with the crosshair,
         the camera stops. True if require_aim is False, training 2 through 2.4
        """
        if self.tb.training < 2.5:
            before = self.tb.base.camera.getH()
            print before
            # get to zero, then try to go a few steps further,
            # don't use reward to find center, since this test is used
            # in higher training levels
            self.move_to_center_without_using_reward()
            print 'after initial move'
            print self.tb.base.camera.getH()
            # now keep trying for a bit, for 2.1 in reality this may cause
            # us to go in circles, getting reward, and popping back up on the
            # same side, but that's okay, should never be able to move past center
            messenger.send('x_axis', [2 * self.tb.multiplier])
            for i in range(20):
                taskMgr.step()
                print self.tb.base.camera.getH()
            # make sure we didn't go to other side
            # if we were on pos, should still be pos,
            # if we were on neg, should still be neg.
            # so multiplying old and new should be a pos. number or zero
            # if in center, could be slightly over the line
            after = self.tb.base.camera.getH()
            #print after
            # can be slightly off center. for beginning training, don't
            # have to let go to get new banana, but new banana always on same
            # side as before, so banana could be in the center or on the same
            # side as it was before, just not past the banana, in any case.
            #self.assertTrue(abs(after) < 0.7 or after * before >= 0)
            # The further away we were from zero, the further in the other direction
            # we may have traveled before stopped, but never more than 2/10 of way.
            self.assertTrue(abs(after) < (abs(before) * 0.2) or after * before >= 0)
            return lambda func: func
        return unittest.skip('skipped test, training > 2.4')

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
            #print self.tb.training
            old_dir = self.tb.multiplier
            before = self.tb.base.camera.getH()
            #print old_dir
            #print before
            # should change to left after reward,
            # when restart bananas happens
            messenger.send('l')
            # go to center for reward, and stay until moving is allowed again.
            self.move_to_center_for_reward('stay')
            # should be on left side now.
            print 'banana on new side now'
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
            #print 'send left'
            messenger.send('l')
            self.tb.restart_bananas()
            old_dir = self.tb.multiplier
            #print old_dir
            before = self.tb.base.camera.getH()
            #print before
            # this will take effect after reward
            messenger.send('r')
            self.move_to_center_for_reward('stay')
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
            # get to reward, then keep sending joystick
            # signal while checking for new banana
            self.move_to_center_for_reward('stay')
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
        True if require_aim is false, in which case need to
        stay in the center for some specified amount of time.
        Training 2 through 2.3
        """
        if self.tb.training < 2.4:
            before = self.tb.base.camera.getH()
            messenger.send('x_axis', [0])
            # go to center (banana at center)
            self.move_to_center_without_using_reward()
            # make sure approximately in center
            position = self.tb.base.camera.getH()
            print('final position', position)
            # make sure we lined up the crosshair and bananas
            # (approximately in center)
            self.assertTrue(-0.8 < position < 0.8)
            # make sure we lined up the crosshair and bananas
            # (approximately in center)
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
            self.move_to_center_for_reward('stay')
            #print self.tb.base.camera.getH()
            self.assertTrue(self.tb.base.camera.getH() == before)
            return lambda func: func
        return unittest.skip('skipped test, training > 2.1')

    def tearDown(self):
        self.clear_collisions()


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
            # if we use our handy method to move to center,
            # banana will be stashed and moved before the
            # method returns, since it switches to sending
            # a zero signal
            messenger.send('x_axis', [2 * self.tb.multiplier])
            # go until reward is over
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

    def tearDown(self):
        self.clear_collisions()


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
        # make it so random selections never go out to 22, which is possible
        # in the game, but screws up tests, since can't move in one direction
        # from that point.
        self.tb.all_random_selections = [[2, 4, 6, 8, 10, 12, 14, 16, 18, 20]]
        self.tb.current_choice = 0
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
        random is not true, so just test for non-random here.
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
        before = self.tb.base.camera.getH()
        print before
        # get reward, then should be in new position
        messenger.send('x_axis', [self.tb.multiplier * 2])
        # get reward
        # once you get to 2.5, have to stay in center for some time
        # to get reward, so get to center, stop moving, then proceed
        # as other training. know banana in center when numbers switch from
        # pos to neg or vise-versa
        if self.tb.training > 2.4:
            self.tb.base.camera.setH(0)
            messenger.send('x_axis', [0])
            #print 'proceed normally'
        while self.tb.reward_count < self.tb.num_beeps:
            #print('check camera', self.tb.base.camera.getH())
            taskMgr.step()
        # once have reward, don't move camera
        messenger.send('x_axis', [0])
        # still in center,
        # now step until banana has been reset
        while not self.tb.moving:
            taskMgr.step()
        second = self.tb.base.camera.getH()
        #print second
        # Go again, may by chance have been twice in the same place,
        # but if really pseudo-random, highly unlikely three times in
        # the same place.
        messenger.send('x_axis', [self.tb.multiplier * 2])
        if self.tb.training > 2.4:
            self.tb.base.camera.setH(0)
            messenger.send('x_axis', [0])
            #print 'proceed normally'
        while self.tb.reward_count < self.tb.num_beeps:
            #print('check camera', self.tb.base.camera.getH())
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
        #print('second', second)
        #print('last', last)
        self.assertFalse(last == second == before)

    def tearDown(self):
        self.clear_collisions()


class TrainingBananaTestsT2_3(TrainingBananaTestsT2_2, unittest.TestCase):
    """Training 2.3, banana appears randomly on either side, multiple distances.
    Must let go of joystick to start next trial, both directions now allowed,
    however wrong direction is slower than towards center. Since can now move away
    from center, now should check that can't move past the screen edge.
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
        # make it so random selections never go out to 22, which is possible
        # in the game, but screws up tests, since can't move in one direction
        # from that point.
        self.tb.all_random_selections = [[2, 4, 6, 8, 10, 12, 14, 16, 18, 20]]
        self.tb.current_choice = 0
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
        # in case we are training right next to the edge of the screen
        while self.tb.base.camera.getH() > 21:
            print self.tb.base.camera.getH()
            self.tb.restart_bananas()
        before = abs(self.tb.base.camera.getH())
        print before
        messenger.send('x_axis', [self.tb.multiplier * -2])
        # move a few times, if slow in opposite direction is
        # turned way down, takes a while to move
        taskMgr.step()
        taskMgr.step()
        taskMgr.step()
        taskMgr.step()
        # opposite direction allowed, so should have moved
        after = abs(self.tb.base.camera.getH())
        self.assertNotEqual(before, after)

    def test_move_to_opposite_side_slower_going_away_from_banana(self):
        """
        test that if we go the wrong direction, we go slower. only true for this level
        """
        if self.tb.training == 2.3:
            # timing not great right out of the starting gate...
            messenger.send('x_axis', [0])
            for i in range(30):
                taskMgr.step()
            # first check away from banana direction, should be slow
            messenger.send('x_axis', [2 * -self.tb.multiplier])
            camera_h = self.tb.base.camera.getH()
            print camera_h
            for i in range(30):
                #print self.tb.speed
                taskMgr.step()
            print self.tb.base.camera.getH()
            first_dist = abs(camera_h - self.tb.base.camera.getH())
            print('dist', first_dist)
            # now stop so speed resets.
            messenger.send('x_axis', [0])
            taskMgr.step()
            # now go towards center, see how long it takes
            # this should be much faster
            messenger.send('x_axis', [2 * self.tb.multiplier])
            avatar_h = self.tb.base.camera.getH()
            print avatar_h
            for i in range(30):
                #print self.tb.speed
                taskMgr.step()
            print self.tb.base.camera.getH()
            second_dist = abs(avatar_h - self.tb.base.camera.getH())
            print('dist', second_dist)
            # if second is faster, that means we have gone further,
            # so second should be significantly larger than larger
            # test that difference is relatively large
            self.assertTrue(second_dist - first_dist > 0.1)
            return lambda func: func
        return unittest.skip('skipped test, training != 2.3')

    def test_cannot_go_past_screen_edge(self):
        # test if we can go past screen edge
        # don't go through center, since we could get a reward and get
        # a new banana in a new place and go in circles for a while.
        # we'll test both sides, eventually since do this test multiple
        # times on multiple levels with random bananas.
        messenger.send('x_axis', [6 * -self.tb.multiplier])
        # first get to edge
        while abs(self.tb.base.camera.getH()) < 22:
            taskMgr.step()
        # now try to go further, shouldn't be able to move
        for i in range(5):
            previous = self.tb.base.camera.getH()
            taskMgr.step()
            self.assertEqual(previous, self.tb.base.camera.getH())

    def tearDown(self):
        self.clear_collisions()


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
        # make it so random selections never go out to 22, which is possible
        # in the game, but screws up tests, since can't move in one direction
        # from that point.
        self.tb.all_random_selections = [[2, 4, 6, 8, 10, 12, 14, 16, 18, 20]]
        self.tb.current_choice = 0
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
        test that if we go the wrong direction, we go the same speed now.
        """
        # timing not great right out of the starting gate...
        messenger.send('x_axis', [0])
        for i in range(30):
            taskMgr.step()
        # we are randomly placing banana. if close to center, go away from center first
        # if close to wall, go towards center first
        if abs(self.tb.base.camera.getH()) < 6:
            first_direction = 2 * -self.tb.multiplier
        else:
            first_direction = 2 * self.tb.multiplier
        #print first_direction
        messenger.send('x_axis', [first_direction])
        camera_h = self.tb.base.camera.getH()
        #print camera_h
        #print 'start first loop'
        for i in range(30):
            #print self.tb.speed
            taskMgr.step()
        first_dist = abs(camera_h - self.tb.base.camera.getH())
        # now stop so speed resets.
        messenger.send('x_axis', [0])
        taskMgr.step()
        #taskMgr.step()
        #print('before', self.tb.speed)
        # now go opposite direction, see how long it takes
        # this should be the same
        messenger.send('x_axis', [-first_direction])
        avatar_h = self.tb.base.camera.getH()
        #print avatar_h
        #print 'start next loop'
        for i in range(30):
            #print self.tb.speed
            taskMgr.step()
        #print self.tb.base.camera.getH()
        second_dist = abs(avatar_h - self.tb.base.camera.getH())
        #print('dist 1', first_dist)
        #print('dist 2', second_dist)
        # should be pretty close
        self.assertTrue(abs(first_dist - second_dist) < 0.2)

    def tearDown(self):
        self.clear_collisions()


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
        # make it so random selections never go out to 22, which is possible
        # in the game, but screws up tests, since can't move in one direction
        # from that point.
        self.tb.all_random_selections = [[2, 4, 6, 8, 10, 12, 14, 16, 18, 20]]
        self.tb.current_choice = 0
        # this will reset x_mag to zero, clearing any joystick pushes,
        # as well resetting other things
        self.tb.reset_variables()
        # make sure at correct training level
        #self.tb.set_level_variables(2)
        # reset banana - this is often done in the test, if we want
        # to ensure a certain direction, but not necessarily
        self.tb.restart_bananas()
        self.start = time.time()

    def test_move_to_opposite_side(self):
        camera_h = self.tb.base.camera.getH()
        self.move_to_opposite_side()
        camera_h_2 = self.tb.base.camera.getH()
        #print(camera_h, camera_h_2)
        #print camera_h + camera_h_2
        self.assertTrue(camera_h + camera_h_2 < 0.5)

    def test_get_reward_when_over_crosshair_required_amount_of_time(self):
        messenger.send('x_axis', [6 * self.tb.multiplier])
        while self.tb.collHandler.getNumEntries() == 0:
            taskMgr.step()
            start = time.time()
        messenger.send('x_axis', [0])
        while not self.tb.yay_reward:
            taskMgr.step()
        finish = time.time()
        #print finish - start
        #print self.tb.hold_aim
        self.assertTrue(finish - start >= self.tb.hold_aim)

    def test_no_reward_when_over_crosshair_less_than_required_amount_of_time(self):
        messenger.send('x_axis', [6 * self.tb.multiplier])
        while self.tb.collHandler.getNumEntries() == 0:
            taskMgr.step()
            start = time.time()
        # go for slightly less time than hold_aim, and make sure no reward
        messenger.send('x_axis', [0])
        while time.time() - start < self.tb.hold_aim - 0.01:
            taskMgr.step()
            self.assertFalse(self.tb.yay_reward)

    def test_allowed_to_go_past_banana(self):
        """
         test that even if we move past the banana, the camera continues
         to move, true if require_aim is True, training 2.4 and higher
        """
        #print 'go past banana'
        # get to zero, then try to go a few steps further
        messenger.send('x_axis', [6 * self.tb.multiplier])
        camera_h = self.tb.base.camera.getH()
        #print camera_h
        # okay, go past center. let's just go to the same
        # distance on the other side as where we started.
        # make this happen quickish
        wrong_speed = self.tb.wrong_speed
        self.tb.wrong_speed = self.tb.initial_speed
        if self.tb.multiplier > 0:
            while self.tb.base.camera.getH() > -camera_h:
                taskMgr.step()
        else:
            while self.tb.base.camera.getH() < -camera_h:
                taskMgr.step()

        # make sure we were able to go past. if original camera was positive,
        # heading should now be negative, and vise-versa.
        #print self.tb.base.camera.getH()
        if camera_h > 0:
            self.assertTrue(self.tb.base.camera.getH() < 0)
        else:
            self.assertTrue(self.tb.base.camera.getH() > 0)

    def test_max_speed_slows_down_direction_away_from_banana_after_passing_banana(self):
        """
        test that after we go past the banana, we go slower, if we continue in same direction
        only true for this level
        """
        if self.tb.training == 2.5:
            before = self.tb.base.camera.getH()
            # timing not great right out of the starting gate...
            messenger.send('x_axis', [0])
            for i in range(30):
                taskMgr.step()
            messenger.send('x_axis', [2 * self.tb.multiplier])
            camera_h = self.tb.base.camera.getH()
            #print camera_h
            for i in range(30):
                taskMgr.step()
            #print self.tb.base.camera.getH()
            first_dist = abs(camera_h - self.tb.base.camera.getH())
            print('dist', first_dist)
            #print 'first test over'
            #print('camera head', self.tb.base.camera.getH())
            # okay, go past center. let's just go to the same
            # distance on the other side as where we started.
            self.move_to_opposite_side(before)
            # and now we can test moving again, fist send a zero,
            # to reset speed.
            messenger.send('x_axis', [0])
            taskMgr.step()
            # now return to our regularly scheduled program
            messenger.send('x_axis', [2 * self.tb.multiplier])
            # and now we can test moving again, first send 2 steps,
            # this puts us starting at the same slow_factor as for
            # the first run
            taskMgr.step()
            taskMgr.step()
            avatar_h = self.tb.base.camera.getH()
            #print avatar_h
            for i in range(30):
                taskMgr.step()
            #print self.tb.base.camera.getH()
            second_dist = abs(avatar_h - self.tb.base.camera.getH())
            print('dist2', second_dist)
            # first speed should be faster than second, so go greater
            # distance in first test
            # should be at least twice the distance
            print('dist2/dist', second_dist / first_dist)
            self.assertTrue(first_dist / second_dist > 2)
            return lambda func: func
        return unittest.skip('skipped test, training != 2.5')

    def test_max_speed_remains_same_in_direction_towards_banana_after_passing_banana(self):
        """
        test that after we go past the banana, we go same speed, if we turn back towards banana
        """
        before = self.tb.base.camera.getH()
        # timing not great right out of the starting gate...
        messenger.send('x_axis', [0])
        for i in range(30):
            taskMgr.step()
        messenger.send('x_axis', [2 * self.tb.multiplier])
        camera_h = self.tb.base.camera.getH()
        #print camera_h
        for i in range(30):
            taskMgr.step()
        #print self.tb.base.camera.getH()
        first_dist = abs(camera_h - self.tb.base.camera.getH())
        print('dist', first_dist)
        #print 'first test over'
        #print('camera head', self.tb.base.camera.getH())
        # okay, go past center. let's just go to the same
        # distance on the other side as where we started.
        self.move_to_opposite_side(before)
        # and now we can test moving again, fist send a zero,
        # to reset speed.
        print 'back'
        messenger.send('x_axis', [0])
        print self.tb.speed
        taskMgr.step()
        print self.tb.speed
        # now we switch directions to test direction towards center
        messenger.send('x_axis', [2 * -self.tb.multiplier])
        # and now we can test moving again, first send 2 steps,
        # this puts us starting at the same slow_factor as for
        # the first run
        taskMgr.step()
        taskMgr.step()
        avatar_h = self.tb.base.camera.getH()
        print avatar_h
        for i in range(30):
            taskMgr.step()
        print self.tb.base.camera.getH()
        second_dist = abs(avatar_h - self.tb.base.camera.getH())
        print('dist', second_dist)
        # should be a small difference
        self.assertTrue(abs(first_dist - second_dist) < 0.2)

    def test_speed_returns_to_normal_after_reward_if_slowed(self):
        """
        test that after we get our reward, speed returns to normal.

        """
        before = self.tb.base.camera.getH()
        # timing not great right out of the starting gate...
        messenger.send('x_axis', [0])
        for i in range(30):
            taskMgr.step()
        messenger.send('x_axis', [2 * self.tb.multiplier])
        camera_h = self.tb.base.camera.getH()
        #print camera_h
        # test before reward:
        for i in range(30):
            #print('i', i)
            taskMgr.step()
        #print self.tb.base.camera.getH()
        first_dist = abs(camera_h - self.tb.base.camera.getH())
        print('dist', first_dist)
        print 'first test over'
        #print('camera head', self.tb.base.camera.getH())
        # okay, go past center. let's just go to the same
        # distance on the other side as where we started.
        self.move_to_opposite_side(before)
        #print('camera head', self.tb.base.camera.getH())
        # and now we can test moving again, first send a zero,
        # to reset speed.
        messenger.send('x_axis', [0])
        taskMgr.step()
        # next we need to test speed to make sure we slowed down,
        # so continue in same direction we were going
        messenger.send('x_axis', [2 * self.tb.multiplier])
        # first send 2 steps,
        # this puts us starting at the same slow_factor as for
        # the first run
        taskMgr.step()
        taskMgr.step()
        avatar_h = self.tb.base.camera.getH()
        #print avatar_h
        for i in range(30):
            taskMgr.step()
        #print self.tb.base.camera.getH()
        second_dist = abs(avatar_h - self.tb.base.camera.getH())
        print('dist2', second_dist)
        print 'dist2 should be much smaller than dist'
        # second speed should be slow
        # now go back to center and collect reward
        self.move_to_center_without_using_reward()
        # get reward
        messenger.send('x_axis', [0])
        taskMgr.step()
        #print self.tb.reward_count
        while self.tb.reward_count < self.tb.num_beeps:
            taskMgr.step()
        #print 'reward'
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
        #print avatar_f
        #print 'test again'
        for i in range(30):
            #print('i', i)
            taskMgr.step()
        #print self.tb.base.camera.getH()
        third_dist = abs(avatar_h - self.tb.base.camera.getH())
        print 'dist and dist3 should be close to same'
        print('dist3', third_dist)
        # second dist should be much shorter than first
        # at least half the dist, if we are slowing down
        # (not 2.6 or higher)
        if self.tb.training == 2.5:
            self.assertTrue(first_dist / second_dist > 2)
        # but the third and first should be close to the same
        self.assertTrue(abs(first_dist - third_dist) < 0.2)

    def test_speed_still_normal_after_reward(self):
        """
        test that after we get our reward, speed returns to normal.

        """
        # in case we are training right next to the edge of the screen
        while self.tb.base.camera.getH() > 21:
            self.tb.restart_bananas()
        # timing not great right out of the starting gate...
        messenger.send('x_axis', [0])
        for i in range(30):
            taskMgr.step()
        messenger.send('x_axis', [2 * self.tb.multiplier])
        camera_h = self.tb.base.camera.getH()
        print camera_h
        for i in range(30):
            #print('i', i)
            taskMgr.step()
        print self.tb.base.camera.getH()
        first_dist = abs(camera_h - self.tb.base.camera.getH())
        print('dist', first_dist)
        #print 'first test over'
        print('camera head', self.tb.base.camera.getH())
        #go to center
        # use not reward method, cause we would go right past center
        # if we were looking for reward.
        self.move_to_center_without_using_reward()
        print('camera head', self.tb.base.camera.getH())
        # stay in center to get reward
        messenger.send('x_axis', [0])
        taskMgr.step()
        while self.tb.reward_count < self.tb.num_beeps:
            taskMgr.step()
        print 'should have gotten reward'
        # now step until banana has been reset
        while not self.tb.moving:
            taskMgr.step()
        print self.tb.base.camera.getH()
        # and now we can test moving again, first send two steps,
        # this puts us starting at the same slow_factor as for
        # the first run
        taskMgr.step()
        taskMgr.step()
        messenger.send('x_axis', [2 * -self.tb.multiplier])
        avatar_h = self.tb.base.camera.getH()
        print avatar_h
        #print 'test again'
        for i in range(30):
            #print('i', i)
            taskMgr.step()
        print self.tb.base.camera.getH()
        second_dist = abs(avatar_h - self.tb.base.camera.getH())
        print('dist', second_dist)
        # speeds should be pretty close, so distances should be close
        self.assertTrue(abs(first_dist - second_dist) < 0.2)

    def tearDown(self):
        print('time this one took', time.time() - self.start)
        self.clear_collisions()


class TrainingBananaTestsT2_6(TrainingBananaTestsT2_5, unittest.TestCase):
    """Training 2.6, subject has to line up crosshair to banana (not go past)
    for min. time, does not slow down if goes past banana, both directions allowed
    """

    @classmethod
    def setUpClass(cls):
        loadPrcFileData("", "window-type offscreen")
        #print 'about to load world'
        training = 2.6
        cls.tb = TrainingBananas()
        cls.tb.set_level_variables(training)
        # make defaults so stuff tests as fast as possible, overrides config file
        cls.tb.reward_time = 0.01
        cls.tb.num_beeps = 1
        cls.tb.avatar_h = 1.5

    def setUp(self):
        # make it so random selections never go out to 22, which is possible
        # in the game, but screws up tests, since can't move in one direction
        # from that point.
        #self.tb.all_random_selections = [[2, 4, 6, 8, 10, 12, 14, 16, 18, 20]]
        self.tb.all_random_selections = [[20]]
        self.tb.current_choice = 0
        # this will reset x_mag to zero, clearing any joystick pushes,
        # as well resetting other things
        self.tb.reset_variables()
        # make sure at correct training level
        #self.tb.set_level_variables(2)
        # reset banana - this is often done in the test, if we want
        # to ensure a certain direction, but not necessarily
        self.tb.restart_bananas()
        self.start = time.time()

    def test_max_speed_does_not_slow_down_after_passing_banana(self):
        """
        test that after we go past the banana, we continue at same speed.
        """
        before = self.tb.base.camera.getH()
        # timing not great right out of the starting gate...
        messenger.send('x_axis', [0])
        for i in range(30):
            taskMgr.step()
        messenger.send('x_axis', [2 * self.tb.multiplier])
        camera_h = self.tb.base.camera.getH()
        #print camera_h
        for i in range(30):
            taskMgr.step()
        #print self.tb.base.camera.getH()
        first_dist = abs(camera_h - self.tb.base.camera.getH())
        print('dist', first_dist)
        #print 'first test over'
        #print('camera head', self.tb.base.camera.getH())
        # okay, go past banana. let's just go to the same place
        # on the other side
        self.move_to_opposite_side(before)
        # and now we can test moving again, first send a zero,
        # to reset speed.
        messenger.send('x_axis', [0])
        taskMgr.step()
        # now return to our regularly scheduled program
        messenger.send('x_axis', [2 * self.tb.multiplier])
        # first send 2 steps,
        # this puts us starting at the same slow_factor as for
        # the first run
        taskMgr.step()
        taskMgr.step()
        avatar_h = self.tb.base.camera.getH()
        #print avatar_h
        for i in range(30):
            taskMgr.step()
        #print self.tb.base.camera.getH()
        second_dist = abs(avatar_h - self.tb.base.camera.getH())
        print('dist', second_dist)
        # we should not change speeds as we pass the banana,
        # and therefor distances should be relatively close
        self.assertTrue(abs(first_dist - second_dist) < 0.2)

    def tearDown(self):
        print('time this one took', time.time() - self.start)
        self.clear_collisions()


class TrainingBananaTestsT3(unittest.TestCase):
    """Training 3, subject has to run forward into the banana
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
        #print before
        messenger.send('y_axis', [-2])
        # have to step twice, can't move on the first frame
        taskMgr.step()
        taskMgr.step()
        # should have moved
        after = self.tb.base.camera.getPos()
        #print('after', after)
        self.assertNotEqual(before, after)

    def test_cannot_move_backward(self):
        # test can now move forward
        before = self.tb.base.camera.getPos()
        print('before', before)
        messenger.send('y_axis', [2])
        # have to step twice, can't move on the first frame
        taskMgr.step()
        taskMgr.step()
        # should not have moved
        after = self.tb.base.camera.getPos()
        #print('after', after)
        self.assertEqual(before, after)

    def test_gets_reward_when_run_into_banana(self):
        messenger.send('y_axis', [-2])
        #print self.tb.base.camera.getPos()[1]
        last_pos = self.tb.base.camera.getPos()[1]
        taskMgr.step()
        taskMgr.step()
        #print last_pos
        # keep going until camera stops moving forward
        while self.tb.base.camera.getPos()[1] > last_pos:
            last_pos = self.tb.base.camera.getPos()[1]
            taskMgr.step()
        #print self.tb.base.camera.getPos()[1]
        self.assertTrue(self.tb.yay_reward)

    def test_avatar_returns_to_same_spot_after_collision(self):
        messenger.send('y_axis', [-2])
        #print self.tb.base.camera.getPos()[1]
        last_pos = self.tb.base.camera.getPos()[1]
        taskMgr.step()
        taskMgr.step()
        #print last_pos
        # keep going until reward
        while not self.tb.yay_reward:
            taskMgr.step()
        #print 'reward'
        # let go of joystick
        messenger.send('y_axis', [0])
        # now go until ban on moving is lifted
        while not self.tb.moving:
            taskMgr.step()
        new_pos = self.tb.base.camera.getPos()[1]
        self.assertEqual(last_pos, new_pos)

    def tearDown(self):
        # need to clear collisions, if some have happened, but haven't been
        # checked yet (ended trial before reward)
        self.tb.restart_bananas()
        taskMgr.step()
        self.tb.check_banana()


class TrainingBananaTestsT3_1(TrainingBananaTestsT3, unittest.TestCase):
    """Training 3, subject has to run forward into the banana, must let go
    of joystick to start new trial
    """

    @classmethod
    def setUpClass(cls):
        loadPrcFileData("", "window-type offscreen")
        #print 'about to load world'
        training = 3.1
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

    def test_does_not_start_next_trial_if_holding_joystick(self):
        messenger.send('y_axis', [-2])
        #print self.tb.base.camera.getPos()[1]
        taskMgr.step()
        taskMgr.step()
        #print last_pos
        # keep going until reward
        while not self.tb.yay_reward:
            taskMgr.step()
        #print 'reward'
        last_pos = self.tb.base.camera.getPos()[1]
        # continue to push joystick for a while, and
        # see if we go anywhere
        for i in range(50):
            taskMgr.step()
        new_pos = self.tb.base.camera.getPos()[1]
        self.assertEqual(last_pos, new_pos)

    def tearDown(self):
        # need to clear collisions, if some have happened, but haven't been
        # checked yet (ended trial before reward)
        self.tb.restart_bananas()
        taskMgr.step()
        self.tb.check_banana()


class TrainingBananaTestsKeys(unittest.TestCase):

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
        # choose a random start level
        level_range = random.choice(range(len(self.tb.levels_available)))
        if len(self.tb.levels_available[level_range]) > 1:
            level = random.choice(self.tb.levels_available[level_range])
        else:
            level = self.tb.levels_available[level_range][0]
        self.tb.set_level_variables(level)
        # make sure training level is set
        self.tb.restart_bananas()
        #print 'end setup'

    def test_move_using_right_arrow_key(self):
        """
        test that using the right arrow to the right moves the banana
        from the right towards the crosshair in the center, if
        trainingDirection is right
        """
        # check this for levels allowed to move both directions,
        # since we just want to know if we can move it, not checking
        # conditions for different levels here, so lets do level 2.4
        self.tb.set_level_variables(2.4)
        self.tb.restart_bananas()
        before = self.tb.base.camera.getH()
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
        # moving to the right, always means numbers getting smaller,
        # regardless of starting position
        after = self.tb.base.camera.getH()
        #print after
        self.assertTrue(after < before)

    def test_move_using_left_arrow_key(self):
        """
        test that moving the joystick to the left moves the banana
        from the left towards the crosshair in the center, if
        trainingDirection is left
        """
        # check this for levels allowed to move both directions,
        # since we just want to know if we can move it, not checking
        # conditions for different levels here, so lets do level 2.4
        self.tb.set_level_variables(2.4)
        self.tb.restart_bananas()
        before = self.tb.base.camera.getH()
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
        # moving to the left, always means numbers getting larger,
        # regardless of starting position
        after = self.tb.base.camera.getH()
        #print after
        self.assertTrue(after > before)

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

    def test_e_increases_banana_distance(self):
        """
        test that e key increases the distance from banana to crosshair
        """
        # this test only makes sense when doing manual bananas, level 2 or 2.1
        # right is positive multiplier
        training = random.choice([2, 2.1])
        self.tb.set_level_variables(training)
        self.tb.restart_bananas()
        before = abs(self.tb.base.camera.getH())
        #print before
        messenger.send('e')
        self.tb.restart_bananas()
        # should be further out now
        after = abs(self.tb.base.camera.getH())
        #print after
        # if at max distance, won't work
        if self.tb.avatar_h > self.tb.max_angle:
            self.assertTrue(after == before)
        else:
            self.assertTrue(after > before)

    def test_d_decreases_banana_distance(self):
        """
        test that d key decreases the distance from banana to crosshair
        """
        # this test only makes sense when doing manual bananas, level 2 or 2.1
        training = random.choice([2, 2.1])
        self.tb.set_level_variables(training)
        self.tb.restart_bananas()
        before = abs(self.tb.base.camera.getH())
        #print before
        messenger.send('d')
        self.tb.restart_bananas()
        after = abs(self.tb.base.camera.getH())
        # if at min distance, won't work
        if self.tb.avatar_h < self.tb.min_angle:
            self.assertTrue(after == before)
        else:
            self.assertTrue(after < before)

    def test_t_increases_training_level(self):
        """
        test that t key increases the training level
        """
        before = self.tb.training
        messenger.send('t')
        self.tb.restart_bananas()
        # if at highest level, should stay at same level
        if before == self.tb.levels_available[-1][-1]:
            self.assertTrue(self.tb.training == before)
        else:
            self.assertTrue(self.tb.training > before)

    def test_g_decreases_training_level(self):
        """
        test that g key decreases the training level
        """
        before = self.tb.training
        #print before
        messenger.send('g')
        self.tb.restart_bananas()
        # can't go below lowest level
        after = self.tb.training
        #print after
        if before == self.tb.levels_available[0][0]:
            self.assertTrue(after == before)
        else:
            self.assertTrue(after < before)

    def test_y_increases_speed_in_direction_opposite_to_banana(self):
        """
        test that if we press y key, speed in direction opposite to banana
        increases
        """
        # using y and h keys basically let you switch from 2.3 to 2.4
        # in a continuous fashion. Works only from 2.3
        training = 2.3
        self.tb.set_level_variables(training)
        self.tb.restart_bananas()
        # check initial speed
        initial_speed = self.tb.wrong_speed
        # first two frames get messed up for timing, so go two steps
        #print self.tb.free_move
        taskMgr.step()
        taskMgr.step()
        messenger.send('x_axis', [2 * -self.tb.multiplier])
        camera_h = self.tb.base.camera.getH()
        #print('wrong speed', self.tb.wrong_speed)
        #print camera_h
        # go a few steps, see how long it takes
        start = time.time()
        for i in range(30):
            #print self.tb.speed
            taskMgr.step()
        first_time = time.time() - start
        first_dist = camera_h - self.tb.base.camera.getH()
        #print('dist', first_dist)
        first_speed = abs(first_dist/first_time)
        # now change speed
        messenger.send('y')
        # have to reset for it to go into effect
        self.tb.restart_bananas()
        taskMgr.step()
        taskMgr.step()
        messenger.send('x_axis', [2 * -self.tb.multiplier])
        avatar_h = self.tb.base.camera.getH()
        #print avatar_h
        start = time.time()
        for i in range(30):
            #print self.tb.speed
            taskMgr.step()
        second_time = time.time() - start
        #print('time', second_time)
        #print('wrong speed', self.tb.wrong_speed)
        #print self.tb.base.camera.getH()
        second_dist = avatar_h - self.tb.base.camera.getH()
        #print('dist', second_dist)
        second_speed = abs(second_dist / second_time)
        #print('first', first_speed)
        #print('second', second_speed)
        # if wrong_speed was already the same as the speed in the opposite direction,
        # verify speed is actually the same
        if initial_speed == 1:
            self.assertAlmostEqual(first_speed, second_speed)
        else:
            self.assertTrue(first_speed < second_speed)

    def test_h_decreases_speed_in_direction_opposite_to_banana(self):
        """
        test that if we press h key, speed in direction opposite to banana
        decreases
        """
        # using y and h keys basically let you switch from 2.3 to 2.4
        # in a continuous fashion. Works only from 2.3
        training = 2.3
        self.tb.set_level_variables(training)
        self.tb.restart_bananas()
        # check initial speed
        #print('wrong speed', self.tb.wrong_speed)
        # first two frames get messed up for timing, so go two steps
        #print self.tb.free_move
        taskMgr.step()
        taskMgr.step()
        messenger.send('x_axis', [2 * -self.tb.multiplier])
        camera_h = self.tb.base.camera.getH()
        #print camera_h
        # go a few steps, see how long it takes
        start = time.time()
        for i in range(30):
            #print self.tb.x_mag
            #print self.tb.speed
            taskMgr.step()
        first_time = time.time() - start
        #print('time', first_time)
        first_dist = camera_h - self.tb.base.camera.getH()
        #print('dist', first_dist)
        first_speed = abs(first_dist/first_time)
        # now change speed
        messenger.send('h')
        # have to reset for it to go into effect
        self.tb.restart_bananas()
        #print('wrong speed', self.tb.wrong_speed)
        taskMgr.step()
        taskMgr.step()
        messenger.send('x_axis', [2 * -self.tb.multiplier])
        avatar_h = self.tb.base.camera.getH()
        #print avatar_h
        start = time.time()
        for i in range(30):
            #print self.tb.x_mag
            #print self.tb.speed
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

    def test_u_increases_choice_of_random_list(self):
        """
        test that u key increases the random list.
        """
        # only makes sense for random levels, 2.2 and greater,
        # randomly choose one
        training = random.choice(self.tb.levels_available[0][1:])
        # usually set to start at the first random list, so change it
        # to a random one
        self.tb.set_level_variables(training)
        self.tb.current_choice = random.choice(range(len(self.tb.all_random_selections)))
        # if changing the random list, need to re-run reset_variables
        self.tb.reset_variables()
        #print self.tb.all_random_selections
        #print 'restart bananas'
        self.tb.restart_bananas()
        # what list are we on now?
        list_no = self.tb.current_choice
        #print list_no
        #print self.tb.random_choices
        #print len(self.tb.all_random_selections)
        # increase it here, if there are more lists to be had...
        if list_no < len(self.tb.all_random_selections) - 1:
            #print 'less than max in test'
            list_no += 1
        # increase it in game
        #print list_no
        messenger.send('u')
        self.tb.restart_bananas()
        #print('test says', self.tb.all_random_selections[list_no])
        #print('list_no', list_no)
        #print self.tb.random_choices
        self.assertEqual(self.tb.all_random_selections[list_no], self.tb.random_choices)

    def test_j_decreases_choice_of_random_list(self):
        """
        test that u key increases the random list.
        """
        # only makes sense for random levels, 2.2 and greater,
        # randomly choose one
        training = random.choice(self.tb.levels_available[0][1:])
        # usually set to start at the first random list, so change it
        # to a random one
        self.tb.current_choice = random.choice(range(len(self.tb.all_random_selections)))
        self.tb.set_level_variables(training)
        self.tb.restart_bananas()
        # what list are we on now?
        list_no = self.tb.current_choice
        #print self.tb.all_random_selections[list_no]
        # increase it here, checking already not zero
        if list_no is not 0:
            list_no -= 1
        #print self.tb.all_random_selections[list_no]
        # increase it in game
        messenger.send('j')
        self.tb.restart_bananas()
        self.assertEqual(self.tb.all_random_selections[list_no], self.tb.random_choices)

    def test_l_changes_banana_to_left_side(self):
        """
        test that l key changes the direction the subject is going to left
        """
        # only makes sense when in manual mode, training 2 or 2.1
        training = random.choice([2, 2.1])
        # set initial direction to right (positive)
        self.tb.new_dir = 1
        self.tb.set_level_variables(training)
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
        # only makes sense when in manual mode, training 2 or 2.1
        training = random.choice([2, 2.1])
        # set initial direction to left (negative)
        self.tb.new_dir = -1
        self.tb.set_level_variables(training)
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
        this only makes sense in some training step I have not created yet.
        """
        #### THIS TEST IS NOT TESTING ANYTHING YET!!!!
        # left is negative multiplier
        self.tb.multiplier = -1
        self.tb.restart_bananas()
        #before = self.tb.base.camera.getH()
        #print before
        messenger.send('f')
        self.tb.restart_bananas()
        # should be on left side now

    def test_space_bar_gives_reward(self):
        messenger.send('space')
        # if delay is in effect, gave reward
        self.assertTrue(self.tb.delay_start)

    def tearDown(self):
        # need to clear collisions, if some have happened, but haven't been
        # checked yet (ended trial before reward)
        self.tb.restart_bananas()
        taskMgr.step()
        self.tb.check_banana()


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
        suite = []
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
            suite = unittest.TestLoader().loadTestsFromTestCase(TrainingBananaTestsT2_5)
        elif int(sys.argv[1]) == 6:
            suite = unittest.TestLoader().loadTestsFromTestCase(TrainingBananaTestsT2_6)
        elif int(sys.argv[1]) == 7:
            suite = unittest.TestLoader().loadTestsFromTestCase(TrainingBananaTestsT3)
        elif int(sys.argv[1]) == 8:
            suite = unittest.TestLoader().loadTestsFromTestCase(TrainingBananaTestsT3_1)
        elif int(sys.argv[1]) == 9:
            suite = unittest.TestLoader().loadTestsFromTestCase(TrainingBananaTestsKeys)
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