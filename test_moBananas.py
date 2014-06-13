import unittest
import moBananas as mb


class MoBananasTests(unittest.TestCase):

    def test_distance(self):
        """
        Test Distance Formula
        """
        p0 = (8, 4)
        p1 = (9, 5)
        dist = 1.4142135623730951
        self.assertEquals(mb.distance(p0, p1), dist)

    def test_setXY_no_pList(self):
        """
        Test that we are given a point that at least 0.5 distance
        away from points already on the list
        """
        pList = []
        p0 = mb.setXY(pList, tooClose=0.5)
        #print p0
        for p in pList:
            #print p
            dist = mb.distance(p0, p)
            #print dist
            self.assertTrue(dist > 0.5)

    def test_setXY_one_point_in_pList(self):
        """
        Test that we are given a point that at least 0.5 distance
        away from points already on the list
        """
        pList = [(4.3, 5.2)]

        p0 = mb.setXY(pList, tooClose=0.5)
        #print p0
        for p in pList:
            #print p
            dist = mb.distance(p0, p)
            #print dist
            self.assertTrue(dist > 0.5)

    def test_setXY_many_points_pList(self):
        """
        Test that we are given a point that at least 0.5 distance
        away from points already on the list
        """
        pList = []
        for i in range(30):
            (x, y) = mb.setXY(pList, tooClose=0.5)
            #print 'new point', p0
            for p in pList:
                dist = mb.distance((x, y), p)
                self.assertTrue(dist >= 0.5)
            pList += [(x, y)]
            #print pList
            #print len(pList)

    def test_setXY_not_close_to_origin(self):
        """
        Test that each point we are given a point is at least 0.5 distance
        away from the avatar, avatar starts at origin, default
        """
        origin = (0, 0)
        pList = []
        for i in range(50):
            (x, y) = mb.setXY(pList, tooClose=0.5)
            dist = mb.distance((x, y), origin)
            self.assertTrue(dist >= 0.5)
            pList += [(x, y)]
            #print pList
            #print len(pList)

    def test_setXY_not_close_to_origin(self):
        """
        Test that each point we are given a point is at least 0.5 distance
        away from the avatar when not at origin
        """
        avatar = (2, -2)
        pList = []
        for i in range(50):
            (x, y) = mb.setXY(pList, avatar, 0.5)
            dist = mb.distance((x, y), avatar)
            self.assertTrue(dist >= 0.5)
            pList += [(x, y)]
            #print pList
            #print len(pList)

    def test_setXY_from_config_file(self):
        """
        Test that each point we are given a point is at least 0.5 distance
        away from the avatar when not at origin
        """
        config = {}
        execfile('config.py', config)
        avatar = (config['initialPos'][0],config['initialPos'][1])
        #print avatar
        tooClose = config['tooClose']
        pList = []
        numBananas = config['numBananas']
        for i in range(numBananas):
            (x, y) = mb.setXY(pList, avatar, tooClose)
            dist = mb.distance((x, y), avatar)
            self.assertTrue(dist >= tooClose)
            pList += [(x, y)]
            #print pList
            #print len(pList)

if __name__ == "__main__":
    unittest.main()
