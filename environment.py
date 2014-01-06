#from direct.directbase.DirectStart import base
from pandaepl import Model, MovingObject


class Environment():
    def __init__(self, config):

        environ = config['environ']

        if environ == 'training':
            self.training()
        elif environ == 'original':
            self.original(config)

    def original(self, config):
        #print config['terrainModel']
        self.terrainModel = Model.Model('terrain', config['terrainModel'], config['terrainCenter'])
        # When hitting an object that is part of the terrain, repel or slide?
        self.terrainModel.setCollisionCallback(MovingObject.MovingObject.handleRepelCollision)

        ## load sky
        self.skyModel = Model.Model("sky", config['skyModel'])
        self.skyModel.setScale(config['skyScale'])

        ## Load palm tree.
        self.treeModel = Model.Model("tree", config['treeModel'], config['treeLoc'])
        self.treeModel.setScale(config['treeScale'])

        ## Load Skyscraper
        self.skyscraperModel = Model.Model("skyscraper", config['skyScraperModel'], config['skyScraperLoc'])
        self.skyscraperModel.setScale(config['skyScraperScale'])

        ## Load Streetlight
        self.streetlightModel = Model.Model("streetlight", config['stLightModel'], config['stLightLoc'])
        self.streetlightModel.setScale(config['stLightScale'])

        ## Load Windmill
        self.windmillModel = Model.Model("windmill", config['windmillModel'], config['windmillLoc'])
        self.windmillModel.setScale(config['windmillScale'])
        self.windmillModel.setH(config['windmillH'])
        #self.windmillModel.showBounds()

    def training(self):
        # no environment when starting training
        base.setBackgroundColor(0, 0, 0)