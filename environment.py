#from direct.directbase.DirectStart import base
#from pandaepl import Model, MovingObject
from panda3d.core import Point3


class PlaceModels(object):
    _registry = []

    def __init__(self):
        self._registry.append(self)
        # default is original group
        self.group = 'original'
        self.model = 'models/fixtures/streetlight.bam'
        self.location = Point3(-13, 13, 0)
        self.scale = 1
        self.head = 0
        self.callback = None
        self.name = 'streetlight'