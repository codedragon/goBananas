from pandaepl import Model, MovingObject, Avatar, VideoLogQueue, Camera
from panda3d.core import Point3
from load_models import PlaceModels, load_models
import moBananas as mB
import os
import random
from numpy import sqrt, pi


class Fruit():
    def __init__(self, config):
        # number fruit to do including first banana (but not remembered location,
        # since there is no actual fruit there). make life easier for researchers,
        # and start counting with 1.
        self.num_fruit = config['num_fruit'] - 1
        self.dir = config['fruit_dir']
        # get this from load_models instead
        #self.scale = config['bananaScale']
        # for repeating a particular configuration
        self.repeat = config['fruit_repeat']
        self.repeat_number = config['repeat_number']
        if self.repeat:
            self.now_repeat = random.choice(range(self.repeat_number))
            print('collect fruit positions from trial', self.now_repeat)
        else:
            self.now_repeat = None
        self.manual = config['manual']
        self.fruit_dict = {}
        self.fruit_models = []
        #self.stashed = self.num_fruit
        self.beeps = None
        self.collision = True
        self.got_fruit = None
        self.pList = []
        if self.manual:
            self.pList = config['pos_fruit']
            self.create_fruit(positions=True)
        else:
            self.create_fruit()

    def create_fruit(self, start=None, positions=None):
        #print 'create bananas'
        #print start
        print 'number fruit', self.num_fruit
        # Randomly assign where fruit goes and return a fruitModel.
        # start allows you to just add new fruit to the fruit already on
        # the field
        if start is None:
            start = 0
        if positions is None:
            pList = []
        # get current position of avatar, so fruit not too close.
        avatar = Avatar.Avatar.getInstance()
        avatarXY = (avatar.getPos()[0], avatar.getPos()[1])
        #print avatarXY
        # for sequential fruit, still create using setXY, since we
        # don't want fruit in the same place twice in one round
        load_models()
        i = 0
        for item in PlaceModels._registry:
            if 'fruit' in item.group:
                print item.model
                if positions:
                    x, y = self.pList[i]
                else:
                    (x, y) = mB.setXY(pList, avatarXY)
                pList.append((x, y))
                model = Model.Model(item.name, item.model, Point3(x, y, 1), self.collide_fruit)
                model.setHpr(Point3(random.randint(0, 360), 0, 75))
                model.setScale(item.scale)
                self.fruit_dict[item.name] = i
                #print(model.retrNodePath().getChild(0))
                #print(model.retrNodePath().getChild(0).getChild(0).node())
                # set collision sphere around fruit
                model.retrNodePath().getChild(0).getChild(0).setScale(item.coll_scale)
                # uncomment to see collision sphere around fruit
                model.retrNodePath().getChild(0).getChild(0).show()
                self.fruit_models.append(model)
                # if true, object is removed from the environment, but not destroyed
                # all but banana are stashed in beginning
                self.fruit_models[i].setStashed(True)
                if item.name == 'banana':
                    self.fruit_models[i].setStashed(False)
                print self.fruit_models[i].getPos()
                i += 1
                if i > self.num_fruit:
                    break

        print 'end load fruit'
        # go ahead and save these banana placements, if we are saving from a different trial,
        # will just be over-written.
        if self.repeat and positions is None:
            self.pList = pList
        #print pList

    def collide_fruit(self, collisionInfoList):
        """
        Handle the subject colliding with a banana
        @param collisionInfoList:
        @return:
        """
        print 'collision'
        # which fruit we ran into
        self.got_fruit = collisionInfoList[0].getInto().getIdentifier()
        print self.got_fruit
        # check to see if the banana was in the camera view when collided,
        # if not, then ignore collision
        collided = collisionInfoList[0].getInto()
        cam_node_path = Camera.Camera.getDefaultCamera().retrNodePath()
        #print collided.retrNodePath().getPos(cam_node_path)
        #print cam_node_path.node().isInView(collided.retrNodePath().getPos(cam_node_path))
        # Sometimes we collide with a banana multiple times for no damn reason, so setting self.collision
        # to keep track of whether this is the first collision
        print self.collision
        if cam_node_path.node().isInView(collided.retrNodePath().getPos(cam_node_path)) and self.collision:
            print self.got_fruit
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

    def replenish_all_fruit(self, repeat=None):
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
        for i in range(self.num_fruit):
            #print pList
            if repeat == 'repeat':
                (x, y) = pList[i]
            else:
                (x, y) = mB.setXY(pList, avatarXY)
                pList.append((x, y))
            #print x, y
            self.fruit_models[i].setPos(Point3(x, y, 1))
            # make new bananas visible
            self.fruit_models[i].setStashed(False)
            # start count again
        #print pList
        if repeat == 'new':
            print 'save new'
            # save the current list of random banana placements
            self.pList = pList
        #self.stashed = self.num_fruit

    def replenish_stashed_fruit(self):
        #print 'replenish'
        pList = []
        avatar = Avatar.Avatar.getInstance()
        avatarXY = (avatar.getPos()[0], avatar.getPos()[1])
        for i in range(self.num_fruit):
            #print pList
            if self.fruit_models[i].isStashed():
                #print 'banana stashed, unstash now'
                (x, y) = mB.setXY(pList, avatarXY)
                pList.append((x, y))
                #print x, y
                self.fruit_models[i].setPos(Point3(x, y, 1))
                # make new bananas visible
                self.fruit_models[i].setStashed(False)
            else:
                # for bananas not replacing, get current banana position, so we
                # don't put them too close together
                pList.append((self.fruit_models[i].getPos()[0], self.fruit_models[i].getPos()[1]))

    def gone_fruit(self, trial_num):
        # make banana disappear
        print 'fruit should go away'
        #print dir(self.fruit_models[0])
        # make banana go away
        #print self.bananaModels[1].getH()
        #print self.got_fruit[-2:]
        # stash the fruit we just ran into,
        self.fruit_models[self.fruit_dict[self.got_fruit]].setStashed(True)
        # unstash the next fruit, unless it is time to go to the remembered banana
        if self.fruit_dict[self.got_fruit] == self.num_fruit:
            # if we are searching for the banana, send trial_num as None
            trial_num = None
            print 'remember banana'
        else:
            self.fruit_models[self.fruit_dict[self.got_fruit] + 1].setStashed(False)

        #self.stashed -= 1
        #print 'banana gone', self.got_fruit
        #print self.stashed
        # log collected banana
        VideoLogQueue.VideoLogQueue.getInstance().writeLine("Finished", [self.got_fruit])
        self.collision = True
        # if self.stashed == 0:
        #     #print 'last banana'
        #     # If doing repeat, every x trials choose a trial to
        #     # be the repeat test layout. This will not happen until after
        #     # we have gone through the first self.repeat_number amount of
        #     # trials, so will not interfere with collecting the initial set
        #     # of banana layout for repeat
        #     print('just finished trial_num', trial_num)
        #     trial_num += 1
        #     if self.repeat and trial_num % self.repeat_number == 0:
        #         # time to choose a new repeat trial, choose a number from 0 to
        #         # repeat number, since we haven't
        #         self.now_repeat = trial_num + random.choice(range(self.repeat_number))
        #         print('chose trial', self.now_repeat)
        #     # collect the set of banana positions that will be repeated
        #     if trial_num == self.now_repeat and self.now_repeat < self.repeat_number:
        #         VideoLogQueue.VideoLogQueue.getInstance().writeLine("RepeatTrial", [trial_num])
        #         self.replenish_all_fruit('new')
        #     elif trial_num == self.now_repeat:
        #         print 'repeat'
        #         VideoLogQueue.VideoLogQueue.getInstance().writeLine("RepeatTrial", [trial_num])
        #         self.replenish_all_fruit('repeat')
        #     else:
        #         self.replenish_all_fruit()
        #     VideoLogQueue.VideoLogQueue.getInstance().writeLine("NewTrial", [trial_num])
            #new_trial()
        return trial_num
