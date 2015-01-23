import unittest
from fruit import Fruit, check_repeat, create_alt_fruit_area
import random


class FruitTests(unittest.TestCase):

    def test_check_repeat_first_trial_normal(self):
        # if first trial, not choosing next repeat trial, so the list should stay
        # the same. trial_type should be empty string, since neither new nor repeat.
        start_number = 3
        # initial_list is [size of set, saved trial, next]
        initial_list = [10, start_number, start_number]
        new_list, trial_type = check_repeat(0, initial_list)
        self.assertEquals(new_list, initial_list)
        self.assertEquals(trial_type, '')

    def test_check_repeat_first_trial_save(self):
        # if first trial, not choosing next repeat trial, so the list should stay
        # the same. trial_type should be 'new', since we are saving this trial.
        start_number = 0
        # initial_list is [size of set, saved trial, next]
        initial_list = [10, start_number, start_number]
        new_list, trial_type = check_repeat(0, initial_list)
        self.assertEquals(new_list, initial_list)
        self.assertEquals(trial_type, 'new')

    def test_check_repeat_second_block_choose(self):
        # choosing next repeat trial, so the list should not stay
        # the same. trial_type may be 'repeat' if trial_num is the
        # same as initial_list[2] or '' if not. I don't think we can
        # get around the conditional, since the initial_list[2] number
        # is randomly chosen
        start_number = 7
        # initial_list is [size of set, saved trial, next]
        initial_list = [10, start_number, start_number]
        print('repeat list', initial_list)
        new_list, trial_type = check_repeat(10, initial_list)
        print('repeat list', initial_list)
        print trial_type
        print 'ok'
        self.assertNotEquals(new_list, initial_list)
        if start_number == initial_list[2]:
            self.assertEquals(trial_type, 'repeat')
        else:
            self.assertEquals(trial_type, '')


if __name__ == "__main__":
    unittest.main(verbosity=2)