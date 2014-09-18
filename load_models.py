from panda3d.core import Point3


class PlaceModels(object):
    _registry = []

    def __init__(self):
        self._registry.append(self)
        # default is original group
        # models can be members of more than one group
        # for example self.group = ['original', 'circle']
        self.group = 'original'
        self.model = 'models/fixtures/streetlight.bam'
        self.location = Point3(-13, 13, 0)
        self.scale = 1
        self.head = 0
        self.callback = None
        self.name = 'streetlight'


# Eventually may want to make this a database
def load_models():
    terrain = PlaceModels()
    terrain.group = 'original'
    #terrain.group = 'meh'
    terrain.name = 'terrain'
    terrain.model = 'models/play_space/field.bam'
    terrain.scale = 1
    #terrain.scale = Point3(1.5, 1.5, 1)
    terrain.location = Point3(0, 0, 0)
    terrain.callback = 'MovingObject.handleRepelCollision'

    sky_model = PlaceModels()
    sky_model.name = 'sky'
    sky_model.group = 'original'
    #sky_model.group = 'meh'
    sky_model.model = 'models/sky/sky.bam'
    sky_model.location = Point3(0, 0, 0)
    sky_model.scale = 1.6

    #smiley_model = PlaceModels()
    #smiley_model.name = 'smiley'
    #smiley_model.group = 'original'
    #smiley_model.model = 'smiley'
    #smiley_model.location = Point3(5, 5, 1)
    #smiley_model.scale = 0.1

    palm_tree = PlaceModels()
    palm_tree.group = 'original'
    palm_tree.name = 'palm_tree'
    palm_tree.model = 'models/trees/palmTree.bam'
    palm_tree.location = Point3(13, 13, 0)
    palm_tree.scale = 0.0175

    skyscraper = PlaceModels()
    skyscraper.group = 'original'
    skyscraper.name = 'skyscraper'
    skyscraper.model = 'models/skyscraper/skyscraper.bam'
    skyscraper.location = Point3(-13, -13, 0)
    skyscraper.scale = 0.3

    streetlight = PlaceModels()
    streetlight.group = ['original']
    streetlight.name = 'streetlight'
    streetlight.model = 'models/streetlight/streetlight.bam'
    streetlight.location = Point3(-13, 13, 0)
    streetlight.scale = 0.75

    courtyard = PlaceModels()
    courtyard.group = 'circle'
    #courtyard.group = 'other'
    courtyard.name = 'terrain'
    #courtyard.model = 'models/play_space/courtyard.bam'
    courtyard.model = 'models/play_space/round_courtyard.bam'
    #courtyard.model = '../play_environ/models/courtyard_one.egg'
    courtyard.scale = 1
    #courtyard.scale = Point3(0.5, 0.5, 1)
    courtyard.location = Point3(0, 0, 0)
    courtyard.callback = 'MovingObject.handleRepelCollision'

    horizon = PlaceModels()
    horizon.name = 'horizon'
    horizon.group = 'circle'
    #horizon.scale = Point3(2, 2, 1)
    horizon.scale = Point3(2, 2, 4)
    #horizon.scale = 0.5
    horizon.model = 'models/sky/sky_kahana2.bam'
    #horizon.model = 'models/sky/good_sky_hole.egg'
    #horizon.model = '../play_environ/models/sky_cylinder.egg'
    horizon.location = Point3(0, 0, -0.5)

#load_models()
#for item in PlaceModels._registry:
#    print item.model