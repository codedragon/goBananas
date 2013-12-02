#from direct.directbase.DirectStart import base
from pandaepl import Model, MovingObject, Avatar, VideoLogQueue, Camera
from panda3d.core import Point3
import moBananas as mb
import os
import random

class Bananas():
    def __init__(self, config):
        self.numBananas = config['numBananas']
        self.dir = config['bananaDir']
        self.scale = config['bananaScale']
        self.createBananas(0)

    def createBananas(self, start):
        #print 'create bananas'
        # Randomly assign where bananas go and return a banana bananaModel.
        self.bananaModels = []
        #print 'numBananas', self.numBananas
        pList = []
        # get current position of avatar, so bananas not too close.
        avatar = Avatar.Avatar.getInstance()
        avatarXY = (avatar.getPos()[0], avatar.getPos()[1])
        #print avatarXY
        for i, j in enumerate(range(start, self.numBananas)):
            (x, y) = mb.setXY(pList, avatarXY)
            #print i,j
            pList += [(x, y)]
            # Model is a global from pandaepl
            # Point3 is a global from Panda3d

            bananaModel = Model.Model("banana" + "%02d" % j,
                                os.path.join(self.dir,
                                "banana" + ".bam"),
                                Point3(x, y, 1),
                                self.collideBanana)
            bananaModel.setScale(self.scale)
            bananaModel.setH(random.randint(0, 361))
            # make collision sphere around banana really small
            bananaModel.retrNodePath().getChild(0).getChild(0).getChild(0).setScale(0.2)
            # uncomment to see collision sphere around bananas
            bananaModel.retrNodePath().getChild(0).getChild(0).getChild(0).show()
            self.bananaModels.append(bananaModel)
            # if true, object is removed from the environment, but not destroyed
            # so start with not stashed
            self.bananaModels[i].setStashed(False)

        self.stashed = self.numBananas
        self.beeps = None
        #self.byeBanana = []
        #print 'end load bananas'
        #print pList
        #return bananaModels

    def collideBanana(self, collisionInfoList):
        """
        Handle the subject colliding with a banana
        @param collisionInfoList:
        @return:
        """
        # which banana we ran into
        self.byeBanana = collisionInfoList[0].getInto().getIdentifier()
        # check to see if the banana was in the camera view when collided,
        # if not, then ignore collision
        collided = collisionInfoList[0].getInto()
        camNodePath = Camera.Camera.getDefaultCamera().retrNodePath()
        #print collided.retrNodePath().getPos(camNodePath)
        #print camNodePath.node().isInView(collided.retrNodePath().getPos(camNodePath))
        if camNodePath.node().isInView(collided.retrNodePath().getPos(camNodePath)):
            VideoLogQueue.VideoLogQueue.getInstance().writeLine("Yummy", [self.byeBanana])
            #print self.byeBanana
            # cannot run inside of banana
            MovingObject.MovingObject.handleRepelCollision(collisionInfoList)

            # Makes it so Avatar cannot turn or go forward
            Avatar.Avatar.getInstance().setMaxTurningSpeed(0)
            Avatar.Avatar.getInstance().setMaxForwardSpeed(0)

            self.beeps = 0

    def replenishBananas(self):
        pList = []
        avatar = Avatar.Avatar.getInstance()
        avatarXY = (avatar.getPos()[0], avatar.getPos()[1])
        # print 'avatar pos', avatarXY
        for i in range(self.numBananas):
            (x, y) = mb.setXY(pList, avatarXY)
            self.bananaModels[i].setPos(Point3(x, y, 1))
            # make new bananas visible
            self.bananaModels[i].setStashed(False)
            # start count again
        self.stashed = self.numBananas

    def goneBanana(self, trialNum):
        # make banana disappear
        #print 'banana should go away'
        # make banana go away
        #print self.bananaModels[1].getH()
        #print self.byeBanana[-2:]
        self.bananaModels[int(self.byeBanana[-2:])].setStashed(True)
        self.stashed -= 1
        #print 'banana gone', self.byeBanana
        #print self.stashed
        # log collected banana
        VideoLogQueue.VideoLogQueue.getInstance().writeLine("Finished", [self.byeBanana])
        if self.stashed == 0:
            #print 'last banana'
            self.replenishBananas()
            trialNum += 1
            VideoLogQueue.VideoLogQueue.getInstance().writeLine("NewTrial", [trialNum])
        return trialNum

    def increaseBananas(self, inputEvent):
        # increase number of bananas by 5
        self.numBananas += 5
        # if we are increasing beyond original amount of bananas,
        # have to create the new bananas
        # print 'bananas number', len(self.bananaModel)
        if self.numBananas > len(self.bananaModels):
            self.bananaModels.extend(self.createBananas(self.numBananas - 5))
            # make new ones show up
        self.replenishBananas()

    def decreaseBananas(self, inputEvent):
        # decrease number of bananas by 5
        # we can just hide the bananas we aren't using
        for i in range(self.numBananas):
            self.bananaModels[i].setStashed(True)
        self.numBananas -= 5
        # reset bananas
        self.replenishBananas()
