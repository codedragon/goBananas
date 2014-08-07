from math import sqrt
import random


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
    try:
        execfile('config.py', config)
    except IOError:
        config = {'tooClose': 1, 'avatarRadius': 0.2, 'minXDistance': -10, 'maxXDistance': 10,
                  'minYDistance': -10, 'maxYDistance': 10}
    if not tooClose:
        #print 'get from config'
        tooClose = config['tooClose']
        dist_avatar = config['avatarRadius']*2
    else:
        dist_avatar = tooClose
    #print 'too close, setXY', tooClose

    x = random.uniform(config['minXDistance'], config['maxXDistance'])
    y = random.uniform(config['minYDistance'], config['maxYDistance'])

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
