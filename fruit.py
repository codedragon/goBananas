from pandaepl import Model, MovingObject, Avatar, VideoLogQueue, Camera
from panda3d.core import Point3
from load_models import load_models, get_model
import moBananas as mB
import os
import random
from numpy import sqrt, pi


class Fruit():
    def __init__(self, config):

        # Do all of this prior to calling class, send in two lists,
        # fruit_types and num_fruit_types

        # fruit to remember, if remembering
        self.fruit_to_remember = config['fruit_to_remember']

        # fruit not remembering
        self.all_fruit = config['fruit']  # list of fruit
        self.num_fruit = config['num_fruit']  # list corresponding to list above

        if self.fruit_to_remember:
            self.all_fruit.insert(0, self.fruit_to_remember)
            self.num_fruit.insert(0, 1)

        # for repeating a particular configuration
        self.repeat = config['fruit_repeat']
        self.repeat_number = config['repeat_number']
        if self.repeat:
            self.now_repeat = random.choice(range(self.repeat_number))
            print('collect fruit positions from trial', self.now_repeat)
        else:
            self.now_repeat = None
        self.manual = config['manual']

        # index_fruit_dict keeps track of which index number in the fruit_model list corresponds to which
        # name/model, because this is easier than running a for loop every time to find the one
        # we want
        self.index_fruit_dict = {}
        # num_fruit dict tells us how many of each fruit we will be showing
        self.num_fruit_dict = {}
        self.fruit_models = []
        # list to keep track of which fruit have shown up
        self.fruit_list = []
        #self.stashed = self.num_fruit
        self.beeps = None
        self.collision = True
        # variable to save the last fruit we ran into
        self.got_fruit = None
        self.pos_list = []

    def create_fruit(self, fruit_dict):
        self.num_fruit_dict = fruit_dict
        # return a fruitModel.
        #print 'create bananas'
        #print start
        print 'dict of number fruit', fruit_dict
        # load the models
        load_models()
        # set counts
        model_count = 0
        # for each fruit in our dictionary, find corresponding model,
        # create new model for each count in dictionary of that fruit
        # This is a lot of loops, fortunately they are all small. Might
        # want to make a method for getting stuff out of PlaceModels.
        for fruit, count in fruit_dict.iteritems():
            for i in range(count):
                item = get_model('name', fruit)
                print item.model
                name = item.name + "%03d" % i
                # differentiate the fruit we are remembering, if we are doing
                # recall_banana task
                if self.fruit_to_remember and item.name == self.fruit_to_remember:
                    name = item.name
                print name
                # create actual model
                self.create_fruit_model(item, name)
                # if we haven't stuck this model in the dictionary yet, do it now
                if name not in self.index_fruit_dict:
                    self.index_fruit_dict[name] = model_count
                model_count += 1

        print self.index_fruit_dict
        print self.fruit_models
        print 'end create fruit'

    def create_fruit_model(self, item, name):
        # initial position does not matter
        model = Model.Model(name, item.model, Point3(0, 0, 1), self.collide_fruit)
        model.setHpr(Point3(random.randint(0, 360), 0, 75))
        model.setScale(item.scale)
        model.name = name
        #print(model.retrNodePath().getChild(0))
        #print(model.retrNodePath().getChild(0).getChild(0).node())
        # set collision sphere around fruit
        model.retrNodePath().getChild(0).getChild(0).setScale(item.coll_scale)
        # uncomment to see collision sphere around fruit
        model.retrNodePath().getChild(0).getChild(0).show()
        # hide all models on creation
        model.setStashed(True)
        self.fruit_models.append(model)
        return model.name

    def setup_trial(self, repeat=None):
        print('fruit_list', self.fruit_list)
        print('num_fruit', self.num_fruit)
        # Eventually have a different code in repeat to signify
        # if using a previous set or saving a new set.
        pos_list = []
        if repeat == 'repeat' and self.pos_list:
            pos_list = self.pos_list
        #print pos_list
        avatar = Avatar.Avatar.getInstance()
        avatarXY = (avatar.getPos()[0], avatar.getPos()[1])
        # print 'avatar pos', avatarXY
        for fruit, index in self.index_fruit_dict.iteritems():
            print fruit, index
            print index
            #print pos_list
            if repeat == 'repeat':
                (x, y) = pos_list[index]
            else:
                (x, y) = mB.setXY(pos_list, avatarXY)
            pos_list.append((x, y))
            #print x, y
            self.fruit_models[index].setPos(Point3(x, y, 1))
            # if task is remembering fruit,
            # make all fruit except one to be remembered not-visible
            if self.fruit_to_remember:
                self.fruit_models[index].setStashed(True)
                if self.fruit_models[index].name == self.fruit_to_remember:
                    self.fruit_models[index].setStashed(False)
            else:
                self.fruit_models[index].setStashed(False)
            # add to our list
            self.fruit_list.append(fruit)
            print self.fruit_list

        #print pos_list
        if repeat == 'new':
            print 'save new'
            # save the current list of random banana placements
            self.pos_list = pos_list
        #self.stashed = self.num_fruit

    def collide_fruit(self, collisionInfoList):
        """
        Handle the subject colliding with a banana, document fruit, subject
        freezes, reward is triggered.
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
        #print('collision', self.collision)
        #print('camera', Camera.Camera.getDefaultCamera().getPos())
        #print('collision position', collided.retrNodePath().getPos(cam_node_path))
        #for fruit in self.fruit_models:
        #    print fruit.getPos()
        #print('in view', cam_node_path.node().isInView(collided.retrNodePath().getPos(cam_node_path)))
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

    def disappear_fruit(self):
        # currently not using trial_num, but may create a task using multiple fruit where
        # this becomes necessary again.
        print('fruit should go away', self.got_fruit)
        current_index = self.index_fruit_dict[self.got_fruit]
        print('this fruit index', current_index)

        # remove the current fruit from list of possible fruit
        self.fruit_list.remove(self.got_fruit)
        # stash the fruit we just ran into,
        self.fruit_models[current_index].setStashed(True)
        # log collected banana
        VideoLogQueue.VideoLogQueue.getInstance().writeLine("Finished", [self.got_fruit])
        self.collision = True

    def get_next_fruit(self):
        # default is not time to find the banana memory
        find_banana_loc = False
        # know it is time to search for location, when we have made it through all
        # of the fruit
        # unstash the next fruit, unless it is time to go to the remembered banana
        if not self.fruit_list:
            # if we are searching for the banana, send find_banana as true
            find_banana_loc = True
            print 'remember banana'
        else:
            print('whole dict', self.index_fruit_dict)
            print('next fruit in list', self.fruit_list[0])
            print('next fruit in dict', self.index_fruit_dict[self.fruit_list[0]])
            self.fruit_models[self.index_fruit_dict[self.fruit_list[0]]].setStashed(False)
        #print 'banana gone', self.got_fruit
        #print self.stashed
        return find_banana_loc

    def replenish_stashed_fruit(self):
        print 'replenish'
        pos_list = []
        avatar = Avatar.Avatar.getInstance()
        avatarXY = (avatar.getPos()[0], avatar.getPos()[1])
        for i in range(self.num_fruit):
            #print pos_list
            if self.fruit_models[i].isStashed():
                #print 'banana stashed, unstash now'
                (x, y) = mB.setXY(pos_list, avatarXY)
                pos_list.append((x, y))
                #print x, y
                self.fruit_models[i].setPos(Point3(x, y, 1))
                # make new bananas visible
                self.fruit_models[i].setStashed(False)
            else:
                # for bananas not replacing, get current banana position, so we
                # don't put them too close together
                pos_list.append((self.fruit_models[i].getPos()[0], self.fruit_models[i].getPos()[1]))

