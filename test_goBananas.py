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

    def check_log(self, log_word, next_word = ''):
        """ Check the log file to see if logWord is present,
        returns line where logWord is found
        """
        #print log_word
        #print next_word
        log_name = self.session + '/log.txt'
        line = []
        with open(log_name) as logfile:
            for line in logfile:
                if log_word in line.split() and next_word in line.split():
                    return line
        #print 'fail'
        return line

    def test_a(self):
        """ goBananas should make a new session in the data directory,
        session should be today's date """
        print self.session
        self.failUnless(os.access(self.session, os.F_OK))

    def test_b(self):
        """ load the config directory
		"""
        self.assertTrue(self.check_log('CONF_LOAD'))

    def test_c(self):
        """ check that custom logging working
		"""
        self.assertTrue(self.check_log('YUMMY'))

    def test_d(self):
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

    def test_e(self):
        """
        Positions for all of the bananas. Should not be close together.
        """
        tooClose = 1
        config = {}
        execfile('config.py', config)
        numBananas = config['numBananas']
        xlist = []
        ylist = []
        for i in range(numBananas):
            line = self.check_log('VROBJECT_POS','banana{0}'.format(str(i)))
            print line
            temp = line.split()
            xlist.append(temp[-3][9:-1])
            ylist.append(temp[-2][:-1])
        # need to compare the distance between all points.
            
        #while tmp:
        #for x,y in zip(xlist, ylist):






    def tearDown(self):
        print 'teardown'
        print os.getcwd()
        #shutil.rmtree(self.session)

if __name__ == "__main__":
    unittest.main()



