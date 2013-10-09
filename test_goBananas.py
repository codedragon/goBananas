import unittest
import os
import shutil
import datetime

class initGoBananasTests(unittest.TestCase):
	def setUp(self):
		print 'setup'
		os.system('python goBananas.py -sTest --no-eeg --no-fs')
		self.session = "data/Test/session_" + datetime.datetime.now().strftime("%y_%m_%d_%H_%M")

	def words(self, fileObj):
		for line in fileObj:
			for word in line.split():
				yield word

	def testOne(self):
		""" goBananas should make a new session in the data directory,
		session should be today's date """
		print self.session
		self.failUnless(os.access(self.session, os.F_OK))

	def testTwo(self):
		""" load the config directory
		"""
		log_name = self.session + '/log.txt'
		word = ''
		with open(log_name) as logfile:
			wordGen = self.words(logfile)
			for word in wordGen:
				if word == 'CONF_LOAD':
					break
		self.assertEqual(word, 'CONF_LOAD')

	def tearDown(self):
		print 'teardown'
		print os.getcwd()
		shutil.rmtree(self.session)

if __name__ == "__main__":
	unittest.main()
