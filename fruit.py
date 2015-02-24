from pandaepl import Model, MovingObject, Avatar, VideoLogQueue, Camera
from panda3d.core import Point3, TransparencyAttrib
from load_models import load_models, get_model
import moBananas as mB
import random
from sys import stdout


def check_repeat(trial_num, original_list):
    # used in gobananas
    # this function decides what kind of trial we are setting up,
    # if starting a new block of trials will decide which one will
    # be the new repeat trial. Do this first, in case this trial
    # (first of new block) is going to be the repeat
    repeat_list = original_list[:]
    trial_type = ''
    if trial_num > 0 and trial_num % repeat_list[0] == 0:
        # time to choose the next trial that will be a repeat,
        # choose a number from 0 to repeat number and add it to this trial number
        repeat_list[2] = trial_num + random.choice(range(repeat_list[0]))
        # print('chose trial', repeat_list[2])
        # if we are on a now_repeat trial, and now the trial number is less than repeat number,
        # it is the first one and we are collecting
    if trial_num == repeat_list[1]:
        # repeat_list[1] is the trial number for collecting positions
        # print 'collecting positions for repeat'
        trial_type = 'new'
    elif trial_num == repeat_list[2]:
        # and now we are repeating
        # print 'repeat'
        trial_type = 'repeat'
    return repeat_list, trial_type


def create_alt_fruit_area(subarea_key, alt_subarea=None):
    # alternate fruit can be directed to a specific subarea, or can be
    # chosen automatically as any section except the one the recall fruit
    # is in.
    if alt_subarea:
        area_list = alt_subarea
    else:
        area_list = range(1, 10)
        area_list.remove(subarea_key)
    print('alternate fruit in area:', area_list)
    return area_list


