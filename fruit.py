from pandaepl import Model, MovingObject, Avatar, VideoLogQueue, Camera
from panda3d.core import Point3
from load_models import PlaceModels, load_models
import moBananas as mB
import os
import random
from numpy import sqrt, pi


class Fruit():
    def __init__(self, config):

        # fruit to remember, if not a remember fruit task, will be none
        self.fruit_to_remember = config['fruit_to_remember']

        # for repeating a particular configuration
        self.repeat = config['fruit_repeat']
        self.repeat_number = config['repeat_number']
        if self.repeat:
            self.now_repeat = random.choice(range(self.repeat_number))
            print('collect fruit positions from trial', self.now_repeat)
        else:
            self.now_repeat = None
        self.manual = config['manual']
        # for the moment Beth wants all of the other fruit the same, but she has gone
        # back and forth on this, so set up machinery to do multiple types of fruit
        self.index_fruit_dict = {}
        self.fruit_models = []
        # list to keep track of which fruit have shown up
        self.fruit_list = []
        #self.stashed = self.num_fruit
        self.beeps = None
        self.collision = True
        # variable to save the last fruit we ran into
        self.got_fruit = None
        self.pList = []

    def create_fruit(self, fruit_dict):
        # return a fruitModel.
        #print 'create bananas'
        #print start
        print 'number fruit', fruit_dict
        pList = []
        # get current position of avatar, so fruit not too close.
        avatar = Avatar.Avatar.getInstance()
        avatarXY = (avatar.getPos()[0], avatar.getPos()[1])
        #print avatarXY
        # for sequential fruit, still create using setXY, since we
        # don't want fruit in the same place twice in one round
        load_models()
        fruit_count = 0
        this_fruit = 0
        this_fruit_num = 0
        # for each fruit in our dictionary, find corresponding model,
        # create new model for each count in dictionary of that fruit
        for fruit, count in self.num_fruit_dict.iteritems():
            for item in PlaceModels._registry:
                if fruit == item.name:
                    for each in range(count):
                        print item.model
                        # positions actually don't matter here, since we will reset them.
                        (x, y) = (0, 0)
                        pList.append((x, y))
                        name = item.name + "%03d" % this_fruit_num
                        print name
                        model = Model.Model(name, item.model, Point3(x, y, 1), self.collide_fruit)
                        model.setHpr(Point3(random.randint(0, 360), 0, 75))
                        model.setScale(item.scale)
                        model.name = item.name
                        if model.name in self.index_fruit_dict:
                            self.index_fruit_dict[model.name].append(this_fruit_num)
                        else:
                            self.index_fruit_dict[item.name] = this_fruit_num
                    #print(model.retrNodePath().getChild(0))
                    #print(model.retrNodePath().getChild(0).getChild(0).node())
                    # set collision sphere around fruit
                    model.retrNodePath().getChild(0).getChild(0).setScale(item.coll_scale)
                    # uncomment to see collision sphere around fruit
                    model.retrNodePath().getChild(0).getChild(0).show()
                    self.fruit_models.append(model)
                    # if true, object is removed from the environment, but not destroyed
                    # all fruit are stashed in beginning, one will be loaded in restart_fruit_sequence
                    self.fruit_models[fruit_count].setStashed(True)
                    #print i
                    fruit_count += 1
                    if fruit_count > self.num_fruit:
                        print('break', fruit_count)
                        break
                    if this_fruit_num == self.num_fruit[this_fruit]:
                        this_fruit_num = 0
                        this_fruit += 1
        print self.index_fruit_dict
        print self.fruit_models
        print 'end create fruit'
        # go ahead and save these banana placements, if we are saving from a different trial,
        # will just be over-written. (restart_fruit_sequence always called after create)
        if self.repeat and positions is None:
            self.pList = pList
        #print pList
        # if the fruit_dict is different from self.num_fruit_dict, add the two together, somehow...

    def restart_fruit_sequence(self, repeat=None):
        print('fruit_list', self.fruit_list)
        print('num_fruit', self.num_fruit)
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
        print(range(self.num_fruit))
        for i in range(self.num_fruit):
            print i
            #print pList
            if repeat == 'repeat':
                (x, y) = pList[i]
            else:
                (x, y) = mB.setXY(pList, avatarXY)
                pList.append((x, y))
            print x, y
            self.fruit_models[i].setPos(Point3(x, y, 1))
            # make all fruit except one to be remembered not-visible
            self.fruit_models[i].setStashed(True)
            if self.fruit_models[i].name == self.fruit_to_remember:
                self.fruit_models[i].setStashed(False)
            # add to our list
            self.fruit_list.append(self.fruit_models[i].name)
        print self.fruit_list

        #print pList
        if repeat == 'new':
            print 'save new'
            # save the current list of random banana placements
            self.pList = pList
        #self.stashed = self.num_fruit

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
        print('collision', self.collision)
        print('camera', Camera.Camera.getDefaultCamera().getPos())
        print('collision position', collided.retrNodePath().getPos(cam_node_path))
        for fruit in self.fruit_models:
            print fruit.getPos()
        print('in view', cam_node_path.node().isInView(collided.retrNodePath().getPos(cam_node_path)))
        if cam_node_path.node().isInView(collided.retrNodePath().getPos(cam_node_path)) and self.collision:
            print self.got_fruit
            # cannot run inside of banana - can't I just do this earlier for all of the fruit?
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

    def gone_fruit(self, trial_num):
        # currently not using trial_num, but may create a task using multiple fruit where
        # this becomes necessary again.
        print 'fruit should go away'
        print('this fruit', self.index_fruit_dict[self.got_fruit])

        # remove the current fruit from list of possible fruit
        self.fruit_list.remove(self.got_fruit)
        # stash the fruit we just ran into,
        self.fruit_models[self.index_fruit_dict[self.got_fruit]].setStashed(True)
        # unstash the next fruit, unless it is time to go to the remembered banana
        find_banana = False
        # know it is time to search for location, when we have made it through all
        # of the fruit
        if not self.fruit_list:
            # if we are searching for the banana, send find_banana as true
            find_banana = True
            print 'remember banana'
        else:
            print('whole dict', self.index_fruit_dict)
            print('next fruit in list', self.fruit_list[0])
            print('next fruit in dict', self.index_fruit_dict[self.fruit_list[0]])
            self.fruit_models[self.index_fruit_dict[self.fruit_list[0]]].setStashed(False)

        #self.stashed -= 1
        #print 'banana gone', self.got_fruit
        #print self.stashed
        # log collected banana
        VideoLogQueue.VideoLogQueue.getInstance().writeLine("Finished", [self.got_fruit])
        self.collision = True
        return find_banana

    def replenish_stashed_fruit(self):
        print 'replenish'
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

