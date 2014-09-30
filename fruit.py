from pandaepl import Model, MovingObject, Avatar, VideoLogQueue, Camera
from panda3d.core import Point3, CollisionNode, CollisionSphere
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
        self.repeat_recall = False

        if self.fruit_to_remember:
            self.all_fruit.insert(0, self.fruit_to_remember)
            self.num_fruit.insert(0, 1)
            self.repeat_recall = config['repeat_recall_fruit']

        # for repeating a particular configuration
        self.repeat = config['fruit_repeat']
        self.repeat_number = config['repeat_number']
        if self.repeat:
            self.now_repeat = random.choice(range(self.repeat_number))
            print('collect fruit positions from trial', self.now_repeat)
            self.repeat = self.now_repeat
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
        self.first_collision = True
        # variable to save the fruit we ran into most recently
        self.current_fruit = None
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
                #print item.model
                name = item.name + "%03d" % i
                # differentiate the fruit we are remembering, if we are doing
                # recall_banana task
                if self.fruit_to_remember and item.name == self.fruit_to_remember:
                    name = item.name
                #print name
                # create actual model
                self.create_fruit_model(item, name)
                # if we haven't stuck this model in the dictionary yet, do it now
                if name not in self.index_fruit_dict:
                    self.index_fruit_dict[name] = model_count
                model_count += 1

        #print self.index_fruit_dict
        #print self.fruit_models
        #print 'end create fruit'

    def create_fruit_model(self, item, name):
        # initial position does not matter
        model = Model.Model(name, item.model, Point3(0, 0, 1), self.collide_fruit)
        try:
            roll = item.roll
        except AttributeError:
            roll = 0
        #roll = 75
        model.setHpr(Point3(random.randint(0, 360), 0, roll))
        model.setScale(item.scale)
        model.name = name
        #print name
        try:
            #print(item.coll_pos)
            x, y, z, s = item.coll_pos
            model_sphere = CollisionSphere(x, y, z, s)
            model.nodePath.attachNewNode(CollisionNode('CollisionSphere'))
            model.retrNodePath().getChild(1).node().addSolid(model_sphere)
            #model.retrNodePath().getChild(1).show()
            #print(model.retrNodePath().getChild(1))
            #print(model.retrNodePath().getChild(1).node())
        except AttributeError:
            model.retrNodePath().getChild(0).getChild(0).setScale(item.coll_scale)
            #model.retrNodePath().getChild(0).getChild(0).show()
            #print(model.retrNodePath().getChild(0).getChild(0))
        #print(model.retrNodePath().getChild(0))
        #print(model.retrNodePath().getChild(0).node())

        #print(model.retrNodePath().getChild(0).getChild(0))
        #print(model.retrNodePath().getChild(0).getChild(0).node())
        #model.retrNodePath().getChild(0).show()

        # hide all models on creation
        model.setStashed(True)
        self.fruit_models.append(model)
        return model.name

    def setup_fruit_for_trial(self, repeat=None):
        # calculate positions for fruit
        #print('fruit_list', self.fruit_list)
        print('num_fruit', self.num_fruit)
        # if repeat is 'repeat', use saved configuration
        # if repeat is 'new' save the configuration creating now
        pos_list = []
        if repeat == 'recall' and not self.pos_list:
            repeat = 'new'
        if repeat == 'repeat' or repeat == 'recall':
            old_list = self.pos_list
        #print pos_list
        avatar = Avatar.Avatar.getInstance()
        avatarXY = (avatar.getPos()[0], avatar.getPos()[1])
        # print 'avatar pos', avatarXY
        for fruit, index in self.index_fruit_dict.iteritems():
            print fruit, index
            #print pos_list
            if repeat == 'repeat':
                (x, y) = old_list[index]
            elif repeat == 'recall' and fruit == self.fruit_to_remember:
                print 'just repeating the fruit to remember'
                (x, y) = old_list[index]
                pos_list.append((x, y))
            else:
                (x, y) = mB.set_xy(pos_list, avatarXY)
                pos_list.append((x, y))
            #print x, y
            self.fruit_models[index].setPos(Point3(x, y, 1))
            self.make_fruit_visible(index)
            # add to our list
            self.fruit_list.append(fruit)
        #print self.fruit_list
        print pos_list

        if repeat == 'new':
            print 'save new'
            # save the current list of random banana placements
            self.pos_list = pos_list
        #self.stashed = self.num_fruit

    def make_fruit_visible(self, index):
        # if task is remembering fruit,
        # make all fruit except one to be remembered not-visible
        if self.fruit_to_remember:
            self.fruit_models[index].setStashed(True)
            if self.fruit_models[index].name == self.fruit_to_remember:
                self.fruit_models[index].setStashed(False)
        else:
            self.fruit_models[index].setStashed(False)

    def collide_fruit(self, collisionInfoList):
        """
        Handle the subject colliding with fruit, document fruit collision, subject
        freezes, reward is triggered.
        @param collisionInfoList:
        @return:
        """
        #print 'collision'
        # which fruit we ran into
        self.current_fruit = collisionInfoList[0].getInto().getIdentifier()
        #print self.current_fruit
        # check to see if the banana was in the camera view when collided,
        # if not, then ignore collision
        collided = collisionInfoList[0].getInto()
        cam_node_path = Camera.Camera.getDefaultCamera().retrNodePath()
        #print collided.retrNodePath().getPos(cam_node_path)
        #print cam_node_path.node().isInView(collided.retrNodePath().getPos(cam_node_path))
        # Sometimes we collide with a banana multiple times for no damn reason, so setting self.first_collision
        # to keep track of whether this is the first collision
        #print('collision', self.first_collision)
        #print('camera', Camera.Camera.getDefaultCamera().getPos())
        #print('collision position', collided.retrNodePath().getPos(cam_node_path))
        #for fruit in self.fruit_models:
        #    print fruit.getPos()
        #print('in view', cam_node_path.node().isInView(collided.retrNodePath().getPos(cam_node_path)))
        if cam_node_path.node().isInView(collided.retrNodePath().getPos(cam_node_path)) and self.first_collision:
        #if self.first_collision:
            #print self.current_fruit
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
            self.first_collision = False

    def disappear_fruit(self):
        #print('fruit should go away', self.current_fruit)
        current_index = self.index_fruit_dict[self.current_fruit]
        #print('this fruit index', current_index)

        # remove the current fruit from list of possible fruit
        self.fruit_list.remove(self.current_fruit)
        # stash the fruit we just ran into,
        self.fruit_models[current_index].setStashed(True)
        # log collected banana
        VideoLogQueue.VideoLogQueue.getInstance().writeLine("Finished", [self.current_fruit])
        self.first_collision = True

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
        #print 'banana gone', self.current_fruit
        #print self.stashed
        return find_banana_loc

    def setup_trial(self, trial_num):
        print('trial number', trial_num)
        print('trial number to be repeated', self.repeat)
        if self.repeat:
            # first check to see if we are choosing a new trial number for repeat.
            if trial_num > 0 and trial_num % self.repeat_number == 0:
                # time to choose the next trial that will be a repeat,
                # choose a number from 0 to repeat number and add it to this trial number
                self.now_repeat = trial_num + random.choice(range(self.repeat_number))
                print('chose trial', self.now_repeat)
            # if we are on a now_repeat trial, and now the trial number is less than repeat number,
            # it is the first one and we are collecting
            if trial_num == self.repeat:
                # self.repeat is the trial number for collecting positions
                print 'collecting positions for repeat'
                VideoLogQueue.VideoLogQueue.getInstance().writeLine("RepeatTrial", [trial_num])
                self.setup_fruit_for_trial('new')
            elif trial_num == self.now_repeat:
                # and now we are repeating
                print 'repeat'
                VideoLogQueue.VideoLogQueue.getInstance().writeLine("RepeatTrial", [trial_num])
                self.setup_fruit_for_trial('repeat')
            else:
                self.setup_fruit_for_trial()
        else:
            if self.repeat_recall:
                self.setup_fruit_for_trial('recall')
            else:
                self.setup_fruit_for_trial()
        VideoLogQueue.VideoLogQueue.getInstance().writeLine("NewTrial", [trial_num])

    def replenish_stashed_fruit(self):
        print 'replenish'
        pos_list = []
        avatar = Avatar.Avatar.getInstance()
        avatarXY = (avatar.getPos()[0], avatar.getPos()[1])
        for i in range(self.num_fruit):
            #print pos_list
            if self.fruit_models[i].isStashed():
                #print 'banana stashed, unstash now'
                (x, y) = mB.set_xy(pos_list, avatarXY)
                pos_list.append((x, y))
                #print x, y
                self.fruit_models[i].setPos(Point3(x, y, 1))
                # make new bananas visible
                self.fruit_models[i].setStashed(False)
            else:
                # for bananas not replacing, get current banana position, so we
                # don't put them too close together
                pos_list.append((self.fruit_models[i].getPos()[0], self.fruit_models[i].getPos()[1]))

