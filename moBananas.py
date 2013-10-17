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

def setXY(pList, tooClose=[]):
    """
    (list) -> tuple
    Returns a point (x,y) that is more than the minimum distance set by tooClose
    in the config.py file from existing points in pList.
    """
    config = {}
    execfile('config.py', config)
    if not tooClose:
        tooClose = config['tooClose']
    x = random.uniform(config['minDistance'], config['maxDistance'])
    y = random.uniform(config['minFwDistance'], config['maxFwDistance'])

    if pList:
        for x1,y1 in pList:
            if distance((x,y), (x1,y1)) < tooClose:
                #print 'set xy too close'
                #print 'distance is ', distance((x,y), (x1,y1))
                #print x,y
                x, y = setXY(pList)
    return x, y