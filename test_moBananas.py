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

    def test_distance_with_negative(self):
        """
        Test Distance Formula
        """
        p0 = (-2, -3)
        p1 = (-4, 4)
        dist = 7.28
        #print mb.distance(p0, p1)
        self.assertAlmostEqual(mb.distance(p0, p1), dist, 2)

    def test_setXY_no_pList(self):
        """
        Test that we are given a point that at least 0.5 distance
        away from points already on the list
        """
        pList = []
        config = {'tooClose': 0.5, 'avatarRadius': 0.2, 'minXDistance': -10, 'maxXDistance': 10,
                  'minYDistance': -10, 'maxYDistance': 10, 'environ': 'original'}
        avatar = (0, 0)
        p0 = mb.setXY(pList, avatar, config)
        #print p0
        for p in pList:
            #print p
            dist = mb.distance(p0, p)
            #print dist
            self.assertTrue(dist > 0.5)

    def test_points_in_circle(self):
        config = {'tooClose': 1, 'avatarRadius': 0.2, 'radius': 10, 'environ': 'circle'}
        avatar = (0, 0)
        pList = []
        # test all the points are in a circle less than the radius size
        for i in range(30):
            (x, y) = mb.setXY(pList, avatar, config)
            #print 'new point', p0
            dist = mb.distance((x, y), (0, 0))
            self.assertTrue(dist < config['radius'])
            pList += [(x, y)]

    def test_setXY_one_point_in_pList(self):
        """
        Test that we are given a point that at least 0.5 distance
        away from points already on the list
        """
        pList = [(4.3, 5.2)]
        config = {'tooClose': 0.5, 'avatarRadius': 0.2, 'minXDistance': -10, 'maxXDistance': 10,
                  'minYDistance': -10, 'maxYDistance': 10, 'environ': 'original'}
        avatar = (0, 0)
        p0 = mb.setXY(pList, avatar, config)
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
        config = {'tooClose': 0.5, 'avatarRadius': 0.2, 'minXDistance': -10, 'maxXDistance': 10,
                  'minYDistance': -10, 'maxYDistance': 10, 'environ': 'original'}
        avatar = (0, 0)
        for i in range(30):
            (x, y) = mb.setXY(pList, avatar, config)
            #print 'new point', p0
            for p in pList:
                dist = mb.distance((x, y), p)
                self.assertTrue(dist >= 0.5)
            pList += [(x, y)]
            #print pList
            #print len(pList)

    def test_setXY_not_close_to_origin(self):
        """
        Test that each point we are given a point is at least min distance
        away from the avatar, avatar starts at origin, default
        """
        origin = (0, 0)
        pList = []
        config = {'tooClose': 0.5, 'avatarRadius': 0.2, 'minXDistance': -10, 'maxXDistance': 10,
                  'minYDistance': -10, 'maxYDistance': 10, 'environ': 'original'}
        avatar = (0, 0)
        avatar_min_dist = config['avatarRadius'] * 2
        for i in range(50):
            (x, y) = mb.setXY(pList, avatar, config)
            dist = mb.distance((x, y), origin)
            self.assertTrue(dist >= avatar_min_dist)
            pList += [(x, y)]
            #print pList
            #print len(pList)

    def test_setXY_not_close_to_avatar_away_from_origin(self):
        """
        Test that each point we are given a point is at least 0.5 distance
        away from the avatar when not at origin
        """
        avatar = (2, -2)
        pList = []
        config = {'tooClose': 0.5, 'avatarRadius': 0.2, 'minXDistance': -10, 'maxXDistance': 10,
                  'minYDistance': -10, 'maxYDistance': 10, 'environ': 'original'}
        avatar_min_dist = config['avatarRadius'] * 2
        for i in range(50):
            (x, y) = mb.setXY(pList, avatar, config)
            dist = mb.distance((x, y), avatar)
            self.assertTrue(dist >= avatar_min_dist)
            pList += [(x, y)]
            #print pList
            #print len(pList)

    def test_setXY_from_config_file(self):
        """
        Distance from the avatar is determined by the avatarRadius (want at
        least twice the distance as the avatar away from the avatar).
        Test that each point we are given a point is at least this distance
        away from the avatar when at the starting position of the avatar in
        the current config file

        """
        config = {}
        execfile('config.py', config)
        avatar = (config['initialPos'][0], config['initialPos'][1])
        #print avatar
        avatar_min_dist = config['avatarRadius'] * 2
        pList = []
        # use a small number of bananas, because test can take a while if
        # large number
        numBananas = config['numBananas']
        if numBananas > 20:
            numBananas = 20
        for i in range(numBananas):
            (x, y) = mb.setXY(pList, avatar, config)
            dist = mb.distance((x, y), avatar)
            self.assertTrue(dist >= avatar_min_dist)
            pList += [(x, y)]
            #print pList
            #print len(pList)

if __name__ == "__main__":
    unittest.main(verbosity=2)
