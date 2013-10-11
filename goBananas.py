from pandaepl.common import *
import os
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

        # Get vr environment object
        vr = Vr.getInstance()

        # Initialize experiment parameters
        if not exp.getState():
            bananas = []
        # Get avatar object
        avatar = Avatar.getInstance()

        # Register Custom Log Entries
        #This one corresponds to colliding with a banana
        Log.getInstance().addType("YUMMY", [("BANANA", basestring)],
                                  False)

        VLQ.getInstance().writeLine("YUMMY", ['Started'])
        #Log.getInstance().addType("EyeData", [("X", float), ("Y", float)], False)
        #Log.getInstance().addType("NewTrial", [("Trial", int)], False)

        # Load environment
        self.loadEnvironment(config)

    def loadEnvironment(self, config):
        """
        Load terrain, sky, etc
        """
        # load terrain
        self.terrainModel = Model('terrain', config['terrainModel'], config['terrainCenter'])
        # When hitting an object that is part of the terrain, repel or slide?
        self.terrainModel.setCollisionCallback(MovingObject.handleRepelCollision)

        # load sky
        self.skyModel = Model("sky", config['skyModel'])
        self.skyModel.setScale(config['skyScale'])

        # Load palm tree.
        self.treeModel = Model("tree", config['treeModel'], config['treeLoc'])
        self.treeModel.setScale(config['treeScale'])

        # Load Skyscraper
        self.skyscraperModel = Model("skyscraper", config['skyScraperModel'], config['skyScraperLoc'])
        self.skyscraperModel.setScale(config['skyScraperScale'])

        # Load Streetlight
        self.streetlightModel = Model("streetlight", config['stLightModel'], config['stLightLoc'])
        self.streetlightModel.setScale(config['stLightScale'])

        # Load Windmill
        self.windmillModel = Model("windmill", config['windmillModel'], config['windmillLoc'])
        self.windmillModel.setScale(config['windmillScale'])
        self.windmillModel.setH(config['windmillH'])


        # Load bananas.
        self.bananaModels = []
        for i in range(0, config['numBananas']):
            bananaModel = Model("banana" + str(i),
                                os.path.join(config['bananaDir'], "banana" + ".bam"),
                                Point3(config['bananaLocs'][i][0],
                                       config['bananaLocs'][i][1],
                                       config['bananaZ']),
                                self.collideBanana)
            bananaModel.setScale(config['bananaScale'])
            self.bananaModels.append(bananaModel)
            self.bananaModels[i].setH(random.randint(0, 361))
            if config['training'] > 0:
                self.bananaModels[i].setStashed(1)

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