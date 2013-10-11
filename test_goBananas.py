import unittest
import os
import shutil
import datetime


class initGoBananasTests(unittest.TestCase):
    def setUp(self):
        print 'setup'
        os.system('python goBananas.py -sTest --no-eeg --no-fs')
        self.session = "data/Test/session_" + datetime.datetime.now().strftime("%y_%m_%d_%H_%M")

    def checkLog(self, logWord):
        """ Check the log file to see if logWord is present,
        returns line where logWord is found
        """
        log_name = self.session + '/log.txt'
        line = []
        with open(log_name) as logfile:
            for line in logfile:
                if logWord in line.split():
                    break
            return line

    def testOne(self):
        """ goBananas should make a new session in the data directory,
        session should be today's date """
        print self.session
        self.failUnless(os.access(self.session, os.F_OK))

    def testTwo(self):
        """ load the config directory
		"""
        self.assertIn('CONF_LOAD', self.checkLog('CONF_LOAD'))

    def testThree(self):
        """ check that custom logging working
		"""
        self.assertIn('YUMMY', self.checkLog('YUMMY'))

    def tearDown(self):
        print 'teardown'
        print os.getcwd()
        shutil.rmtree(self.session)

    if __name__ == "__main__":
        unittest.main()
