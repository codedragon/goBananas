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
        self.head = 0
        self.scale = 1
        self.callback = None
        self.name = 'streetlight'
        self.coll_scale = 1


# Eventually may want to make this a database
def load_models():
    terrain = PlaceModels()
    terrain.group = 'original'
    # terrain.group = 'meh'
    terrain.name = 'terrain'
    terrain.model = 'models/play_space/field.bam'
    terrain.scale = 1
    # terrain.scale = Point3(1.5, 1.5, 1)
    terrain.location = Point3(0, 0, 0)
    terrain.callback = 'MovingObject.handleRepelCollision'

    sky_model = PlaceModels()
    sky_model.name = 'sky'
    sky_model.group = ['original', 'stone', 'narrow']
    sky_model.model = 'models/sky/sky.bam'
    sky_model.location = Point3(0, 0, -0.5)
    sky_model.scale = 1.6

    # smiley_model = PlaceModels()
    # smiley_model.name = 'smiley'
    # smiley_model.group = 'original'
    # smiley_model.model = 'smiley'
    # smiley_model.location = Point3(5, 5, 1)
    # smiley_model.scale = 0.1

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
    # courtyard.group = 'other'
    courtyard.name = 'terrain'
    courtyard.model = 'models/play_space/round_courtyard.bam'
    courtyard.scale = 1
    # courtyard.scale = Point3(0.5, 0.5, 1)
    courtyard.location = Point3(0, 0, 0)
    courtyard.callback = 'MovingObject.handleRepelCollision'

    ground = PlaceModels()
    ground.group = 'stone'
    ground.name = 'ground'
    ground.model = 'models/play_space/ground.bam'
    ground.scale = 1.5
    # ground.scale = Point3(0.5, 0.5, 1)
    ground.location = Point3(0, 0, 0)

    sq_courtyard = PlaceModels()
    sq_courtyard.group = 'stone'
    sq_courtyard.name = 'terrain'
    sq_courtyard.model = 'models/play_space/walls.bam'
    sq_courtyard.scale = 1
    sq_courtyard.location = Point3(0, 0, 0)
    sq_courtyard.callback = 'MovingObject.handleRepelCollision'

    # mountains y is distance from wall,
    mountain = PlaceModels()
    mountain.group = 'stone'
    mountain.name = 'mountain'
    mountain.model = 'models/mountain/mountain.bam'
    mountain.scale = 0.0005
    mountain.location = Point3(0, -30, -0.5)

    mountain2 = PlaceModels()
    mountain2.group = 'stone'
    mountain2.name = 'mountain2'
    mountain2.model = 'models/mountain/mountain.bam'
    mountain2.scale = 0.0004
    mountain2.head = 180
    mountain2.location = Point3(30, -45, -0.5)

    mountain3 = PlaceModels()
    mountain3.group = 'stone'
    mountain3.name = 'mountain3'
    mountain3.model = 'models/mountain/mountain.bam'
    mountain3.scale = 0.0003
    mountain3.head = 270
    mountain3.location = Point3(11, -40, -0.5)

    windmill = PlaceModels()
    windmill.group = 'stone'
    windmill.name = 'windmill'
    windmill.model = 'models/windmill/windmill.bam'
    windmill.scale = 0.03
    windmill.head = 15
    windmill.location = Point3(-10, 30, -1)

    tree = PlaceModels()
    tree.group = 'stone'
    tree.name = 'tree'
    tree.model = 'models/trees/tree.bam'
    tree.scale = 0.5
    # tree.head = 15
    tree.location = Point3(40, 20, 0)

    tree2 = PlaceModels()
    tree2.group = 'stone'
    tree2.name = 'tree2'
    tree2.model = 'models/trees/tree.bam'
    tree2.scale = 0.3
    tree2.head = 120
    tree2.location = Point3(30, 12, 0)

    tree_n = PlaceModels()
    tree_n.group = ['narrow']
    tree_n.name = 'tree'
    tree_n.model = 'models/trees/tree.bam'
    tree_n.scale = 0.5
    # tree_n.head = 15
    tree_n.location = Point3(-3, 13, 0)

    fir_tree = PlaceModels()
    fir_tree.group = 'stone'
    fir_tree.name = 'fir_tree'
    fir_tree.model = 'models/trees/fir_tree.bam'
    fir_tree.scale = 2
    # fir_tree.head = 15
    fir_tree.location = Point3(40, 0, -2)

    fir_tree2 = PlaceModels()
    fir_tree2.group = 'stone'
    fir_tree2.name = 'fir_tree2'
    fir_tree2.model = 'models/trees/fir_tree.bam'
    fir_tree2.scale = 5
    fir_tree2.head = 90
    fir_tree2.location = Point3(40, 10, 0)

    fir_tree3 = PlaceModels()
    fir_tree3.group = 'stone'
    fir_tree3.name = 'fir_tree3'
    fir_tree3.model = 'models/trees/fir_tree.bam'
    fir_tree3.scale = 2.5
    fir_tree3.head = 180
    fir_tree3.location = Point3(30, 20, -1)

    fir_tree4 = PlaceModels()
    fir_tree4.group = 'stone'
    fir_tree4.name = 'fir_tree4'
    fir_tree4.model = 'models/trees/fir_tree.bam'
    fir_tree4.scale = 3.5
    fir_tree4.head = 120
    fir_tree4.location = Point3(30, 37, -1)

    fir_tree_n = PlaceModels()
    fir_tree_n.group = ['narrow']
    fir_tree_n.name = 'fir_tree'
    fir_tree_n.model = 'models/trees/fir_tree.bam'
    fir_tree_n.scale = 1.5
    #fir_tree.head = 15
    fir_tree_n.location = Point3(-2, -13, -2)

    fir_tree_n2 = PlaceModels()
    fir_tree_n2.group = ['narrow']
    fir_tree_n2.name = 'fir_tree2'
    fir_tree_n2.model = 'models/trees/fir_tree.bam'
    fir_tree_n2.scale = 1
    fir_tree_n2.head = 90
    fir_tree_n2.location = Point3(2.1, 0, 0)

    ranch_house = PlaceModels()
    ranch_house.group = 'stone'
    ranch_house.name = 'ranch_house'
    ranch_house.model = 'models/buildings/house.egg'
    ranch_house.scale = 3.5
    ranch_house.head = 15
    ranch_house.location = Point3(-50, 3, 3.3)

    horizon = PlaceModels()
    horizon.name = 'horizon'
    horizon.group = ['circle']
    horizon.scale = Point3(2, 2, 4)
    # horizon.scale = 0.5
    horizon.model = 'models/sky/sky_kahana2.bam'
    # horizon.model = 'models/sky/good_sky_hole.egg'
    # horizon.model = '../play_environ/models/sky_cylinder.egg'
    horizon.location = Point3(0, 0, -0.5)

    narrow_court = PlaceModels()
    narrow_court.group = 'narrow'
    narrow_court.name = 'terrain'
    narrow_court.model = 'models/play_space/narrow_court.egg'
    narrow_court.scale = 1
    narrow_court.head = 90
    narrow_court.location = Point3(0, 0, 0.8)
    narrow_court.callback = 'MovingObject.handleRepelCollision'

    banana = PlaceModels()
    banana.name = 'old_banana'
    banana.group = 'fruit'
    banana.scale = 0.5
    banana.model = 'models/bananas/banana.bam'
    banana.coll_scale = 1

    banana = PlaceModels()
    banana.name = 'banana'
    banana.group = 'fruit'
    banana.scale = 0.015
    banana.model = 'models/fruit/banana.bam'
    banana.roll = 75
    banana.coll_scale = 1

    plum = PlaceModels()
    plum.name = 'plum'
    plum.group = 'fruit'
    # plum.scale = 0.004
    # plum.scale = 0.2
    plum.scale = 0.08
    plum.model = 'models/fruit/plum.bam'
    plum.roll = 75
    # scale is redundant if we are setting the pos (last number is scale)
    plum.coll_scale = 1
    # plum.coll_pos = (-5, 5, 110, 200)
    # plum.coll_pos = (0, 0, 1, 4)

    cherry = PlaceModels()
    cherry.name = 'cherry'
    cherry.group = 'fruit'
    cherry.scale = 0.08
    cherry.model = 'models/fruit/cherries.egg'
    cherry.coll_scale = 2
    

def get_model(model_type, model_value):
    load_models()
    for item in PlaceModels()._registry:
        data = getattr(item, model_type)
        if data == model_value:
            return item
    else:
        print(model_value, "not found")

# load_models()
# for item in PlaceModels._registry:
#     print item.model
