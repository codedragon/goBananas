from __future__ import with_statement
import unittest
import os
import shutil
import datetime
import platform
# Do not import pandaepl or it will start pandaepl without any of our parameters.
from pandaepl import Conf

class initGoBananasTests(unittest.TestCase):
    def setUp(self):
        print 'setup'
        #if platform.system() == 'Darwin':
        os.system('ppython goBananas.py -sTest --no-eeg --no-fs')
        #else:
        #    os.system('python goBananas.py -sTest --no-eeg --no-fs')
        self.session = "data/Test/session_" + datetime.datetime.now().strftime("%y_%m_%d_%H_%M")

    def check_log(self, log_word):
        """ Check the log file to see if logWord is present,
        returns line where logWord is found
        """
        log_name = self.session + '/log.txt'
        line = []
        with open(log_name) as logfile:
            for line in logfile:
                if log_word in line.split():
                    break
            return line

    def test_one(self):
        """ goBananas should make a new session in the data directory,
        session should be today's date """
        print self.session
        self.failUnless(os.access(self.session, os.F_OK))

    def test_two(self):
        """ load the config directory
		"""
        self.assertTrue(self.check_log('CONF_LOAD'))

    def test_three(self):
        """ check that custom logging working
		"""
        self.assertTrue(self.check_log('YUMMY'))

    def test_four(self):
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

    def tearDown(self):
        print 'teardown'
        print os.getcwd()
        #shutil.rmtree(self.session)

if __name__ == "__main__":
    unittest.main()



