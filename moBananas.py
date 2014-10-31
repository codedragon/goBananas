from __future__ import division
from math import sqrt
import random
""" Functions for bananas that don't need PandaEPL, so can actually be tested reasonably!
Includes functions for testing distance, figuring out banana placement, and determining
reward level dependent on banana positions
"""


def distance(p0, p1):
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
        x = random.uniform(config['minXDistance'], config['maxXDistance'])
        y = random.uniform(config['minYDistance'], config['maxYDistance'])
    return x, y


def set_xy(pList, avatar=(0, 0), config = None):
    """
    (list) -> tuple
    Returns a point (x,y) that is more than the minimum distance set by tooClose
    in the config.py file from existing points in pList. Also cannot be too 
    close to the avatar, which is at the origin in the beginning.
    This algorithm is pretty inefficient for large numbers of fruit, and should
    eventually be optimized.
    """
    if config is None:
        config = {}
        execfile('config.py', config)

    too_close = config['tooClose']
    dist_avatar = config['avatarRadius'] + too_close

    x, y = get_random_xy(config)
    #print('x, y', x, y)
    # check the distance to points already on the list and to the avatar
    if pList:
        for x1, y1 in pList:
            # if either too close to other bananas or avatar, get new points.
            if distance((x, y), (x1, y1)) < too_close or distance((x, y), avatar) < dist_avatar:
                #print 'set xy too close'
                #print 'distance is ', distance((x,y), (x1,y1))
                #print x,y
                x, y = set_xy(pList, avatar, config)
    else:
        # check the distance to the avatar if there is no list yet
        if distance((x, y), avatar) < dist_avatar:
            x, y = set_xy(pList, avatar, config)
    #print 'set_xy, x,y', x, y
    return x, y


def get_circle_point(radius):
    x, y = random.uniform(-radius, radius), random.uniform(-radius, radius)
    if distance((x, y), (0, 0)) > radius:
        x, y = get_circle_point(radius)
    return x, y


def create_sub_areas(dimensions):
    # dimensions is a tuple (min_x, max_x, min_y, max_y)
    min_x, max_x, min_y, max_y = [float(x) for x in dimensions]
    # distances for x and y in new sections
    x_distance = distance((min_x, min_y), (max_x, min_y)) / 3
    print x_distance
    y_distance = distance((min_x, min_y), (min_x, max_y)) / 3
    print y_distance
    # 7, 8, 9
    # 4, 5, 6
    # 1, 2, 3
    # returns a dictionary where each number represents a section
    # of the field: (min_x, min_y, max_x, max_y)
    sub_areas = {1: (min_x, min_x + x_distance, min_y, min_y + y_distance),
                 2: (min_x + x_distance, min_x + 2 * x_distance, min_y, min_y + y_distance),
                 3: (min_x + 2 * x_distance, min_x + 3 * x_distance, min_y, min_y + y_distance),
                 4: (min_x, min_x + x_distance, min_y + y_distance, min_y + 2 * y_distance),
                 5: (min_x + x_distance, min_x + 2 * x_distance, min_y + y_distance, min_y + 2 * y_distance),
                 6: (min_x + 2 * x_distance, min_x + 3 * x_distance, min_y + y_distance, min_y + 2 * y_distance),
                 7: (min_x, min_x + x_distance, min_y + 2 * y_distance, min_y + 3 * y_distance),
                 8: (min_x + x_distance, min_x + 2 * x_distance, min_y + 2 * y_distance, min_y + 3 * y_distance),
                 9: (min_x + 2 * x_distance, min_x + 3 * x_distance, min_y + 2 * y_distance, min_y + 3 * y_distance),
                 }
    return sub_areas


def get_subset_area(subset, sub_areas):
    # need to create a dictionary
    # sub_areas dictionary has values (min_x, max_x, min_y, max_y
    subset = {'minXDistance': sub_areas[subset][0],
              'maxXDistance': sub_areas[subset][1],
              'minYDistance': sub_areas[subset][2],
              'maxYDistance': sub_areas[subset][3],
              }