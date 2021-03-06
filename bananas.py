from pandaepl import Model, MovingObject, Avatar, VideoLogQueue, Camera
from panda3d.core import Point3
import moBananas as mB
import os
import random
from numpy import sqrt, pi


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
        self.weighted_bananas = config['weightedBananas']
        if self.weighted_bananas:
            self.change_weights = config['changeWeightLoc']
            # total area is 400, 20x20
            high_area = 0.25 * 0.33 * 400
            middle_area = 0.25 * 400
            self.high_radius = sqrt(high_area / pi)
            self.mid_radius = sqrt(middle_area / pi)
            self.high_reward = config['high_reward']
            self.mid_reward = config['mid_reward']
            self.low_reward = config['low_reward']
            print self.high_radius
            print self.mid_radius
            # must use a decimal number (float)
            weight_center = (-8.0, 0.5)
            self.changeWeightedCenter(weight_center)
            # uncomment to choose a center randomly
            #self.changeWeightedCenter()
            print('center', self.weight_center)
        try:
            self.manual = config['manual']
        except KeyError:
            print 'default'
            self.manual = False
        #print self.manual
        self.bananaModels = []
        self.stashed = self.numBananas
        self.beeps = None
        self.collision = True
        self.pList = []
        if self.manual:
            self.pList = config['posBananas']
            self.create_bananas(positions=True)
        else:
            self.create_bananas()

    def create_bananas(self, start=None, positions=None):
        #print 'create bananas'
        #print start
        print 'numBananas', self.numBananas
        # Randomly assign where bananas go and return a banana bananaModel.
        # start allows you to just add new bananas to the bananas already on
        # the field
        if start is None:
            start = 0
        if positions is None:
            pList = []
        # get current position of avatar, so bananas not too close.
        avatar = Avatar.Avatar.getInstance()
        avatarXY = (avatar.getPos()[0], avatar.getPos()[1])
        #print avatarXY
        for i in range(start, self.numBananas):
            if positions:
                x, y = self.pList[i]
            else:
                (x, y) = mB.setXY(pList, avatarXY)
                pList.append((x, y))
            self.create_banana_model(i, x, y)
        #print 'end load bananas'
        # go ahead and save these banana placements, if we are saving from a different trial,
        # will just be over-written.
        if self.repeat and positions is None:
            self.pList = pList
        #print pList
        # if you want to see a smiley ball sitting at the center of the weighted circle,
        # uncomment here and in changeWeightedCenter
        #self.ballModel = Model.Model("smiley", "smiley",
        #                        Point3(self.weight_center[0], self.weight_center[1], 1))

        #self.ballModel.setScale(0.1)

    def create_banana_model(self, i, x, y):
        banana_model = Model.Model("banana" + "%03d" % i,
                                os.path.join(self.dir,
                                "banana.bam"),
                                Point3(x, y, 1),
                                self.collideBanana)
        banana_model.setScale(self.scale)
        banana_model.setH(random.randint(0, 360))
        # make collision sphere around banana really small
        banana_model.retrNodePath().getChild(0).getChild(0).getChild(0).setScale(0.2)
        # uncomment to see collision sphere around bananas
        print banana_model.retrNodePath().getChild(0).getChild(0).getChild(0).node()
        #banana_model.retrNodePath().getChild(0).getChild(0).getChild(0).show()
        self.bananaModels.append(banana_model)
        # if true, object is removed from the environment, but not destroyed
        # so start with not stashed
        self.bananaModels[i].setStashed(False)

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
        cam_node_path = Camera.Camera.getDefaultCamera().retrNodePath()
        #print collided.retrNodePath().getPos(cam_node_path)
        #print cam_node_path.node().isInView(collided.retrNodePath().getPos(cam_node_path))
        # Sometimes we collide with a banana multiple times for no damn reason, so setting self.collision
        # to keep track of whether this is the first collision
        if cam_node_path.node().isInView(collided.retrNodePath().getPos(cam_node_path)) and self.collision:
            #print self.byeBanana
            # cannot run inside of banana
            MovingObject.MovingObject.handleRepelCollision(collisionInfoList)
            #print 'stop moving'
            # Makes it so Avatar cannot turn or go forward
            Avatar.Avatar.getInstance().setMaxTurningSpeed(0)
            Avatar.Avatar.getInstance().setMaxForwardSpeed(0)
            #VideoLogQueue.VideoLogQueue.getInstance().writeLine("Yummy", ['stop moving!'])
            # Setting self.beeps to 0 is signal to give reward
            self.beeps = 0
            #print self.beeps
            self.collision = False

    def replenish_all_bananas(self, repeat=None):
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
                (x, y) = mB.setXY(pList, avatarXY)
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

    def replenish_stashed_bananas(self):
        #print 'replenish'
        pList = []
        avatar = Avatar.Avatar.getInstance()
        avatarXY = (avatar.getPos()[0], avatar.getPos()[1])
        for i in range(self.numBananas):
            #print pList
            if self.bananaModels[i].isStashed():
                #print 'banana stashed, unstash now'
                (x, y) = mB.setXY(pList, avatarXY)
                pList.append((x, y))
                #print x, y
                self.bananaModels[i].setPos(Point3(x, y, 1))
                # make new bananas visible
                self.bananaModels[i].setStashed(False)
            else:
                # for bananas not replacing, get current banana position, so we
                # don't put them too close together
                pList.append((self.bananaModels[i].getPos()[0], self.bananaModels[i].getPos()[1]))

    def goneBanana(self, trialNum):
        # make banana disappear
        #print 'banana should go away'
        # make banana go away
        #print self.bananaModels[1].getH()
        #print self.byeBanana[-2:]
        self.bananaModels[int(self.byeBanana[-3:])].setStashed(True)
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
            print('just finished trialNum', trialNum)
            trialNum += 1
            if self.repeat and trialNum % self.repeat_number == 0:
                # time to choose a new repeat trial, choose a number from 0 to
                # repeat number, since we haven't
                self.now_repeat = trialNum + random.choice(range(self.repeat_number))
                print('chose trial', self.now_repeat)
            # collect the set of banana positions that will be repeated
            if trialNum == self.now_repeat and self.now_repeat < self.repeat_number:
                VideoLogQueue.VideoLogQueue.getInstance().writeLine("RepeatTrial", [trialNum])
                self.replenish_all_bananas('new')
            elif trialNum == self.now_repeat:
                print 'repeat'
                VideoLogQueue.VideoLogQueue.getInstance().writeLine("RepeatTrial", [trialNum])
                self.replenish_all_bananas('repeat')
            else:
                self.replenish_all_bananas()
            if self.weighted_bananas and trialNum % self.change_weights == 0:
                self.changeWeightedCenter()
            VideoLogQueue.VideoLogQueue.getInstance().writeLine("NewTrial", [trialNum])
            #new_trial()
        return trialNum

    def increaseBananas(self, inputEvent):
        # increase number of bananas by 5
        print self.numBananas
        self.numBananas += 5
        print('new banana number', self.numBananas)
        # if we are increasing beyond original amount of bananas,
        # have to create the new bananas
        # print 'bananas number', len(self.bananaModel)
        if self.numBananas > len(self.bananaModels):
            self.create_bananas(self.numBananas - 5)
            # make new ones show up (also any that have been previously hidden)
        self.replenish_stashed_bananas()

    def decreaseBananas(self, inputEvent):
        # decrease number of bananas by 5
        # we can just hide the bananas we aren't using
        # hide the last 5.
        start = self.numBananas - 5
        for i in range(start, self.numBananas):
            self.bananaModels[i].setStashed(True)
        self.numBananas -= 5
        # reset bananas
        self.replenish_stashed_bananas()

    def changeWeightedCenter(self, center=None):
        if center is None:
            self.weight_center = (random.uniform(-10, 10), random.uniform(-10, 10))
        else:
            self.weight_center = center
        # if you want to see a smiley ball at the weight center... (also have
        # to initialize it above)
        #self.ballModel.setPos(Point3(self.weight_center[0], self.weight_center[1], 1))
        VideoLogQueue.VideoLogQueue.getInstance().writeLine("WeightedCenter",
                                                            [self.weight_center[0],
                                                             self.weight_center[1]])

    def changeTrialCenter(self, trialNum):
        # override for when the next change of weighted center happens
        # may eventually want a different variable for this, if we really want
        # to use both regular changes and overrides in the same game.
        self.change_weights = trialNum + 1

    def get_reward_level(self, position):
        print('banana position', position[0], position[1])
        distance = mB.distance((position[0], position[1]), self.weight_center)
        print('center', self.weight_center)
        print('distance to center', distance)
        print('high', self.high_radius)
        print('mid', self.mid_radius)
        if distance < self.high_radius:
            reward = self.high_reward
        elif distance < self.mid_radius:
            reward = self.mid_reward
        else:
            reward = self.low_reward
        return reward
