from pandaepl import Model, MovingObject, Avatar, VideoLogQueue, Camera
from panda3d.core import Point3, CollisionNode, CollisionSphere, TransparencyAttrib
from load_models import load_models, get_model
import moBananas as mB
import random


class Fruit():
    def __init__(self, config):

        # Do all of this prior to calling class, send in two lists,
        # fruit_types and num_fruit_types
        self.config = config

        # if this is not a sequential memory task, this might not be set
        self.config.setdefault('fruit_to_remember', False)

        # fruit not remembering - these will be adjusted, so make into variables
        all_fruit = config['fruit']  # list of fruit
        num_fruit = config['num_fruit']  # list corresponding to list above
        self.repeat_recall = False

        if self.config['fruit_to_remember']:
            #print 'recall task'
            # if doing recall task, fruit to remember is always first
            all_fruit.insert(0, self.config['fruit_to_remember'])
            num_fruit.insert(0, 1)
            self.recall_node_path = None
            # bring this into a variable, so we can toggle it.
            self.repeat_recall = config['repeat_recall_fruit']
            self.all_subareas = mB.create_sub_areas(self.config)
            #print self.all_subareas
            self.fruit_area = [{}]
            self.create_fruit_area_dict(self.config['subarea'])
            self.alpha = self.config['alpha']
        else:
            self.fruit_area = [{}]
            self.create_fruit_area_dict(0)

        # for repeating a particular configuration
        self.repeat = config.get('fruit_repeat', False)  # assume false if none provided
        if self.repeat:
            self.repeat_number = config['repeat_number']  # how often to repeat
            self.now_repeat = random.choice(range(self.repeat_number))  # choose which trial we are repeating
            print('collect fruit positions from trial', self.now_repeat)
            self.repeat = self.now_repeat  # remember which trial we have repeated
        else:
            self.now_repeat = None  # never repeat

        # index_fruit_dict keeps track of which index number in the fruit_model list corresponds to which
        # name/model, because this is easier than running a for loop every time to find the one
        # we want. What if I just put the models in a dictionary in the first place? Hmmm...
        #self.index_fruit_dict = {}
        # num_fruit dict tells us how many of each fruit we will be showing
        self.num_fruit_dict = {}
        # dictionary of actual fruit models
        self.fruit_models = {}
        # list to keep track of which fruit have shown up
        self.fruit_list = []
        #self.stashed = self.num_fruit
        self.beeps = None
        self.first_collision = True
        # variable to save the fruit we ran into most recently
        self.current_fruit = None
        # dictionary to save positions for repeated trials or single fruit
        self.pos_dict = {}
        # for testing can send in a list, for recall, just where the banana
        # is, for non-sequential tasks, need one position for each fruit
        #self.pos_list = [5, -5]

    def create_fruit(self, fruit_dict):
        self.num_fruit_dict = fruit_dict
        # return a fruitModel.
        #print 'create bananas'
        #print start
        #print 'dict of number fruit', fruit_dict
        # load the models
        load_models()
        # set counts
        model_count = 0
        # for each fruit in our dictionary, find corresponding model,
        # create new model for each count in dictionary of that fruit
        # This is a lot of loops, fortunately they are all small. Might
        # want to make a method for getting stuff out of PlaceModels.
        #print 'making fruit dictionary'
        for fruit, count in fruit_dict.iteritems():
            for i in range(count):
                item = get_model('name', fruit)
                #print item.model
                name = item.name + "%03d" % i
                # differentiate the fruit we are remembering, if we are doing
                # recall_banana task
                if self.config['fruit_to_remember'] and item.name == self.config['fruit_to_remember']:
                    name = item.name
                #print name
                # create actual model
                self.create_fruit_model(item, name)
                # if we haven't stuck this model in the dictionary yet, do it now
                # each model gets a unique number
                # why would the current model ever already have an entry?
                #self.index_fruit_dict[name] = self.index_fruit_dict.setdefault(name, model_count) + 1
                #print self.index_fruit_dict
                #self.index_fruit_dict[name] = model_count
                model_count += 1

        # if we are doing recall, set ability to use alpha
        if self.config['fruit_to_remember']:
            fruit_index = self.config['fruit_to_remember']
            self.recall_node_path = self.fruit_models[fruit_index].retrNodePath()
            self.recall_node_path.setTransparency(TransparencyAttrib.MAlpha)
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

        model.setHpr(Point3(random.randint(0, 360), 0, roll))
        model.setScale(item.scale)
        model.name = name
        #print('create fruit', name)

        model.retrNodePath().getChild(0).getChild(0).setScale(item.coll_scale)

        # hide all models on creation
        model.setStashed(True)
        self.fruit_models[name] = model
        #return model.name

    def setup_trial(self, trial_num):
        # trials are set up mostly the same, whether showing fruit sequentially or all at once.
        print('trial number', trial_num)
        print('trial number to be repeated', self.repeat)
        # self.repeat only refers to regular trials, not sequential trials
        if self.repeat:
            # first check to see if we are choosing a new trial
            # number for repeat.
            if trial_num > 0:
                print trial_num % self.repeat_number
            if trial_num > 0 and trial_num % self.repeat_number == 0:
                # time to choose the next trial that will be a repeat,
                # choose a number from 0 to repeat number and add it to this trial number
                self.now_repeat = trial_num + random.choice(range(self.repeat_number))
                print('chose trial', self.now_repeat)
            # if we are on a now_repeat trial, and now the trial number is less than repeat number,
            # it is the first one and we are collecting
            if trial_num == self.repeat:
                # self.repeat is the trial number for collecting positions
                #print 'collecting positions for repeat'
                VideoLogQueue.VideoLogQueue.getInstance().writeLine("RepeatTrial", [trial_num])
                self.setup_fruit_for_trial('new')
            elif trial_num == self.now_repeat:
                # and now we are repeating
                #print 'repeat'
                VideoLogQueue.VideoLogQueue.getInstance().writeLine("RepeatTrial", [trial_num])
                self.setup_fruit_for_trial('repeat')
            else:
                self.setup_fruit_for_trial()
        else:
            if self.config['fruit_to_remember']:
                # repeat_recall can be toggled with button press
                if self.repeat_recall:
                    self.setup_fruit_for_trial('recall_repeat')
                else:
                    self.setup_fruit_for_trial('recall')
            else:
                self.setup_fruit_for_trial()
        VideoLogQueue.VideoLogQueue.getInstance().writeLine("NewTrial", [trial_num])

    def setup_fruit_for_trial(self, repeat='No'):
        #print 'setup fruit for trial'
        # get positions for fruit
        # if repeat has 'repeat' in it, use same positions as before
        # (for recall this is only the recall fruit)
        # if repeat is 'new', use new positions
        # if repeat is 'recall' with no repeat, use the proper
        # dictionary entry in self.pos_dict for the recall fruit
        # if repeat is 'new' save the configuration creating now
        # pos_list is used to make sure we are not putting fruit too close
        # together. 
        pos_list = []
        # make sure start with empty list
        self.fruit_list = []
        # if we are repeating the recall fruit, need to
        # do keep track, so random positions are placed
        # proper distance from it, and for sequence order
        first_show = False
        if repeat == 'recall_repeat':
            # variable to identify which fruit to show first
            first_show = 'random'
            # want to repeat the location, but doesn't work
            # if there is no location saved.
            print 'repeating recall fruit'
            if self.pos_dict:
                # we have a position saved, so go ahead and
                # add it to the starting list, so other fruit
                # is not assigned too close to it.
                pos_list.append(self.pos_dict[self.config['fruit_to_remember']])
            else:
                print 'but no positions to recall'
                repeat = 'recall'
                first_show = self.config['fruit_to_remember']
        #print pos_list
        avatar = Avatar.Avatar.getInstance()
        avatar_x_y = (avatar.getPos()[0], avatar.getPos()[1])
        # print 'avatar pos', avatar_x_y

        for name, fruit in self.fruit_models.iteritems():
            print name
            #print pos_list
            if repeat == 'repeat':
                # only do this for regular task, not recall
                (x, y) = self.pos_dict[name]
            elif name == self.config['fruit_to_remember']:
                if 'repeat' in repeat:
                    print 'repeat the same position for the banana again'
                    # if not a new position, put in the recall fruit position
                    # we used previously, already added to pos_list, so good.
                    (x, y) = self.pos_dict[name]
                else:
                    print 'new recall fruit position'
                    # getting a new position
                    # send in config with sub areas
                    (x, y) = mB.set_xy(pos_list, avatar_x_y, self.fruit_area[0])
                    pos_list.append((x, y))
                    # always be ready to repeat recall fruit, cheap
                    self.pos_dict[name] = (x, y)
                    # make sure we know to show it, since not a repeat
                #print('recall fruit position', x, y)
            else:
                # will use whole area if gobananas: the last area
                # is the only self.fruit_area.
                # in this else for recall we are only dealing with
                # the fruit not remembering, which is always the
                # last index in the self.fruit_area
                #print self.fruit_area
                #print self.fruit_area[-1]
                (x, y) = mB.set_xy(pos_list, avatar_x_y, self.fruit_area[-1])
                pos_list.append((x, y))
            #print pos_list
            print('current positions', name, x, y)
            self.fruit_models[name].setPos(Point3(x, y, 1))
            started = self.make_fruit_visible(name, first_show)
            if started == 'Done':
                first_show = False
            # add to our list, except for the recall fruit,
            # if we aren't showing it
            #if show_fruit or fruit != self.config['fruit_to_remember']:
            #    print "add", fruit
            #    
            if repeat == 'new':
                #print 'save new'
                # save new banana placements
                self.pos_dict[name] = (x, y)
        print('fruit list', self.fruit_list)    

    def make_fruit_visible(self, name, first_show=None):
        print 'first_show', first_show
        # fruit indexes are given one at a time,
        # if task is remembering fruit,
        # make all fruit except first fruit visible
        # else (for goBananas) make all fruit visible
        recall_fruit = self.config['fruit_to_remember']
        if recall_fruit:
            # if first_show is a name, this is the first fruit to show
            # normally we start with the fruit to remember, but if we are doing
            # it in the same place every time, then subject will be in that
            # place already, and makes no sense. So show it once at a given
            # position, then not again until it moves again.
            first = False
            if name == recall_fruit == first_show:
                first = True
            elif first_show == 'random':
                first = True
            if first:
                print('show this fruit first!', name)
                self.fruit_models[name].setStashed(False)
                self.fruit_list.append(name)
                first_show = 'Done'
            elif name == recall_fruit:
                print("don't show the recall fruit this trial", name)
                # don't show the recall fruit this trial!
                self.fruit_models[name].setStashed(True)
            else:
                print('show this fruit eventually', name)
                # eventually show this fruit
                self.fruit_list.append(name)
        else:
            self.fruit_models[name].setStashed(False)
            self.fruit_list.append(name)
        return first_show
            
    def collide_fruit(self, collision_info):
        """
        Handle the subject colliding with fruit, document fruit collision, subject
        freezes, reward is triggered.
        @param collision_info:
        @return:
        """
        print 'collision'
        #print 'what is first_collision now?', self.first_collision
        # which fruit we ran into
        self.current_fruit = collision_info[0].getInto().getIdentifier()
        #print('collision', self.current_fruit)
        #print self.first_collision
        # check to see if the banana was in the camera view when collided,
        # if not, then ignore collision
        collided = collision_info[0].getInto()
        cam_node_path = Camera.Camera.getDefaultCamera().retrNodePath()
        #print collided.retrNodePath().getPos(cam_node_path)
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
            #print 'first collision, in view'
            #print self.current_fruit
            # cannot run inside of banana - can't I just do this earlier for all of the fruit?
            MovingObject.MovingObject.handleRepelCollision(collision_info)
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
        #print 'disappear fruit'
        # fruit that is currently visible is stashed
        #print('fruit should go away', self.current_fruit)
        #current_index = self.index_fruit_dict[self.current_fruit]
        #print('this fruit index', current_index)

        # remove the current fruit from list of possible fruit
        self.fruit_list.remove(self.current_fruit)
        print 'removed a fruit from the list', self.fruit_list
        # stash the fruit we just ran into,
        self.fruit_models[self.current_fruit].setStashed(True)
        self.reset_collision()

    def reset_collision(self):
        # log collected banana
        VideoLogQueue.VideoLogQueue.getInstance().writeLine("Finished", [self.current_fruit])
        self.first_collision = True

    def get_next_fruit(self):
        print 'get next fruit'
        print 'fruit list, if empty, remembering', self.fruit_list
        # not used for goBananas
        # if we are doing fruit sequentially, go to the next one
        # default is not time to find the banana memory
        find_banana_loc = False
        # know it is time to search for location, when we have made it through all
        # of the fruit
        # unstash the next fruit, unless it is time to go to the remembered banana
        # (list is empty)
        if not self.fruit_list:
            # if we are searching for the banana, send find_banana as true
            # if banana is going to be partially visible, turn it on
            if self.alpha > 0:
                #print 'flash recall fruit'
                self.flash_recall_fruit(True)
            find_banana_loc = True
            #print 'remember banana'
        else:
            #print('whole dict', self.index_fruit_dict)
            #print('next fruit in list', self.fruit_list[0])
            #print('next fruit in dict', self.index_fruit_dict[self.fruit_list[0]])
            #print self.fruit_models[self.index_fruit_dict[self.fruit_list[0]]].getPos()
            self.fruit_models[self.fruit_list[0]].setStashed(False)
        #print 'banana gone', self.current_fruit
        #print self.stashed
        return find_banana_loc

    def flash_recall_fruit(self, flash):
        # flash the fruit the subject is/was suppose to find
        # flash is true or false, depending on whether we are turning it on or off,
        # makes more sense for true to turn on fruit and false turn off, so invert signal
        #print('flash ', flash)
        self.fruit_models[self.config['fruit_to_remember']].setStashed(not flash)
        if flash:
            self.recall_node_path.setAlphaScale(self.alpha)
        else:
            self.recall_node_path.setAlphaScale(1)
        #print('index for recall fruit', self.index_fruit_dict[self.config['fruit_to_remember']])
        #print self.fruit_models[self.index_fruit_dict[self.config['fruit_to_remember']]].getPos()
        
    def create_fruit_area_dict(self, subarea_key):
        #print('created new dictionary')
        # Need to keep around the original size of the area, and I don't trust the pandaepl config
        # dictionary, because they have done weird things to scope, so create a new dictionary
        #print('key', subarea_key)
        # start with an empty dictionary every time
        self.fruit_area = [{}]
        if subarea_key == 0:
            #print 'key is zero'
            # don't get entire self.config dictionary, just bounds of courtyard
            self.fruit_area[0].update({'min_x': self.config['min_x'],
                                       'max_x': self.config['max_x'],
                                       'min_y': self.config['min_y'],
                                       'max_y': self.config['max_y']
                                       })
            #print self.fruit_area
        else:
            #print 'key is not zero'
            self.fruit_area[0].update(self.all_subareas[subarea_key])
            #print self.fruit_area

        self.fruit_area[0]['tooClose'] = self.config['tooClose']
        self.fruit_area[0]['avatarRadius'] = self.config['avatarRadius']
        self.fruit_area[0]['environ'] = self.config['environ']
        if 'circle' in self.config['environ']:
            self.fruit_area[0]['radius'] = self.config['radius']
        #print('after updating tooclose', self.fruit_area)

        #print self.fruit_area
        if subarea_key > 0:
            # also make a config dict for the other fruit
            size_area = self.create_alt_fruit_area(subarea_key)
            self.fruit_area.append({'min_x': min([self.all_subareas[i]['min_x'] for i in size_area]),
                                    'max_x': max([self.all_subareas[i]['max_x'] for i in size_area]),
                                    'min_y': min([self.all_subareas[i]['min_y'] for i in size_area]),
                                    'max_y': max([self.all_subareas[i]['max_y'] for i in size_area]),
                                    'tooClose': self.config['tooClose'],
                                    'avatarRadius': self.config['avatarRadius'],
                                    'environ': self.config['environ']})
        # make sure we know we moved
        self.pos_list = []

    def create_alt_fruit_area(self, subarea_key):
        # plum can be in same area as banana, or one section away
        # could probably come up with some algorithm for this, but
        # couldn't be bothered.
        if subarea_key == 1:
            area_list = [1, 2, 4, 5]
        elif subarea_key == 2:
            area_list = [1, 2, 3, 4, 5, 6]
        elif subarea_key == 3:
            area_list = [2, 3, 5, 6]
        elif subarea_key == 4:
            area_list = [1, 2, 4, 5, 7, 8]
        elif subarea_key == 5:
            area_list = [0]
        elif subarea_key == 6:
            area_list = [2, 3, 5, 6, 8, 9]
        elif subarea_key == 7:
            area_list = [4, 5, 7, 8]
        elif subarea_key == 8:
            area_list = [4, 5, 6, 7, 8, 9]
        elif subarea_key == 9:
            area_list = [5, 6, 8, 9]
        else:
            area_list = []
        return area_list
