from pandaepl.common import *
#import os
import datetime

class goBananas:
	def __init__(self):
		"""
		Initialize the experiment
		"""
		# Get experiment instance.
		print 'init'
		exp = Experiment.getInstance()
		#exp.setSessionNum(0)
		# Set session to today's date
		exp.setSessionNum(datetime.datetime.now().strftime("%y_%m_%d_%H_%M"))

		config = Conf.getInstance().getConfig()  # Get configuration dictionary.
		print config['training']

		Experiment.getInstance().stop()

	def start(self):
		"""
		Start the experiment.
		"""
		print 'start'
		Experiment.getInstance().start()


if __name__ == '__main__':
	#print 'main?'
	goBananas().start()
else:
	#print 'not main?'
	#import argparse
	#p = argparse.ArgumentParser()
	#p.add_argument('-scrap')
	#import sys
	#sys.argv.extend(['stest'])
	#sys.argv = ['goBananas','-stest']
		#,'--no-eeg','--no-fs']
	goBananas().start()