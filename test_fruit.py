import unittest
from fruit import Fruit, check_repeat, create_alt_fruit_area


class FruitTests(unittest.TestCase):

    def test_check_repeat_first_trial_normal(self):
        # if first trial, not choosing next repeat trial, so the list should stay
        # the same. trial_type should be empty string, since neither new nor repeat.
        repeat_number = 3
        trial_number = 0
        # initial_list is [size of set, repeat trial, next time to repeat]
        initial_list = [10, repeat_number, repeat_number]
        new_list, trial_type = check_repeat(trial_number, initial_list)
        self.assertEquals(new_list, initial_list)
        self.assertEquals(trial_type, '')

    def test_check_repeat_first_trial_save(self):
        # if first trial, not choosing next repeat trial, so the list should stay
        # the same. trial_type should be 'new', since we are saving this trial.
        repeat_number = 0
        trial_number = 0
        # initial_list is [size of set, repeat trial, next time to repeat]
        initial_list = [10, repeat_number, repeat_number]
        new_list, trial_type = check_repeat(trial_number, initial_list)
        self.assertEquals(new_list, initial_list)
        self.assertEquals(trial_type, 'new')

    def test_check_repeat_second_block_choose(self):
        # choosing next repeat trial, so the list should not stay
        # the same. trial_type may be 'repeat' if trial_num is the
        # same as initial_list[2] or '' if not. I don't think we can
        # get around the conditional, since the initial_list[2] number
        # is randomly chosen
        repeat_number = 7
        trial_number = 10
        # initial_list is [size of set, repeat trial, next time to repeat]
        initial_list = [10, repeat_number, repeat_number]
        new_list, trial_type = check_repeat(trial_number, initial_list)
        self.assertNotEquals(new_list, initial_list)
        if trial_number == new_list[2]:
            self.assertEquals(trial_type, 'repeat')
        else:
            self.assertEquals(trial_type, '')

    # things to test for recall trials:
    # manual/random
    # whole area/subarea
    # random only: repeat/not repeat
    # alpha/invisible

    def test_recall_first_correct_trials_bright(self):
        # want to test this for manual and random
        config = {'fruit_to_remember': 'banana', 'manual': True, 'subarea': 2,
                  'alpha': 0.3, 'num_repeat_visible': 2, 'first_fruit_alpha': True}

        fruit = Fruit(config)
        fruit.pos_dict = {}
        for i in range(config['num_repeat_visible'] + 3):
            # print('key', fruit.new_subarea_key)
            # print('manual', fruit.manual)
            remember, trial_type = fruit.setup_recall_trial(i)
            # print remember, trial_type
            # fake what we do in setup_fruit_for_recall_trial
            if i == 0:
                fruit.pos_dict['foo'] = 1  # fake that we are saving
                fruit.new_subarea_key = None  # no more moving
                self.assertEquals(trial_type, 'manual_bright')
            elif i < config['num_repeat_visible']:
                self.assertEquals(trial_type, 'repeat_bright')
            elif i == config['num_repeat_visible']:
                self.assertEquals(trial_type, 'repeat_alpha')
            else:
                self.assertEquals(trial_type, 'repeat')

if __name__ == "__main__":
    unittest.main(verbosity=2)