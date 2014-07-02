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


def setXY(pList, avatar=(0, 0), tooClose=None,):
    """
    (list) -> tuple
    Returns a point (x,y) that is more than the minimum distance set by tooClose
    in the config.py file from existing points in pList. Also cannot be too 
    close to the avatar, which is at the origin in the beginning.
    """
    config = {}
    execfile('config.py', config)
    if not tooClose:
        #print 'get from config'
        tooClose = config['tooClose']
        dist_avatar = config['avatarRadius']*3
    else:
        dist_avatar = tooClose
    #print 'too close, setXY', tooClose

    x = random.uniform(config['minDistance'], config['maxDistance'])
    y = random.uniform(config['minFwDistance'], config['maxFwDistance'])

    #print 'x', x
    # check the distance to points already on the list and to the avatar
    if pList:
        for x1, y1 in pList:
            # if either too close, get new points.
            if distance((x, y), (x1, y1)) < tooClose or distance((x, y), avatar) < dist_avatar:
                #print 'set xy too close'
                #print 'distance is ', distance((x,y), (x1,y1))
                #print x,y
                x, y = setXY(pList, avatar, tooClose)
    else:
        # check the distance to the avatar if there is no list yet
        if distance((x, y), avatar) < dist_avatar:
            x, y = setXY(pList, avatar, tooClose)
    #print 'setXY, x,y', x, y
    return x, y


def get_reward_level(position):
    pass