class Fruit():
    def __init__(self, config):
        # Used in both goBananas and bananaRecall, sometimes referred to as regular
        # and sequential tasks, respectively.
        self.config = config
        # if this is not a sequential memory task, this might not be set
        self.config.setdefault('fruit_to_remember', False)
        if self.config['fruit_to_remember']:
            # print 'recall task'
            # give exact location according to dictionary in config
            self.manual = config.get('manual')
            # bring this into a variable, so we can toggle it.
            # repeats until given new area by default if manual,
            # if set that way for random
            if self.manual:
                self.repeat = True
            else:
                self.repeat = config['repeat_recall_fruit']
            self.subarea_key = config.get('subarea', 0)
            # print 'fruit init', self.manual, self.subarea_key
            self.new_subarea_key = None
            if self.subarea_key:
                self.new_subarea_key = True
            # print('subarea', self.subarea_key)
            self.alpha = self.config['alpha']
            # print('alpha', self.alpha)
            self.num_shows = 0
        else:
            self.subarea_key = None
            # for repeating a particular configuration
            # able to toggle this in bananaRecall, so making it a variable in both games to
            # simplify things.
            self.repeat = self.config.get('fruit_repeat', False)  # assume false if none provided
            if self.repeat:
                start_number = random.choice(range(self.config['repeat_number']))
                # repeat_list is a list of variables we care about for repeating trials
                # the first two will not change, last one changes each time we enter a new block
                # [frequency of repeat, start number, next number]
                self.repeat_list = [self.config['repeat_number'], start_number, start_number]

        if self.config.get('go_alpha', False):
            self.alpha = self.config['alpha']
            # print('alpha', self.alpha)
        if self.config.get('alpha', False):
            self.alpha_node_path = None
        self.alpha_fruit = False

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
                # differentiate the fruit we are remembering,
                # if we are doing recall_banana task
                if self.config['fruit_to_remember'] and item.name == self.config['fruit_to_remember']:
                    name = item.name
                # print name
                # create actual model
                self.create_fruit_model(item, name)
                # check if we are making a fruit semi-transparent
                # will choose the first fruit of the given type
                if test_alpha and item.name == test_alpha:
                    self.alpha_fruit = name
                    # print self.alpha_fruit
                    test_alpha = self.set_alpha_fruit(name, True)

        # if we are doing recall, set ability to use alpha
        if self.config['fruit_to_remember']:
            self.set_alpha_fruit(self.config['fruit_to_remember'])

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

    def setup_gobananas_trial(self, trial_num):
        trial_type = ''
        if self.repeat:
            self.repeat_list, trial_type = check_repeat(trial_num, self.repeat_list)
            # print('got stuff back', trial_type)
            # print('trial number to be repeated', self.repeat_list[1])
        avatar_x_y = self.log_new_trial(trial_type, trial_num)
        new_pos_dict = self.setup_fruit_for_trial(avatar_x_y, trial_type)
        self.change_positions(new_pos_dict)

    def setup_fruit_for_trial(self, avatar_x_y, repeat='No'):
        # print('repeat_trial_type', repeat)
        # print 'setup fruit for trial'
        # get positions for fruit
        # if repeat has 'repeat' in it, use same positions as before
        # if repeat is 'new', use new positions, save configuration
        # pos_list is used to make sure we are not putting fruit too close
        # together or too close to the avatar
        pos_list = []
        # pos_dict is returned so we have a dictionary of the new positions
        pos_dict = {}
        # make sure start with empty list
        self.fruit_list = []
        for name, fruit in self.fruit_models.iteritems():
            # print name
            # print pos_list
            # print('repeat', repeat)
            if repeat == 'repeat':
                # get x,y from the dictionary
                (x, y) = self.pos_dict[name]
            else:
                # get new positions
                (x, y) = mB.get_random_xy(pos_list, avatar_x_y, self.config)
                pos_list.append((x, y))
            # print pos_list
            # print('current positions', name, x, y)
            pos_dict[name] = (x, y)
            self.make_fruit_visible(name, repeat)
        if repeat == 'new':
            # print 'save new'
            # save new banana placements
            self.pos_dict = pos_dict
        # print pos_dict
        # print('fruit list', self.fruit_list)
        return pos_dict

    def setup_recall_trial(self, trial_num):
        # print('recall_repeat this trial is', self.repeat)
        # repeat_recall can be toggled with button press
        # only go to new place after have been to old place for at least one
        # alpha or invisible showing
        # need trial_type for determining if repeating, new manual position
        # or new random position:
        # need to return remember = True, if banana is not full bright (will be searching)
        #
        # print 'setup recall trial'
        # print self.new_subarea_key
        # print self.num_shows
        remember = False
        if self.num_shows == self.config['num_repeat_visible']:
            # first trial after required visible repeats is required,
            # and is always a repeat
            # always alpha if set in config
            remember = True
            if self.config.get('first_fruit_alpha', True):
                trial_type = 'repeat_alpha'
            else:
                trial_type = 'repeat'
        elif self.num_shows > self.config['num_repeat_visible']:
            print 'okay to change areas'
            # okay to change position
            if self.new_subarea_key:
                self.num_shows = 0
                trial_type = 'manual_bright'
            elif not self.manual and not self.repeat:
                self.num_shows = 0
                trial_type = 'random_bright'
            else:
                trial_type = 'repeat'
                remember = True
        elif self.repeat and self.pos_dict:
            # this is repeat because required, so always full bright,
            print 'repeating same place, make bright'
            trial_type = 'repeat_bright'
        else:
            print 'new'
            if self.new_subarea_key:
                trial_type = 'manual_bright'
                self.num_shows = 0
            else:
                trial_type = 'random_bright'
                self.num_shows = 0
        print('trial type', trial_type)
        self.num_shows += 1
        avatar_x_y = self.log_new_trial(trial_type, trial_num)
        new_pos_dict = self.setup_fruit_for_recall_trial(avatar_x_y, trial_type)
        self.change_positions(new_pos_dict)
        return remember

    def setup_fruit_for_recall_trial(self, avatar_x_y, repeat='No'):
        # print('repeat_trial_type', repeat)
        # print 'setup fruit for trial'
        # get positions for fruit
        # if repeat has 'repeat' in it, use same positions as before
        # (for recall this only applies to the recall fruit)
        # if repeat is 'recall' with no repeat, get a new position for
        # the recall fruit, from appropriate area

        # fruit_list is
        # pos_list is used to make sure we are not putting fruit too close
        # together or too close to the avatar
        pos_list = []

        # pos_dict is returned, giving us a dictionary of the new positions
        # so that we can move the fruit to the appropriate places.
        pos_dict = {}
        # make sure start with empty list
        self.fruit_list = []
        # if we are repeating the recall fruit, need to
        # keep track, so random positions are placed
        # proper distance from it
        if 'repeat' in repeat:
            # we have a position saved, so go ahead and
            # add it to the starting list, so other fruit
            # is not assigned too close to it.
            pos_list.append(self.pos_dict[self.config['fruit_to_remember']])
        elif 'manual' in repeat:
            # print 'switch subareas'
            # we switched subareas
            self.subarea_key = self.new_subarea_key
            self.new_subarea_key = None
            # since specific x, y, go ahead and add to list
            pos_list.append(self.config['points'].get(self.subarea_key))
        # get alt_area
        alt_area = create_alt_fruit_area(self.subarea_key)
        # print pos_list
        # print 'avatar pos', avatar_x_y
        for name, fruit in self.fruit_models.iteritems():
            # print name
            # print pos_list
            # print('repeat', repeat)
            if name == self.config['fruit_to_remember']:
                if 'repeat' in repeat:
                    # print 'repeat the same position for the banana again'
                    # if not a new position, put in the recall fruit position
                    # we used previously, already added to pos_list, so good.
                    (x, y) = self.pos_dict[name]
                else:
                    # print 'new recall fruit position'
                    # print self.manual
                    # print self.subarea_key
                    # getting a new position
                    # send in config with sub areas
                    if 'manual' in repeat:
                        print('switching placement', self.subarea_key)
                        # print self.config['points']
                        (x, y) = self.config['points'].get(self.subarea_key)
                    else:
                        # print 'get random'
                        (x, y) = mB.get_random_xy(pos_list, avatar_x_y, self.config, [self.subarea_key])
                    pos_list.append((x, y))
                    # always be ready to repeat recall fruit, cheap
                    self.pos_dict[name] = (x, y)
                    # make sure we know to show it, since not a repeat
                # print('recall fruit position', x, y)
            else:
                # fruit not remembering is in alternate area, if we have specified an area for the recall
                # fruit
                (x, y) = mB.get_random_xy(pos_list, avatar_x_y, self.config, alt_area)
                pos_list.append((x, y))
            # print pos_list
            # print('current positions', name, x, y)
            pos_dict[name] = (x, y)
            self.make_fruit_visible(name, repeat)
        # print pos_dict
        # print('fruit list', self.fruit_list)
        return pos_dict

    def log_new_trial(self, trial_type, trial_num):
        stdout.write('trial number ' + str(trial_num) + '\n')
        # print('trial_type', trial_type)
        VideoLogQueue.VideoLogQueue.getInstance().writeLine("NewTrial", [trial_num])
        if trial_type == 'new' or 'repeat' in trial_type:
            # print trial_type
            # print 'log repeat'
            VideoLogQueue.VideoLogQueue.getInstance().writeLine("RepeatTrial", [trial_num])
        avatar = Avatar.Avatar.getInstance()
        avatar_x_y = (avatar.getPos()[0], avatar.getPos()[1])
        return avatar_x_y

    def change_positions(self, pos_dict):
        for key, value in pos_dict.iteritems():
            self.fruit_models[key].setPos(Point3(value[0], value[1], 1))

    def make_fruit_visible(self, name, repeat=None):
        # print 'choose_first_fruit', choose_first_fruit
        # fruit indexes are given one at a time,
        # if task is remembering fruit,
        # create a list of fruit we will be showing consecutively 
        # after the first fruit, first fruit is visible
        # else (for goBananas) make all fruit visible
        recall_fruit = self.config['fruit_to_remember']
        if recall_fruit:
            if name == recall_fruit:
                # decide if we have shown required number of times at full bright.
                if 'bright' in repeat:
                    # first x trials solid on, set in config how many
                    # print 'on solid'
                    self.change_alpha_fruit('on')
                elif 'alpha' in repeat and self.alpha == 0:
                    # get alpha from config
                    print 'reset recall fruit alpha'
                    self.alpha = self.config['alpha']
                    self.change_alpha_fruit('on_alpha')
                elif self.alpha > 0:
                    # if alpha is on, use alpha
                    print 'recall fruit alpha'
                    self.change_alpha_fruit('on_alpha')
                else:
                    print 'recall fruit invisible'
                    self.change_alpha_fruit('off')
                self.fruit_list.append(name)
            else:
                self.fruit_list.append(name)
        else:
            # go bananas
            if name == self.alpha_fruit:
                self.change_alpha_fruit('on_alpha', name)
            self.fruit_models[name].setStashed(False)
            self.fruit_list.append(name)

    def set_alpha_fruit(self, name, alpha=None):
        # set up fruit to be alpha, may also change alpha
        # immediately, if alpha is true
        self.alpha_node_path = self.fruit_models[name].retrNodePath()
        self.alpha_node_path.setTransparency(TransparencyAttrib.MAlpha)
        if alpha:
            print('make a fruit alpha', name, self.config['alpha'])
            self.alpha_node_path.setAlphaScale(self.config['alpha'])
            # log it
            VideoLogQueue.VideoLogQueue.getInstance().writeLine("Alpha", [name + ' ' + str(self.config['alpha'])])
        return False  # only do one fruit

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
        # print self.fruit_list
        # remove the current fruit from list of possible fruit
        self.fruit_list.remove(self.current_fruit)
        # for gobananas, show how many fruit are left on field
        if not self.config['fruit_to_remember']:
            print('number of fruit left this trial ', len(self.fruit_list))
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
        # only for banana recall (sequential fruit!)
        # not used for goBananas
        # print 'get next fruit'
        # print 'fruit gone', self.current_fruit
        self.fruit_models[self.fruit_list[0]].setStashed(False)
        print('next fruit', self.fruit_list[0])

    def change_alpha_fruit(self, mode=None, fruit=None):
        # fruit default is the recall fruit
        # mode can be three states, on, alpha_on, off. Default is alpha_on
        if mode is None:
            mode = 'alpha_on'
        if fruit is None:
            fruit = self.config['fruit_to_remember']
        # for alpha, we only care if we are turning on alpha or on full,
        # if turning off, just leave in same state. Otherwise the logs will
        # be confusing with alpha changing when fruit disappears.
        if 'alpha' in mode:
            # print('should be on at this alpha ', self.alpha)
            self.alpha_node_path.setAlphaScale(self.alpha)
            # log what alpha we flashed at
            # print('alpha', self.alpha)
            # print('fruit', fruit)
            VideoLogQueue.VideoLogQueue.getInstance().writeLine("Alpha",
                                                                [fruit + ' ' + str(self.alpha)])
        elif 'on' in mode:
            # print('should be on at this alpha ', 1)
            self.alpha_node_path.setAlphaScale(1)
            # log we returned to full alpha, should be also stashed at this point,
            # but that is logged automatically
            VideoLogQueue.VideoLogQueue.getInstance().writeLine("Alpha",
                                                                [fruit + ' 1'])
        if 'on' in mode:
            # turn it on, should already be at correct alpha
            self.fruit_models[fruit].setStashed(False)
        else:
            self.fruit_models[fruit].setStashed(True)

    def choose_recall_position(self, subarea_key):
        print('new subarea key', subarea_key)
        self.new_subarea_key = subarea_key

    def check_distance_to_fruit(self, target_fruit):
        avatar = Avatar.Avatar.getInstance()
        avatar_pos = (avatar.getPos()[0], avatar.getPos()[1])
        banana = self.fruit_models[target_fruit]
        banana_pos = (banana.getPos()[0], banana.getPos()[1])
        dist_to_banana = mB.get_distance(avatar_pos, banana_pos)
        return dist_to_banana
