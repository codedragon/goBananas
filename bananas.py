from pandaepl import Model, MovingObject, Avatar, VideoLogQueue, Camera
from panda3d.core import Point3
import moBananas as mb
import os
import sys
import random


class Bananas():
    def __init__(self, config):
        self.numBananas = config['numBananas']
        self.dir = config['bananaDir']
        self.scale = config['bananaScale']
        self.repeat = config['bananaRepeat']
        self.repeat_number = config['repeatNumber']
        if self.repeat:
            self.now_repeat = random.choice(range(self.repeat_number))
            print('collect banana positions from trial', self.now_repeat)
        else:
            self.now_repeat = None
        try:
            self.manual = config['manual']
        except KeyError:
            print 'default'
            self.manual = False
        print self.manual
        self.bananaModels = []
        self.stashed = self.numBananas
        self.beeps = None
        self.collision = True
        self.pList = []
        if self.manual:
            self.posBananas = config['posBananas']
            self.createManualBananas()
        else:
            self.createBananas()

    def createManualBananas(self):
        # don't assign bananas randomly, place exactly where we want them
        # according to config file. Technically, could do more than 2 bananas,
        # but have never needed to.
        self.pList = self.posBananas
        for i in range(self.numBananas):
            # pop okay, since only doing this for a list of max 4 items
            #x = self.posBananas.pop(0)
            #y = self.posBananas.pop(0)
            x, y = self.pList[i]
            bananaModel = Model.Model("banana" + "%02d" % i,
                                os.path.join(self.dir,
                                "banana.bam"),
                                Point3(x, y, 1),
                                self.collideBanana)
            bananaModel.setScale(self.scale)
            # could make this static instead
            #bananaModel.setH(random.randint(0, 360))
            bananaModel.setH(280)
            # make collision sphere around banana really small
            bananaModel.retrNodePath().getChild(0).getChild(0).getChild(0).setScale(0.3)
            # uncomment to see collision sphere around bananas
            #bananaModel.retrNodePath().getChild(0).getChild(0).getChild(0).show()
            # what the hell is up with so many banana children?
            #print 'banana'
            #print bananaModel.retrNodePath()
            #print bananaModel.retrNodePath().getChild(0)
            #print bananaModel.retrNodePath().getChild(0).getChild(0)
            #print bananaModel.retrNodePath().getChild(0).getChild(0).getChild(0)
            #print bananaModel.retrNodePath().getChild(0).getChild(0).getChild(0).node()
            #print bananaModel.retrNodePath().getChild(0).getChild(0).getChild(0).node().getFromCollideMask()
            #print bananaModel.retrNodePath().getChild(0).getChild(0).getChild(0).node().getIntoCollideMask()
            self.bananaModels.append(bananaModel)
            # if true, object is removed from the environment, but not destroyed
            # so start with not stashed
            self.bananaModels[i].setStashed(False)

        #print 'on screen?'
        print self.pList

    def createBananas(self, start=None):

        #print 'create bananas'
        # Randomly assign where bananas go and return a banana bananaModel.
        # start allows you to just add new bananas to the bananas already on
        # the field
        if start is None:
            start = 0
        #print 'numBananas', self.numBananas
        pList = []
        # get current position of avatar, so bananas not too close.
        avatar = Avatar.Avatar.getInstance()
        avatarXY = (avatar.getPos()[0], avatar.getPos()[1])
        #print avatarXY
        for i, j in enumerate(range(start, self.numBananas)):
            (x, y) = mb.setXY(pList, avatarXY)
            #print i,j
            #pList += [(x, y)]
            pList.append((x, y))
            # Model is a global from pandaepl
            # Point3 is a global from Panda3d

            bananaModel = Model.Model("banana" + "%02d" % j,
                                os.path.join(self.dir,
                                "banana.bam"),
                                Point3(x, y, 1),
                                self.collideBanana)
            bananaModel.setScale(self.scale)
            bananaModel.setH(random.randint(0, 361))
            # make collision sphere around banana really small
            bananaModel.retrNodePath().getChild(0).getChild(0).getChild(0).setScale(0.2)
            # uncomment to see collision sphere around bananas
            #bananaModel.retrNodePath().getChild(0).getChild(0).getChild(0).show()
            self.bananaModels.append(bananaModel)
            # if true, object is removed from the environment, but not destroyed
            # so start with not stashed
            self.bananaModels[i].setStashed(False)
        #print 'end load bananas'
        # go ahead and save these banana placements, if we are saving from a different trial,
        # will just be over-written.
        if self.repeat:
            self.pList = pList
        print pList
        #return bananaModels

    def collideBanana(self, collisionInfoList):
        """
        Handle the subject colliding with a banana
        @param collisionInfoList:
        @return:
        """
        #print 'collision'
        # which banana we ran into
        self.byeBanana = collisionInfoList[0].getInto().getIdentifier()
        # check to see if the banana was in the camera view when collided,
        # if not, then ignore collision
        collided = collisionInfoList[0].getInto()
        camNodePath = Camera.Camera.getDefaultCamera().retrNodePath()
        #print collided.retrNodePath().getPos(camNodePath)
        #print camNodePath.node().isInView(collided.retrNodePath().getPos(camNodePath))
        # Sometimes we collide with a banana multiple times for no damn reason, so setting self.collision
        # to keep track of whether this is the first collision
        if camNodePath.node().isInView(collided.retrNodePath().getPos(camNodePath)) and self.collision:
            #print self.byeBanana
            # cannot run inside of banana
            MovingObject.MovingObject.handleRepelCollision(collisionInfoList)
            #print 'stop moving'
            # Makes it so Avatar cannot turn or go forward
            Avatar.Avatar.getInstance().setMaxTurningSpeed(0)
            Avatar.Avatar.getInstance().setMaxForwardSpeed(0)
            #VideoLogQueue.VideoLogQueue.getInstance().writeLine("Yummy", ['stop moving!'])
            self.beeps = 0
            #print self.beeps
            self.collision = False

    def replenishBananas(self, repeat=None):
        # Eventually have a different code in repeat to signify
        # if using a previous set or saving a new set.
        if repeat == 'repeat' and self.pList:
            pList = self.pList
        else:
            pList = []
        #print pList
        avatar = Avatar.Avatar.getInstance()
        avatarXY = (avatar.getPos()[0], avatar.getPos()[1])
        # print 'avatar pos', avatarXY
        for i in range(self.numBananas):
            #print pList
            if repeat == 'repeat':
                (x, y) = pList[i]
            else:
                (x, y) = mb.setXY(pList, avatarXY)
                pList.append((x, y))
            #print x, y
            self.bananaModels[i].setPos(Point3(x, y, 1))
            # make new bananas visible
            self.bananaModels[i].setStashed(False)
            # start count again
        #print pList
        if repeat == 'new':
            print 'save new'
            # save the current list of random banana placements
            self.pList = pList
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
        self.collision = True
        if self.stashed == 0:
            #print 'last banana'
            # If doing repeat, every x trials choose a trial to
            # be the repeat test layout. This will not happen until after
            # we have gone through the first self.repeat_number amount of
            # trials, so will not interfere with collecting the initial set
            # of banana layout for repeat
            if self.repeat and trialNum % self.repeat_number == 0:
                self.now_repeat = trialNum + random.choice(range(self.repeat_number))
                print('chose trial', self.now_repeat)
            print('trialNum', trialNum)
            # collect the set of banana positions that will be repeated
            if trialNum == self.now_repeat and self.now_repeat < self.repeat_number:
                self.replenishBananas('new')
            elif trialNum == self.now_repeat:
                print 'repeat'
                self.replenishBananas('repeat')
            else:
                self.replenishBananas()
            trialNum += 1
            VideoLogQueue.VideoLogQueue.getInstance().writeLine("NewTrial", [trialNum])
            #new_trial()
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
