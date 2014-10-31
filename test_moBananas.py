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
        self.assertEqual(mb.distance(p0, p1), dist)

    def test_distance_with_negative(self):
        """
        Test Distance Formula
        """
        p0 = (-2, -3)
        p1 = (-4, 4)
        dist = 7.28
        #print mb.distance(p0, p1)
        self.assertAlmostEqual(mb.distance(p0, p1), dist, 2)

    def test_distance_with_both_exact(self):
        """
        Test Distance Formula with a position that includes a negative
        and that should give an exact distance
        """
        p0 = (-10, 10)
        p1 = (-10, -10)
        dist = 20
        #print mb.distance(p0, p1)
        self.assertEqual(mb.distance(p0, p1), dist)

    def test_set_xy_no_pList(self):
        """
        Test that we are given a point that at least 0.5 distance
        away from points already on the list
        """
        pList = []
        config = {'tooClose': 0.5, 'avatarRadius': 0.2, 'minXDistance': -10, 'maxXDistance': 10,
                  'minYDistance': -10, 'maxYDistance': 10, 'environ': 'original'}
        avatar = (0, 0)
        p0 = mb.set_xy(pList, avatar, config)
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
            (x, y) = mb.set_xy(pList, avatar, config)
            #print 'new point', p0
            dist = mb.distance((x, y), (0, 0))
            self.assertTrue(dist < config['radius'])
            pList += [(x, y)]

    def test_set_xy_one_point_in_pList(self):
        """
        Test that we are given a point that at least 0.5 distance
        away from points already on the list
        """
        pList = [(4.3, 5.2)]
        config = {'tooClose': 0.5, 'avatarRadius': 0.2, 'minXDistance': -10, 'maxXDistance': 10,
                  'minYDistance': -10, 'maxYDistance': 10, 'environ': 'original'}
        avatar = (0, 0)
        p0 = mb.set_xy(pList, avatar, config)
        #print p0
        for p in pList:
            #print p
            dist = mb.distance(p0, p)
            #print dist
            self.assertTrue(dist > 0.5)

    def test_set_xy_many_points_pList(self):
        """
        Test that we are given a point that at least 0.5 distance
        away from points already on the list
        """
        pList = []
        config = {'tooClose': 0.5, 'avatarRadius': 0.2, 'minXDistance': -10, 'maxXDistance': 10,
                  'minYDistance': -10, 'maxYDistance': 10, 'environ': 'original'}
        avatar = (0, 0)
        for i in range(30):
            (x, y) = mb.set_xy(pList, avatar, config)
            #print 'new point', p0
            for p in pList:
                dist = mb.distance((x, y), p)
                self.assertTrue(dist >= 0.5)
            pList += [(x, y)]
            #print pList
            #print len(pList)

    def test_set_xy_not_close_to_origin(self):
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
            (x, y) = mb.set_xy(pList, avatar, config)
            dist = mb.distance((x, y), origin)
            self.assertTrue(dist >= avatar_min_dist)
            pList += [(x, y)]
            #print pList
            #print len(pList)

    def test_set_xy_not_close_to_avatar_away_from_origin(self):
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
            (x, y) = mb.set_xy(pList, avatar, config)
            dist = mb.distance((x, y), avatar)
            self.assertTrue(dist >= avatar_min_dist)
            pList += [(x, y)]
            #print pList
            #print len(pList)

    def test_set_xy_from_config_file(self):
        """
        Distance from the avatar is determined by the avatarRadius (want at
        least twice the distance as the avatar away from the avatar).
        Test that each point we are given a point is at least this distance
        away from the avatar when at the starting position of the avatar in
        the current config file

        """
        config = {}
        execfile('testing_config.py', config)
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
            (x, y) = mb.set_xy(pList, avatar, config)
            dist = mb.distance((x, y), avatar)
            self.assertTrue(dist >= avatar_min_dist)
            pList += [(x, y)]
            #print pList
            #print len(pList)

    def test_create_sub_areas(self):
        min_and_max = mb.create_sub_areas((0, 9, 3, 12))
        print min_and_max
        self.assertDictEqual(min_and_max, {1: (0.0, 3.0, 3.0, 6.0),
                                           2: (3.0, 6.0, 3.0, 6.0),
                                           3: (6.0, 9.0, 3.0, 6.0),
                                           4: (0.0, 3.0, 6.0, 9.0),
                                           5: (3.0, 6.0, 6.0, 9.0),
                                           6: (6.0, 9.0, 6.0, 9.0),
                                           7: (0.0, 3.0, 9.0, 12.0),
                                           8: (3.0, 6.0, 9.0, 12.0),
                                           9: (6.0, 9.0, 9.0, 12.0)})

    def test_create_sub_areas_with_neg(self):
        # try with easy negative numbers
        min_and_max = mb.create_sub_areas((-30, 30, -30, 30))
        #print min_and_max
        self.assertDictEqual(min_and_max, {1: (-30.0, -10.0, -30.0, -10.0),
                                           2: (-10.0, 10.0, -30.0, -10.0),
                                           3: (10.0, 30.0, -30.0, -10.0),
                                           4: (-30.0, -10.0, -10.0, 10.0),
                                           5: (-10.0, 10.0, -10.0, 10.0),
                                           6: (10.0, 30.0, -10.0, 10.0),
                                           7: (-30.0, -10.0, 10.0, 30.0),
                                           8: (-10.0, 10.0, 10.0, 30.0),
                                           9: (10.0, 30.0, 10.0, 30.0)})
if __name__ == "__main__":
    unittest.main(verbosity=2)
