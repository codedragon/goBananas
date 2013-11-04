from math import sqrt
import random

def distance(p0, p1):
    """
    (tuple, tuple) -> float
    Returns the distance between 2 points. p0 is a tuple with (x, y)
    and p1 is a tuple with (x1, y1)
    """
    dist = sqrt((float(p0[0]) - float(p1[0])) ** 2 + (float(p0[1]) - float(p1[1])) ** 2)
    return dist

def setXY(pList, avatar=(0, 0), tooClose=[],):
    """
    (list) -> tuple
    Returns a point (x,y) that is more than the minimum distance set by tooClose
    in the config.py file from existing points in pList. Also cannot be too close
    to the avatar, which is at the origin in the beginning.
    """
    config = {}
    execfile('config.py', config)
    if not tooClose:
        tooClose = config['tooClose']
        dist_avatar = config['avatarRadius']*2
    else:
        dist_avatar = tooClose
    x = random.uniform(config['minDistance'], config['maxDistance'])
    y = random.uniform(config['minFwDistance'], config['maxFwDistance'])

    # check the distance to the avatar
    if distance((x, y), avatar) < dist_avatar:
        x, y = setXY(pList)

    # check the distance to points already on the list
    if pList:
        for x1,y1 in pList:
            if distance((x,y), (x1,y1)) < tooClose:
                #print 'set xy too close'
                #print 'distance is ', distance((x,y), (x1,y1))
                #print x,y
                x, y = setXY(pList)
    return x, y