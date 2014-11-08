from __future__ import division
from math import sqrt
import random
""" Functions for bananas that don't need PandaEPL, so can actually be tested reasonably!
Includes functions for testing distance, figuring out banana placement, and determining
reward level dependent on banana positions
"""


def get_distance(p0, p1):
    """
    (tuple, tuple) -> float
    Returns the distance between 2 points. p0 is a tuple with (x, y)
    and p1 is a tuple with (x1, y1), works with negative points
    """
    dist = sqrt((float(p0[0]) - float(p1[0]))**2 + (float(p0[1]) - float(p1[1]))**2)
    return dist


def get_random_xy(config):
    # get a random x and y coordinate
    environ = config['environ']
    if environ and 'circle' in environ:
        radius = config['radius']
        x, y = get_circle_point(radius)
    else:
        x = random.uniform(config['min_x'], config['max_x'])
        y = random.uniform(config['min_y'], config['max_y'])
    return x, y


def set_xy(pos_list, avatar=(0, 0), config = None):
    """
    (list) -> tuple
    Returns a point (x,y) that is more than the minimum distance set by tooClose
    in the config.py file from existing points in pos_list. Also cannot be too
    close to the avatar, which is at the origin in the beginning.
    This algorithm is pretty inefficient for large numbers of fruit, and should
    eventually be optimized.
    """
    if config is None:
        config = {}
        execfile('config.py', config)
    print('in set_xy', config)
    too_close = config['tooClose']
    dist_avatar = config['avatarRadius'] + too_close

    x, y = get_random_xy(config)
    #print('x, y', x, y)
    # check the distance to points already on the list and to the avatar
    if pos_list:
        for x1, y1 in pos_list:
            # if either too close to other bananas or avatar, get new points.
            if get_distance((x, y), (x1, y1)) < too_close or get_distance((x, y), avatar) < dist_avatar:
                #print 'set xy too close'
                #print 'distance is ', get_distance((x,y), (x1,y1))
                #print x,y
                x, y = set_xy(pos_list, avatar, config)
    else:
        # check the distance to the avatar if there is no list yet
        if get_distance((x, y), avatar) < dist_avatar:
            x, y = set_xy(pos_list, avatar, config)
    #print 'set_xy, x,y', x, y
    return x, y


def get_circle_point(radius):
    x, y = random.uniform(-radius, radius), random.uniform(-radius, radius)
    if get_distance((x, y), (0, 0)) > radius:
        x, y = get_circle_point(radius)
    return x, y


def create_sub_areas(dimensions):
    # dimensions is a dictionary
    min_x = dimensions['min_x']
    max_x = dimensions['max_x']
    min_y = dimensions['min_y']
    max_y = dimensions['max_y']
    # distances for x and y in new sections
    x_dist = get_distance((min_x, min_y), (max_x, min_y)) / 3
    y_dist = get_distance((min_x, min_y), (min_x, max_y)) / 3
    # 7, 8, 9
    # 4, 5, 6
    # 1, 2, 3
    # returns a dictionary where each number represents a section
    # of the field: (min_x, min_y, max_x, max_y)
    sub_areas = {1: {'min_x': min_x, 'max_x': min_x + x_dist,
                     'min_y': min_y, 'max_y': min_y + y_dist},
                 2: {'min_x': min_x + x_dist, 'max_x': min_x + 2 * x_dist,
                     'min_y': min_y,  'max_y': min_y + y_dist},
                 3: {'min_x': min_x + 2 * x_dist, 'max_x': min_x + 3 * x_dist,
                     'min_y': min_y, 'max_y': min_y + y_dist},
                 4: {'min_x': min_x, 'max_x': min_x + x_dist,
                     'min_y': min_y + y_dist, 'max_y': min_y + 2 * y_dist},
                 5: {'min_x': min_x + x_dist, 'max_x': min_x + 2 * x_dist,
                     'min_y': min_y + y_dist, 'max_y': min_y + 2 * y_dist},
                 6: {'min_x': min_x + 2 * x_dist, 'max_x': min_x + 3 * x_dist,
                     'min_y': min_y + y_dist, 'max_y': min_y + 2 * y_dist},
                 7: {'min_x': min_x, 'max_x': min_x + x_dist,
                     'min_y': min_y + 2 * y_dist, 'max_y': min_y + 3 * y_dist},
                 8: {'min_x': min_x + x_dist, 'max_x': min_x + 2 * x_dist,
                     'min_y': min_y + 2 * y_dist, 'max_y': min_y + 3 * y_dist},
                 9: {'min_x': min_x + 2 * x_dist, 'max_x': min_x + 3 * x_dist,
                     'min_y': min_y + 2 * y_dist, 'max_y': min_y + 3 * y_dist},
                 }
    return sub_areas
