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


def get_random_xy(config, area=None):
    # area should be list of sections x,y allowed to be in.
    # get a random x and y coordinate.
    # If no area given, assume using entire area
    # circle never involves subareas, so return right away
    if 'circle' in config.get('environ', ''):
        radius = config['radius']
        x, y = get_circle_point(radius)
        return x, y
    if not area or len(area) == 9:
        # print 'user whole area'
        # use entire area
        x = random.uniform(config['min_x'], config['max_x'])
        y = random.uniform(config['min_y'], config['max_y'])
        return x, y
    x_y_limits = []
    total_set = range(1, 10)
    non_area = [num for num in total_set if num not in area]
    # get lists of min, max for x, y.
    # if area is large, we will check if not in sub-area instead
    test_areas = area
    exclude = False
    if len(area) > 4:
        test_areas = non_area
        # print 'non-area', test_areas
        exclude = True

    for sub_area in test_areas:
        x_y_limits.append(get_x_y_sub_area(config, sub_area))

    # if area (not test_area) just one section, return random number from that section
    if len(area) == 1:
        # print 'use one section'
        x = random.uniform(x_y_limits[0][0], x_y_limits[0][1])
        y = random.uniform(x_y_limits[0][2], x_y_limits[0][3])
        return x, y

    # If more than one section, get random number
    # from large area and then check to see if in correct
    # sub_area (or not in non_areas)
    if exclude:
        x, y = get_random_xy_not_subarea(config, x_y_limits, test_areas)
    else:
        x, y = get_random_xy_subarea(config, x_y_limits, test_areas)
    print 'random_xy returning', x, y
    return x, y


def get_random_xy_subarea(config, x_y_limits, area):
    x = random.uniform(config['min_x'], config['max_x'])
    y = random.uniform(config['min_y'], config['max_y'])
    # print x_y_limits
    # make sure in correct sub-area, check smaller
    # checking areas it can be in, so just go
    # until match
    # print x_y_limits
    for x_y in x_y_limits:
        if point_inside_square(x, y, x_y):
            # print 'yup, return'
            # print x, y
            return x, y
    else:
        # print 'try again'
        x, y = get_random_xy_subarea(config, x_y_limits, area)
    return x, y


def get_random_xy_not_subarea(config, x_y_limits, area):
    x = random.uniform(config['min_x'], config['max_x'])
    y = random.uniform(config['min_y'], config['max_y'])
    print x_y_limits
    # make sure in correct sub-area, check smaller
    # if we are checking areas it can be in, just go
    # until match, but if checking non-areas, must
    # test all non-areas,
    for x_y in x_y_limits:
        # using non_areas, so need to go through all subareas,
        # and make sure x, y not in any of them. If inside an
        # area, try again.
        if point_inside_square(x, y, x_y):
            print 'try again'
            x, y = get_random_xy_not_subarea(config, x_y_limits, area)
    print 'returning', x, y
    return x, y


def point_inside_square(x, y, limits):
    """ determine if a point is inside a given square or not
    limits is a tuple, (x_min, x_max, y_min, y_max)"""
    inside_x = False
    inside_y = False
    # print x, y
    # print limits
    if limits[0] < x < limits[1]:
        print 'x in square'
        inside_x = True
    if limits[2] < y < limits[3]:
        print 'y in square'
        inside_y = True
    # print inside_x and inside_y
    return inside_x and inside_y


def set_xy(pos_list, avatar=(0, 0), config = None, area = None):
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
    #print('in set_xy', config)
    too_close = config['tooClose']
    dist_avatar = config['avatarRadius'] + too_close
    x, y = get_random_xy(config, area)
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


def get_x_y_sub_area(config, area_key):
    # get total area
    min_x = config['min_x']
    max_x = config['max_x']
    min_y = config['min_y']
    max_y = config['max_y']
    # distances for x and y in new sections
    x_dist = get_distance((min_x, min_y), (max_x, min_y)) / 3
    y_dist = get_distance((min_x, min_y), (min_x, max_y)) / 3
    if area_key == 1:
        return min_x, min_x + x_dist, min_y, min_y + y_dist
    elif area_key == 2:
        return min_x + x_dist, min_x + 2 * x_dist, min_y, min_y + y_dist
    elif area_key == 3:
        return min_x + 2 * x_dist, min_x + 3 * x_dist, min_y, min_y + y_dist
    elif area_key == 4:
        return min_x, min_x + x_dist, min_y + y_dist, min_y + 2 * y_dist
    elif area_key == 5:
        return min_x + x_dist, min_x + 2 * x_dist, min_y + y_dist, min_y + 2 * y_dist
    elif area_key == 6:
        return min_x + 2 * x_dist, min_x + 3 * x_dist, min_y + y_dist, min_y + 2 * y_dist
    elif area_key == 7:
        return min_x, min_x + x_dist, min_y + 2 * y_dist, min_y + 3 * y_dist
    elif area_key == 8:
        return min_x + x_dist, min_x + 2 * x_dist, min_y + 2 * y_dist, min_y + 3 * y_dist
    elif area_key == 9:
        return min_x + 2 * x_dist, min_x + 3 * x_dist, min_y + 2 * y_dist, min_y + 3 * y_dist
