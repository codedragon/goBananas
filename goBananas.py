from direct.directbase.DirectStart import base
from pandaepl.common import *
#noinspection PyUnresolvedReferences
from panda3d.core import WindowProperties
import os
import datetime
import random
import moBananas as mb
# import PyDAQmx as daq
import pydaq

class GoBananas:
    def __init__(self):
        """
        Initialize the experiment
        """
        # Get experiment instance.
        #print 'init'
        exp = Experiment.getInstance()
        #exp.setSessionNum(0)
        # Set session to today's date
        exp.setSessionNum(datetime.datetime.now().strftime("%y_%m_%d_%H_%M"))

        config = Conf.getInstance().getConfig()  # Get configuration dictionary.
        #print config['training']
        #print 'load testing', config['testing']

        # get rid of cursor
        win_props = WindowProperties()
        win_props.setCursorHidden(True)
        base.win.requestProperties(win_props)

        # set up reward system
        if config['reward']:
            self.reward = pydaq.GiveReward()
        else:
            self.reward = None

        # Get vr environment object
        vr = Vr.getInstance()

        # Initialize experiment parameters
        #if not exp.getState():
            #bananas = []
            # Get avatar object
        #avatar = Avatar.getInstance()

        # Register Custom Log Entries
        #This one corresponds to colliding with a banana
        Log.getInstance().addType("YUMMY", [("BANANA", basestring)],
                                  False)
        Log.getInstance().addType("NewTrial", [("Trial", int)], False)
        #Log.getInstance().addType("EyeData", [("X", float), ("Y", float)], False)

        # First Trial
        self.trialNum = 1
        VLQ.getInstance().writeLine("NewTrial", [self.trialNum])

        # bring some configuration parameters into memory that we will
        # use often. also makes it possible to change these dynamically
        self.numBananas = config['numBananas']
        self.numBeeps = config['numBeeps']
        self.extra = config['extra']
        self.fullTurningSpeed = config['fullTurningSpeed']
        self.fullForwardSpeed = config['fullForwardSpeed']

        # initiate beeps
        self.beeps = None

        if config['eyeData']:
            self.gain = config['gain']
            self.offset = config['offset']

        # Load environment
        self.loadEnvironment(config)

        # Handle keyboard events
        #vr.inputListen('toggleDebug',
        #               lambda inputEvent:
        #               Vr.getInstance().setDebug(not Vr.getInstance().isDebug * ()))
        vr.inputListen("upTurnSpeed", self.upTurnSpeed)
        vr.inputListen("downTurnSpeed", self.downTurnSpeed)
        
        # set up task to be performed between frames
        vr.addTask(Task("checkReward",
                        lambda taskInfo:
                            self.checkReward(),
                        config['pulseInterval']))

    def loadEnvironment(self, config):
        """
        Load terrain, sky, etc
        """
        # load terrain
        # Model is a global variable from pandaepl
        self.terrainModel = Model('terrain', config['terrainModel'], config['terrainCenter'])
        # When hitting an object that is part of the terrain, repel or slide?
        self.terrainModel.setCollisionCallback(MovingObject.handleRepelCollision)
        #
        ## load sky
        self.skyModel = Model("sky", config['skyModel'])
        self.skyModel.setScale(config['skyScale'])
        #
        ## Load palm tree.
        self.treeModel = Model("tree", config['treeModel'], config['treeLoc'])
        self.treeModel.setScale(config['treeScale'])
        #
        ## Load Skyscraper
        self.skyscraperModel = Model("skyscraper", config['skyScraperModel'], config['skyScraperLoc'])
        self.skyscraperModel.setScale(config['skyScraperScale'])
        #
        ## Load Streetlight
        self.streetlightModel = Model("streetlight", config['stLightModel'], config['stLightLoc'])
        self.streetlightModel.setScale(config['stLightScale'])
        #
        ## Load Windmill
        self.windmillModel = Model("windmill", config['windmillModel'], config['windmillLoc'])
        self.windmillModel.setScale(config['windmillScale'])
        self.windmillModel.setH(config['windmillH'])

        # Load random Bananas
        if not config['testing']:
            #print 'random bananas'
            self.bananaModel = self.createBananas()
        else:
            # Show a couple of bananas where we define the positions for testing
            # also need to uncomment some banana parameters in config file
            bananaModels = []
            bananaModel = Model("banana0", config['bananaModel'], 
                                config['bananaLoc'])
            bananaModel.setScale(config['bananaScale'])
            bananaModel.setH(config['bananaH'])
            bananaModels.append(bananaModel)
            #
            bananaModel1 = Model("banana1", config['bananaModel'], 
                                 config['bananaLoc2'])
            bananaModel1.setScale(config['bananaScale'])
            bananaModel1.setH(config['bananaH'])
            #
            bananaModels.append(bananaModel1)
            self.bananaModel = bananaModels

    def createBananas(self):
        #print 'create bananas'
        # Randomly assign where bananas go and return a banana bananaModel.
        # get config dictionary
        # distance formula: ((x2 - x1)^2 + (y2 - y1)^2)^1/2
        # make sure distance is less than 0.5
        config = Conf.getInstance().getConfig()
        bananaModels = []
        #print 'numBananas', self.numBananas
        pList = []
        # get current position of avatar, so bananas not too close.
        avatar = Avatar.getInstance()
        avatarXY = (avatar.getPos()[0], avatar.getPos()[1])
        #print avatarXY
        for i in range(self.numBananas):
            (x, y) = mb.setXY(pList, avatarXY)
            #print point
            pList += [(x, y)]
            # Model is a global from pandaepl
            # Point3 is a global from Panda3d
            bananaModel = Model("banana" + "%02d" % i,
                                os.path.join(config['bananaDir'], 
                                "banana" + ".bam"),
                                Point3(x, y, 1),
                                self.collideBanana)
            bananaModel.setScale(config['bananaScale'])
            bananaModel.setH(random.randint(0, 361))
            bananaModels.append(bananaModel)
            # if true, object is removed from the environment, but not destroyed
            # so start with not stashed
            bananaModels[i].setStashed(False)
        self.stashed = self.numBananas
        #print 'end load bananas'
        #print pList
        return bananaModels

    def replenishBananas(self):
        pList = []
        avatar = Avatar.getInstance()
        avatarXY = (avatar.getPos()[0], avatar.getPos()[1])
        #print avatarXY
        for i in range(self.numBananas):
            (x, y) = mb.setXY(pList, avatarXY)
            self.bananaModel[i].setPos(Point3(x, y, 1))
            # make new bananas visible
            self.bananaModel[i].setStashed(False)
        # start count again
        self.stashed = self.numBananas

    def collideBanana(self, collisionInfoList):
        """
        Handle the subject colliding with a banana
        @param collisionInfoList:
        @return:
        """
        #print 'collide'
        config = Conf.getInstance().getConfig()  # Get configuration dictionary.
        # check if we are giving extra reward
        self.extra = config['extra']
        
        # which banana we ran into
        self.byeBanana = collisionInfoList[0].getInto().getIdentifier()
        #print self.byeBanana
        # cannot run inside of banana
        MovingObject.handleRepelCollision(collisionInfoList)

        # Makes it so Avatar cannot turn or go forward
        Avatar.getInstance().setMaxTurningSpeed(0)
        Avatar.getInstance().setMaxForwardSpeed(0)

        # start reward, will continue reward as long as beeps 
        # is less than numBeeps
        # (checks during each frame, see checkReward)
        #if self.reward:
        #    self.reward.pumpOut()
        #else:
        #    print 'first beep'
        self.beeps = 0

    def goneBanana(self):
        # make banana disappear
        #print 'banana should go away'
        # make banana go away
        #print self.byeBanana[-2:]
        self.bananaModel[int(self.byeBanana[-2:])].setStashed(True)
        self.stashed -= 1
        #print 'banana gone', self.byeBanana
        #print self.stashed
        # log collected banana
        VLQ.getInstance().writeLine("YUMMY", [self.byeBanana])
        if self.stashed == 0:
            #print 'last banana'
            VLQ.getInstance().writeLine("YUMMY", ['last_banana'])
            self.replenishBananas()
            self.trialNum += 1
        VLQ.getInstance().writeLine("NewTrial", [self.trialNum])

    def checkReward(self):
        # checks to see if we are giving reward. If we are, there
        # was a collision, and avatar can't move and banana hasn't 
        # disappeared yet.
        # After last reward, banana disappears and avatar can move.
        # print 'current beep', self.beeps
        if self.beeps == None:
            return
        
        # Still here? Give reward!
        if self.reward:
            self.reward.pumpOut()
        else:
            print 'beep', self.beeps
        # increment reward
        self.beeps += 1
        
        # If done, get rid of banana
        if self.beeps == self.numBeeps:
            # check to see if we are doing double reward
            if self.stashed == 1 and self.extra > 1:
                #print 'reset'
                self.beeps = 0
                self.extra -= 1
            else:
                # banana disappears 
                self.goneBanana()
                # avatar can move
                Avatar.getInstance().setMaxTurningSpeed(self.fullTurningSpeed)
                Avatar.getInstance().setMaxForwardSpeed(self.fullForwardSpeed)
                # reward is over
                self.beeps = None


    def getEyeData(self):
        eyeData = pydaq.EOGData
        Log.getInstance().writeLine("EyeData",
                                [((eyeData[0] * self.gain[0]) - self.offset[0]),
                                ((eyeData[1] * self.gain[1]) - self.offset[1])])

    def upTurnSpeed(self, inputEvent):
        avatar = Avatar.getInstance()
        self.fullTurningSpeed += 0.1
        if avatar.getMaxTurningSpeed() > 0:
            avatar.setMaxTurningSpeed(self.fullTurningSpeed)
        print("fullTurningSpeed: " + str(self.fullTurningSpeed))

    def downTurnSpeed(self, inputEvent):
        avatar = Avatar.getInstance()
        self.fullTurningSpeed -= 0.1
        if avatar.getMaxTurningSpeed() > 0:
            avatar.setMaxTurningSpeed(self.fullTurningSpeed)
        print("fullTurningSpeed: " + str(self.fullTurningSpeed))

    def start(self):
        """
        Start the experiment.
        """
        #print 'start'
        Experiment.getInstance().start()

if __name__ == '__main__':
    #print 'main?'
    GoBananas().start()
else:
    print 'not main?'
    #import argparse
    #p = argparse.ArgumentParser()
    #p.add_argument('-scrap')
    #import sys
    #sys.argv.extend(['stest'])
    #sys.argv = ['goBananas','-stest']
    #,'--no-eeg','--no-fs']
    GoBananas().start()
