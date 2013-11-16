from __future__ import with_statement
import unittest
import os
import time
import datetime
import itertools
import moBananas as mb
import shutil
import sys

# Do not import pandaepl or goBananas or it will start pandaepl without any of our parameters.
# from pandaepl import Conf
# from goBananas import distance
# import goBananas as gb


class TestGoBananas(unittest.TestCase):

    def setUp(self):
        print 'setup'
        #if platform.system() == 'Darwin':
        os.system('ppython goBananas.py -sTest --no-eeg --no-fs')
        #else:
        #    os.system('python goBananas.py -sTest --no-eeg --no-fs')
        self.session = "data/Test/session_" + datetime.datetime.now().strftime("%y_%m_%d_%H_%M")

    def test_session(self):
        """ goBananas should make a new session in the data directory,
        session should be today's date """
        print 'checking session', self.session
        time.sleep(0.3)
        self.failUnless(os.access(self.session, os.F_OK))

    def test_config(self):
        """ load the config directory
		"""
        self.assertTrue(self.check_log('CONF_LOAD'))

    def test_logging(self):
        """ check that custom logging working
		"""
        self.assertTrue(self.check_log('NewTrial'))

    def test_num_bananas(self):
        """Have correct number of bananas
        """
        config = {}
        execfile('config.py',config)
        #print config['numBananas']
        #last_banana = 'banana{0}'.format(str(config['numBananas'] - 1))
        #print last_banana
        self.assertTrue(self.check_log('banana{0}'.format(str(config['numBananas'] - 1))))
        # should not have more bananas
        self.assertRaises(self.check_log('banana{0}'.format(str(config['numBananas']))))

    def test_position_bananas(self):
        """
        Positions for all of the bananas. Should not be close together.
        """
        config = {}
        execfile('config.py', config)
        # check log if more than one banana, if running tests, numBananas in config not accurate
        if not self.check_log('banana01'):
            print 'Test aborted: Need more than one banana to test distance'
            return unittest.skip("Need more than one banana to test distance")
        plist = []
        for i in range(config['numBananas']):
            line = self.check_log('VROBJECT_POS','banana{0}'.format(str(i)))
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
            self.assertTrue(distance >= config['tooClose'])

    def test_banana_eaten_and_logged(self):
        print 'Please get one banana'
        self.assertTrue(self.check_log('YUMMY'))

    def test_collect_eye_positions(self):
        self.assertTrue(self.check_log('EyeData'))

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

def suite_one():
    suite_one = unittest.TestSuite()
    suite_one.addTest(TestGoBananas("test_session"))
    return suite_one

if __name__ == "__main__":
    unittest.main()
    #suite = unittest.TestLoader().loadTestsFromTestCase(TestGoBananas)
    #unittest.TextTestRunner(verbosity=2).run(suite_one())

# To run a single test:
# python test_goBananas.py TestGoBananas.test_last_banana