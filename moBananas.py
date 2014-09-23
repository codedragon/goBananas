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
    and p1 is a tuple with (x1, y1)
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