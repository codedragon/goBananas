from panda3d.core import Point3
from environment import PlaceModels


# Eventually may want to make this a database
def load_models():
    terrain = PlaceModels()
    terrain.group = 'original'
    terrain.name = 'terrain'
    terrain.model = 'models/play_space/field.bam'
    terrain.scale = 1
    terrain.location = Point3(0, 0, 0)
    terrain.callback = 'MovingObject.handleRepelCollision'

    sky_model = PlaceModels()
    sky_model.name = 'sky'
    sky_model.group = 'original'
    sky_model.model = 'models/sky/sky.bam'
    sky_model.location = Point3(0, 0, 0)
    sky_model.scale = 1.6

    palm_tree = PlaceModels()
    palm_tree.group = ['original', 'better']
    palm_tree.name = 'palm_tree'
    palm_tree.model = 'models/trees/palmTree.bam'
    palm_tree.location = Point3(13, 13, 0)
    palm_tree.scale = 0.0175

    skyscraper = PlaceModels()
    skyscraper.group = ['original', 'better']
    skyscraper.name = 'skyscraper'
    skyscraper.model = 'models/skyscraper/skyscraper.bam'
    skyscraper.location = Point3(-13, -13, 0)
    skyscraper.scale = 0.3

    streetlight = PlaceModels()
    streetlight.group = ['original', 'better']
    streetlight.name = 'streetlight'
    streetlight.model = 'models/streetlight/streetlight.bam'
    streetlight.location = Point3(-13, 13, 0)
    streetlight.scale = 0.75

    windmill = PlaceModels()
    #windmill.group = ['original', 'better']
    windmill.group = ['better']
    windmill.name = 'windmill'
    windmill.model = 'models/windmill/windmill.bam'
    windmill.location = Point3(13, -13, 0)
    windmill.scale = 0.2
    windmill.head = 45

    courtyard = PlaceModels()
    courtyard.group = 'better'
    courtyard.name = 'terrain'
    #courtyard.model = 'models/play_space/courtyard.bam'
    courtyard.model = '../play_environ/models/courtyard_one.egg'
    courtyard.scale = 1
    courtyard.location = Point3(0, 0, 0)
    courtyard.callback = 'MovingObject.handleRepelCollision'

    horizon = PlaceModels()
    horizon.name = 'horizon'
    horizon.group = 'better'
    #horizon.scale = 1.6
    horizon.scale = Point3(1, 1, 1)
    #horizon.model = '../play_environ/models/good_sky_hole.egg'
    horizon.model = '../play_environ/models/sky_cylinder.egg'
    horizon.location = Point3(0, 0, -1)

#load_models()
#for item in PlaceModels._registry:
#    print item.model