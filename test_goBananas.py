from __future__ import with_statement
import unittest
import os
import time
import datetime
import itertools
import moBananas as mb
import shutil
import sys
import platform
# Do not import pandaepl or goBananas or it will start pandaepl without any of our parameters.
# from pandaepl import Conf
# from goBananas import distance
# import goBananas as gb


class TestGoBananas(unittest.TestCase):

    def setUp(self):
        print 'setup'
        if platform.system() == 'Darwin':
            print 'trying arch'
            os.system('arch -i386 ppython goBananas.py -sTest --no-eeg --no-fs')
            # WANT TO USE THE TEST CONFIGURATION FILE, I think. HOW DO I MAKE THIS HAPPEN?
            # MAYBE COPY THE CONFIG FILE
        else:
            os.system('python goBananas.py -sTest --no-eeg --no-fs')

        # Should figure out how to get this from exp.getSessionNum,
        # could be off by a minute, as is.
        self.session = "data/Test/session_" + datetime.datetime.now().strftime("%y_%m_%d_%H_%M")
        # make sure this is really the session number
        if not os.path.exists(self.session):
            # if not, try a minute earlier
            new_time = str(int(self.session[-2:]) - 1)
            # need to make sure new time is using 0n notation for numbers < 10
            if len(new_time) == 1:
                new_time = '0' + new_time
            self.session = self.session.replace('','')[:-2] + new_time
            print 'session problem, trying one minute earlier', self.session
            if not os.path.exists(self.session):
                print self.session
                raise Exception("Data file does not exist!")
        self.config = {}
        execfile('config.py', self.config)
        print self.session

    def test_session(self):
        """ goBananas should make a new session in the data directory,
        session should be today's date """
        print 'checking session', self.session
        time.sleep(0.3)
        print 'after sleep'
        self.failUnless(os.access(self.session, os.F_OK))
        print 'done?'

    def test_config(self):
        """ load the config directory
		"""
        self.assertTrue(self.check_log('CONF_LOAD'))

    def test_logging(self):
        """ check that custom logging working - checks for a new trial
		"""
        self.assertTrue(self.check_log('NewTrial'))

    def test_num_bananas(self):
        """Have correct number of bananas out
        """
        #config = {}
        #execfile('config.py',config)
        #print config['numBananas']
        #print 'banana{0}'.format(str(config['numBananas'] - 1))
        #last_banana = 'banana{0}'.format(str(config['numBananas'] - 1))
        #print last_banana
        self.assertTrue(self.check_log('banana' + "%02d" % self.config['numBananas'] - 1))
        #self.assertTrue(self.check_log('banana{0}'.format(str(self.config['numBananas'] - 1))))
        # should not have more bananas
        self.assertRaises(self.check_log('banana{0}'.format(str(self.config['numBananas']))))
        self.assertTrue(self.check_log('banana' + "%02d" % self.config['numBananas']))
        print 'banana' + '%02d' + 'should not have been found' % self.config['numBananas']

    def test_position_bananas(self):
        """
        Positions for all of the bananas. Should not be close together.
        """
        #config = {}
        #execfile('config.py', config)
        # check log if more than one banana, if running tests, numBananas in config not accurate
        if not self.check_log('banana01'):
            print 'Test aborted: Need more than one banana to test distance'
            return unittest.skip("Need more than one banana to test distance")
        plist = []
        for i in range(self.config['numBananas']):
            line = self.check_log('VROBJECT_POS', 'banana' + '%02d' % i)
            #print line
            temp = line.split()
            #print temp[-3][9:-1]
            #print temp[-2][:-1]
            plist += [(temp[-3][9:-1], temp[-2][:-1])]
        #print plist
        # need to compare the distance between all points.
        #distance = mb.distance(plist[0], plist[1])
        for p0, p1 in itertools.combinations(plist, 2):
            #print p0, p1
            distance = mb.distance(p0, p1)
            #print distance
            self.assertTrue(distance >= self.config['tooClose'])

    def test_banana_eaten_and_logged(self):
        self.assertTrue(self.check_log('Yummy'))

    def test_collect_eye_positions(self):
        self.assertTrue(self.check_log('EyeData'))

    def test_reward_logged(self):
        self.assertTrue(self.check_log('Beeps'))

    def test_reward_amount(self):
        # just check the first banana
        self.assertEqual(self.count_beeps(1)[0], self.config['numBeeps'])

    def test_double_reward_last_banana(self):
        # check last banana for extra reward
        num_bananas = self.config['numBananas']
        reward = self.config['numBeeps'] * self.config['extra']
        print reward
        [beeps, last] = self.count_beeps(num_bananas)
        print last
        self.assertTrue(last)
        self.assertTrue(reward == beeps)

    def tearDown(self):
        if sys.exc_info() == (None, None, None):
            print 'removing log file'
            shutil.rmtree(self.session)
        else:
            print sys.exc_info()
            print os.getcwd()
            print 'fail'


    def check_log(self, log_word, next_word=''):
        """ Help function for tests, will check the log
        file to see if logWord is present, returns the
        line where logWord is found, returns empty string
        if logWord not found, if next_word is given, will
        look for both strings in the same line.
        """
        #print log_word
        if next_word == '':
            next_word = log_word
            #print next_word
        log_name = self.session + '/log.txt'
        line = []
        with open(log_name) as logfile:
            for line in logfile:
                if log_word in line.split() and next_word in line.split():
                    return line
        print '%s not found' % log_word
        return ''

    def count_beeps(self, yum_n):
        """ Help function for tests, will check the log
            file to find Yummy n (yum_n), which is just the nth
            yummy in the file. So if yum_x = 2, finds the collision
            with the second banana, then checks the number of beeps
            between it and the next Yummy, and finally checks if there
            is a NewTrial entry before the next Yummy. Returns
            beeps, int, number of beeps between 2 Yummys, and
            new_trial, bool, True or False for whether that was
            last banana.
            """
        yummy = 1
        new_trial = False
        check = 0
        beeps = 0
        log_name = self.session + '/log.txt'
        line = []
        #print 'yum_n', yum_n
        with open(log_name) as logfile:
            for line in logfile:
                if 'Yummy' in line.split():
                    print 'found yummy', yummy
                    print 'yum_n', yum_n
                    if yummy == yum_n:
                        check = 1
                        print 'yummy we are looking for', yummy
                    elif yummy == yum_n + 1:
                        check = None
                        print 'okay, stop looking', yummy
                    yummy += 1
                    print 'check', check
                if check:
                    if 'Beeps' in line.split():
                        beeps += 1
                        print 'found a beep', beeps
                    if 'NewTrial' in line.split():
                        new_trial = True
                        print 'found a new trial'
                        return beeps, new_trial
                elif check is None:
                    return beeps, new_trial
        print 'ended'
        return beeps, new_trial

        print '%s not found' % log_word
        return ''

def suite_one():
    suite_one = unittest.TestSuite()
    suite_one.addTest(TestGoBananas("test_session"))
    return suite_one

if __name__ == "__main__":
    unittest.main(verbosity=2)
    #suite = unittest.TestLoader().loadTestsFromTestCase(TestGoBananas)
    #unittest.TextTestRunner(verbosity=2).run(suite_one())

# To run a single test:
# python test_goBananas.py TestGoBananas.test_last_banana
