from pandaepl import Model, MovingObject, Avatar, VideoLogQueue, Camera
from panda3d.core import Point3, TransparencyAttrib
from load_models import load_models, get_model
import moBananas as mB
import random
from sys import stdout


def check_repeat(trial_num, repeat_list):
    # this function decides what kind of trial we are setting up,
    # if starting a new block of trials will decide which one will
    # be the new repeat trial. Do this first, in case this trial
    # (first of new block) is going to be the repeat
    fruit_trial = ''
    if trial_num > 0 and trial_num % repeat_list[0] == 0:
        # time to choose the next trial that will be a repeat,
        # choose a number from 0 to repeat number and add it to this trial number
        repeat_list[2] = trial_num + random.choice(range(repeat_list[0]))
        # print('chose trial', repeat_list[2])
        # if we are on a now_repeat trial, and now the trial number is less than repeat number,
        # it is the first one and we are collecting
    if trial_num == repeat_list[1]:
        # self.repeat is the trial number for collecting positions
        # print 'collecting positions for repeat'
        fruit_trial = 'new'
    elif trial_num == repeat_list[2]:
        # and now we are repeating
        # print 'repeat'
        fruit_trial = 'repeat'
    return repeat_list, fruit_trial


def create_alt_fruit_area(subarea_key):
    # alternate fruit can be in same area as banana, or one section away
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
            # print 'recall task'
            # if doing recall task, fruit to remember is always first
            all_fruit.insert(0, self.config['fruit_to_remember'])
            num_fruit.insert(0, 1)
            self.recall_node_path = None
            # bring this into a variable, so we can toggle it.
            self.repeat_recall = config['repeat_recall_fruit']
            self.all_subareas = mB.create_sub_areas(self.config)
            # print self.all_subareas
            self.fruit_area = [{}]
            self.create_fruit_area_dict(self.config['subarea'])
            self.alpha = self.config['alpha']
        else:
            self.fruit_area = [{}]
            self.create_fruit_area_dict(0)

        # for repeating a particular configuration
        self.repeat = config.get('fruit_repeat', False)  # assume false if none provided
        if self.repeat:
            start_number = random.choice(range(config['repeat_number']))
            # repeat_list is a list of variables we care about for repeating trials
            # the first two will not change, last one changes each time we enter a new block
            # [frequency of repeat, start number, next number]
            self.repeat_list = [config['repeat_number'], start_number, start_number]

        # num_fruit dict will tell us how many of each fruit we will be showing
        self.num_fruit_dict = {}
        # dictionary of actual fruit models
        self.fruit_models = {}
        # list to keep track of which fruit have shown up
        self.fruit_list = []
        # keeps track of reward beeps
        self.beeps = None
        # variable to make sure we don't collide more than once into the same fruit
        self.first_collision = True
        # variable to save the fruit we ran into most recently
        self.current_fruit = None
        # dictionary to save positions for repeated trials or single fruit
        self.pos_dict = {}
        # for testing can send in a list, for recall, just where the banana
        # is, for non-sequential tasks, need one position for each fruit
        # self.pos_list = [5, -5]
        self.pos_list = []

    def create_fruit(self, fruit_dict):
        self.num_fruit_dict = fruit_dict
        # return a fruitModel.
        # print 'create bananas'
        # print 'dict of number fruit', fruit_dict
        # load the models
        load_models()
        # random alpha?
        test_alpha = self.config.get('go_alpha', False)
        # for each fruit in our dictionary, find corresponding model,
        # create new model for each count in dictionary of that fruit
        # This is a couple of loops, fortunately they are all small.
        # print 'making fruit dictionary'
        for fruit, count in fruit_dict.iteritems():
            for i in range(count):
                item = get_model('name', fruit)
                # print item.model
                name = item.name + "%03d" % i
                # differentiate the fruit we are remembering, if we are doing
                # recall_banana task
                if self.config['fruit_to_remember'] and item.name == self.config['fruit_to_remember']:
                    name = item.name
                print name
                # create actual model
                self.create_fruit_model(item, name)
                if test_alpha and item.name == test_alpha:
                    print('make a fruit 1/2 alpha', name)
                    # will choose the last banana created
                    random_node_path = self.fruit_models[name].retrNodePath()
                    random_node_path.setTransparency(TransparencyAttrib.MAlpha)
                    random_node_path.setAlphaScale(self.config['alpha'])
                    # log it
                    VideoLogQueue.VideoLogQueue.getInstance().writeLine("Alpha", [name + ' ' + str(self.config['alpha'])])
                    test_alpha = False  # only do one fruit

        # if we are doing recall, set ability to use alpha
        if self.config['fruit_to_remember']:
            fruit_index = self.config['fruit_to_remember']
            self.recall_node_path = self.fruit_models[fruit_index].retrNodePath()
            self.recall_node_path.setTransparency(TransparencyAttrib.MAlpha)
        # print self.fruit_models
        # print 'end create fruit'

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
        try:
            model.retrNodePath().getChild(0).getChild(0).setScale(item.coll_scale)
        except AssertionError:
            print "no collision sphere detected"
        # print model.retrNodePath().getChild(0).getChild(0).getChild(0)
        # uncomment to show collision sphere
        # model.retrNodePath().getChild(0).getChild(0).getChild(0).show()

        # hide all models on creation
        model.setStashed(True)
        self.fruit_models[name] = model
        
    def setup_trial(self, trial_num):
        # trials are set up mostly the same, whether showing fruit sequentially or all at once.
        stdout.write('trial number ' + str(trial_num) + '\n')
        # print('trial number to be repeated', self.repeat_list[1])
        fruit_trial = ''
        # self.repeat only refers to regular trials, not sequential trials
        if self.repeat:
            self.repeat_list, fruit_trial = check_repeat(trial_num, self.repeat_list)
            # print('got stuff back', fruit_trial)
        else:
            # print 'not repeating'
            if self.config['fruit_to_remember']:
                # repeat_recall can be toggled with button press
                # print('recall_repeat this trial is', self.repeat_recall)
                if self.repeat_recall:
                    fruit_trial = 'recall_repeat'
                else:
                    fruit_trial = 'recall'
        self.setup_fruit_for_trial(fruit_trial)
        VideoLogQueue.VideoLogQueue.getInstance().writeLine("NewTrial", [trial_num])
        if fruit_trial == 'new' or fruit_trial == 'repeat':
            # print 'log repeat'
            VideoLogQueue.VideoLogQueue.getInstance().writeLine("RepeatTrial", [trial_num])

    def setup_fruit_for_trial(self, repeat='No'):
        # print('repeat_fruit_trial', repeat)
        # print 'setup fruit for trial'
        # get positions for fruit
        # if repeat has 'repeat' in it, use same positions as before
        # (for recall this only applies to the recall fruit)
        # if repeat is 'new', use new positions, save configuration
        # if repeat is 'recall' with no repeat, get a new position for
        # the recall fruit, from appropriate area

        # pos_list is used to make sure we are not putting fruit too close
        # together or too close to the avatar
        pos_list = []
        # make sure start with empty list
        self.fruit_list = []
        # if we are repeating the recall fruit, need to
        # do keep track, so random positions are placed
        # proper distance from it
        if repeat == 'recall_repeat':
            # want to repeat the location, but doesn't work
            # if there is no location saved.
            # print 'repeating recall fruit'
            if self.pos_dict:
                # we have a position saved, so go ahead and
                # add it to the starting list, so other fruit
                # is not assigned too close to it.
                pos_list.append(self.pos_dict[self.config['fruit_to_remember']])
            else:
                # print 'but no positions to recall'
                repeat = 'recall'
        # print pos_list
        avatar = Avatar.Avatar.getInstance()
        avatar_x_y = (avatar.getPos()[0], avatar.getPos()[1])
        # print 'avatar pos', avatar_x_y
        for name, fruit in self.fruit_models.iteritems():
            # print name
            # print pos_list
            if repeat == 'repeat':
                # will only do this for regular task, not recall
                (x, y) = self.pos_dict[name]
            elif name == self.config['fruit_to_remember']:
                if 'repeat' in repeat:
                    # print 'repeat the same position for the banana again'
                    # if not a new position, put in the recall fruit position
                    # we used previously, already added to pos_list, so good.
                    (x, y) = self.pos_dict[name]
                else:
                    # print 'new recall fruit position'
                    # getting a new position
                    # send in config with sub areas
                    (x, y) = mB.set_xy(pos_list, avatar_x_y, self.fruit_area[0])
                    pos_list.append((x, y))
                    # always be ready to repeat recall fruit, cheap
                    self.pos_dict[name] = (x, y)
                    # make sure we know to show it, since not a repeat
                # print('recall fruit position', x, y)
            else:
                # will use whole area if gobananas: in this case, 
                # the last area is the only self.fruit_area.
                # for recall, we are only dealing here with
                # the fruit not remembering, which is always the
                # last index in the self.fruit_area
                # print self.fruit_area
                # print self.fruit_area[-1]
                (x, y) = mB.set_xy(pos_list, avatar_x_y, self.fruit_area[-1])
                pos_list.append((x, y))
            # print pos_list
            # print('current positions', name, x, y)
            self.fruit_models[name].setPos(Point3(x, y, 1))
            self.make_fruit_visible(name)
            # if we have decided on the first fruit, then 
            # won't have to figure this out next time through the loop
            # if started == 'Done':
            #     choose_first_fruit = False
            # repeat is only exactly 'new' for gobananas, so won't interfere
            # with recall task
            if repeat == 'new':
                # print 'save new'
                # save new banana placements
                self.pos_dict[name] = (x, y)
        # print('fruit list', self.fruit_list)

    def make_fruit_visible(self, name):
        # print 'choose_first_fruit', choose_first_fruit
        # fruit indexes are given one at a time,
        # if task is remembering fruit,
        # create a list of fruit we will be showing consecutively 
        # after the first fruit, first fruit is visible
        # else (for goBananas) make all fruit visible
        recall_fruit = self.config['fruit_to_remember']
        if recall_fruit:
            if name == recall_fruit:
                # always show the recall fruit first
                self.fruit_models[name].setStashed(False)
            self.fruit_list.append(name)
        else:
            self.fruit_models[name].setStashed(False)
            self.fruit_list.append(name)
            
    def collide_fruit(self, collision_info):
        """
        Handle the subject colliding with fruit, document fruit collision, subject
        freezes, reward is triggered.
        @param collision_info:
        @return:
        """
        # print 'collision'
        # print 'what is first_collision now?', self.first_collision
        # which fruit we ran into
        self.current_fruit = collision_info[0].getInto().getIdentifier()
        # print('collision', self.current_fruit)
        # print self.first_collision
        # check to see if the banana was in the camera view when collided,
        # if not, then ignore collision
        collided = collision_info[0].getInto()
        cam_node_path = Camera.Camera.getDefaultCamera().retrNodePath()
        # print collided.retrNodePath().getPos(cam_node_path)
        # print collided.retrNodePath().getPos(cam_node_path)
        # print cam_node_path.node().isInView(collided.retrNodePath().getPos(cam_node_path))
        # Sometimes we collide with a banana multiple times for no damn reason, so setting self.first_collision
        # to keep track of whether this is the first collision
        # print('collision', self.first_collision)
        # print('camera', Camera.Camera.getDefaultCamera().getPos())
        # print('collision position', collided.retrNodePath().getPos(cam_node_path))
        # for fruit in self.fruit_models:
        #     print fruit.getPos()
        # print('in view', cam_node_path.node().isInView(collided.retrNodePath().getPos(cam_node_path)))
        if cam_node_path.node().isInView(collided.retrNodePath().getPos(cam_node_path)) and self.first_collision:
            # print 'first collision, in view'
            # print self.current_fruit
            # cannot run inside of banana - can't I just do this earlier for all of the fruit?
            MovingObject.MovingObject.handleRepelCollision(collision_info)
            # print 'stop moving'
            # Makes it so Avatar cannot turn or go forward
            Avatar.Avatar.getInstance().setMaxTurningSpeed(0)
            Avatar.Avatar.getInstance().setMaxForwardSpeed(0)
            # VideoLogQueue.VideoLogQueue.getInstance().writeLine("Yummy", ['stop moving!'])
            # Setting self.beeps to 0 is signal to give reward
            self.beeps = 0
            # print self.beeps
            self.first_collision = False

    def disappear_fruit(self):
        # print 'disappear fruit'
        # fruit that is currently visible is stashed
        # print('fruit should go away', self.current_fruit)
        # print('this fruit index', current_index)

        # remove the current fruit from list of possible fruit
        self.fruit_list.remove(self.current_fruit)
        # print 'removed a fruit from the list', self.fruit_list
        # stash the fruit we just ran into,
        self.fruit_models[self.current_fruit].setStashed(True)
        self.reset_collision()

    def reset_collision(self):
        # print 'reset collision'
        # log collected banana
        VideoLogQueue.VideoLogQueue.getInstance().writeLine("Finished", [self.current_fruit])
        self.first_collision = True

    def get_next_fruit(self):
        # print 'get next fruit'
        # print 'fruit list, if empty, remembering', self.fruit_list
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
                # print 'flash recall fruit'
                self.flash_on_recall_fruit(True)
                find_banana_loc = None
            else:
                find_banana_loc = True
            # print 'remember banana'
        else:
            # print('next fruit in list', self.fruit_list[0])
            self.fruit_models[self.fruit_list[0]].setStashed(False)
        # print 'banana gone', self.current_fruit
        # print self.stashed
        return find_banana_loc

    def flash_on_recall_fruit(self, flash):
        # flash the fruit the subject is/was suppose to find
        # flash is true or false, depending on whether we are turning it on or off,
        # makes more sense for true to turn on fruit and false turn off, so invert signal
        # print('flash ', flash)
        recall_fruit = self.config['fruit_to_remember']
        self.fruit_models[recall_fruit].setStashed(not flash)
        if flash:
            self.recall_node_path.setAlphaScale(self.alpha)
            # log what alpha we flashed at
            VideoLogQueue.VideoLogQueue.getInstance().writeLine("Alpha", [recall_fruit + ' ' + str(self.alpha)])
        else:
            self.recall_node_path.setAlphaScale(1)
            # log we returned to full alpha, should be also stashed at this point,
            # but that is logged automatically
            VideoLogQueue.VideoLogQueue.getInstance().writeLine("Alpha", [recall_fruit + ' ' + str(1)])
        
    def create_fruit_area_dict(self, subarea_key):
        # print('created new dictionary')
        # Need to keep around the original size of the area, and I don't trust the pandaepl config
        # dictionary, because they have done weird things to scope, so create a new dictionary
        # print('key', subarea_key)
        # start with an empty dictionary every time
        self.fruit_area = [{}]
        if subarea_key == 0:
            # print 'key is zero'
            # don't get entire self.config dictionary, just bounds of courtyard
            self.fruit_area[0].update({'min_x': self.config['min_x'],
                                       'max_x': self.config['max_x'],
                                       'min_y': self.config['min_y'],
                                       'max_y': self.config['max_y']
                                       })
            # print self.fruit_area
        else:
            # print 'key is not zero'
            self.fruit_area[0].update(self.all_subareas[subarea_key])
            # print self.fruit_area

        self.fruit_area[0]['tooClose'] = self.config['tooClose']
        self.fruit_area[0]['avatarRadius'] = self.config['avatarRadius']
        self.fruit_area[0]['environ'] = self.config['environ']
        if 'circle' in self.config['environ']:
            self.fruit_area[0]['radius'] = self.config['radius']
        # print('after updating tooclose', self.fruit_area)

        # print self.fruit_area
        if subarea_key > 0:
            # also make a config dict for the other fruit
            size_area = create_alt_fruit_area(subarea_key)
            self.fruit_area.append({'min_x': min([self.all_subareas[i]['min_x'] for i in size_area]),
                                    'max_x': max([self.all_subareas[i]['max_x'] for i in size_area]),
                                    'min_y': min([self.all_subareas[i]['min_y'] for i in size_area]),
                                    'max_y': max([self.all_subareas[i]['max_y'] for i in size_area]),
                                    'tooClose': self.config['tooClose'],
                                    'avatarRadius': self.config['avatarRadius'],
                                    'environ': self.config['environ']})
        # make sure we know we moved
        self.pos_list = []
