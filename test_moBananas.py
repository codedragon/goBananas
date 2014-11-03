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
        self.assertEquals(mb.get_distance(p0, p1), dist)

    def test_distance_with_negative(self):
        """
        Test Distance Formula
        """
        p0 = (-2, -3)
        p1 = (-4, 4)
        dist = 7.28
        #print mb.get_distance(p0, p1)
        self.assertAlmostEqual(mb.get_distance(p0, p1), dist, 2)

    def test_distance_with_both_exact(self):
        """
        Test Distance Formula with a position that includes a negative
        and that should give an exact distance
        """
        p0 = (-10, 10)
        p1 = (-10, -10)
        dist = 20
        #print mb.get_distance(p0, p1)
        self.assertEqual(mb.get_distance(p0, p1), dist)

    def test_set_xy_no_pList(self):
        """
        Test that we are given a point that at least 0.5 distance
        away from points already on the list
        """
        pList = []
        config = {'tooClose': 0.5, 'avatarRadius': 0.2, 'min_x': -10, 'max_x': 10,
                  'min_y': -10, 'max_y': 10, 'environ': 'original'}
        avatar = (0, 0)
        p0 = mb.set_xy(pList, avatar, config)
        #print p0
        for p in pList:
            #print p
            dist = mb.get_distance(p0, p)
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
            dist = mb.get_distance((x, y), (0, 0))
            self.assertTrue(dist < config['radius'])
            pList += [(x, y)]

    def test_set_xy_one_point_in_pList(self):
        """
        Test that we are given a point that at least 0.5 distance
        away from points already on the list
        """
        pList = [(4.3, 5.2)]
        config = {'tooClose': 0.5, 'avatarRadius': 0.2, 'min_x': -10, 'max_x': 10,
                  'min_y': -10, 'max_y': 10, 'environ': 'original'}
        avatar = (0, 0)
        p0 = mb.set_xy(pList, avatar, config)
        #print p0
        for p in pList:
            #print p
            dist = mb.get_distance(p0, p)
            #print dist
            self.assertTrue(dist > 0.5)

    def test_set_xy_many_points_pList(self):
        """
        Test that we are given a point that at least 0.5 distance
        away from points already on the list
        """
        pList = []
        config = {'tooClose': 0.5, 'avatarRadius': 0.2, 'min_x': -10, 'max_x': 10,
                  'min_y': -10, 'max_y': 10, 'environ': 'original'}
        avatar = (0, 0)
        for i in range(30):
            (x, y) = mb.set_xy(pList, avatar, config)
            #print 'new point', p0
            for p in pList:
                dist = mb.get_distance((x, y), p)
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
        config = {'tooClose': 0.5, 'avatarRadius': 0.2, 'min_x': -10, 'max_x': 10,
                  'min_y': -10, 'max_y': 10, 'environ': 'original'}
        avatar = (0, 0)
        avatar_min_dist = config['avatarRadius'] * 2
        for i in range(50):
            (x, y) = mb.set_xy(pList, avatar, config)
            dist = mb.get_distance((x, y), origin)
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
        config = {'tooClose': 0.5, 'avatarRadius': 0.2, 'min_x': -10, 'max_x': 10,
                  'min_y': -10, 'max_y': 10, 'environ': 'original'}
        avatar_min_dist = config['avatarRadius'] * 2
        for i in range(50):
            (x, y) = mb.set_xy(pList, avatar, config)
            dist = mb.get_distance((x, y), avatar)
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
            dist = mb.get_distance((x, y), avatar)
            self.assertTrue(dist >= avatar_min_dist)
            pList += [(x, y)]
            #print pList
            #print len(pList)

    def test_create_sub_areas(self):
        my_dict = {'min_x': 0, 'max_x': 9, 'min_y': 3, 'max_y': 12}
        min_and_max = mb.create_sub_areas(my_dict)
        print min_and_max
        self.assertTrue(min_and_max == {1: {'min_x': 0, 'max_x': 3, 'min_y': 3, 'max_y': 6},
                                        2: {'min_x': 3, 'max_x': 6, 'min_y': 3, 'max_y': 6},
                                        3: {'min_x': 6, 'max_x': 9, 'min_y': 3, 'max_y': 6},
                                        4: {'min_x': 0, 'max_x': 3, 'min_y': 6, 'max_y': 9},
                                        5: {'min_x': 3, 'max_x': 6, 'min_y': 6, 'max_y': 9},
                                        6: {'min_x': 6, 'max_x': 9, 'min_y': 6, 'max_y': 9},
                                        7: {'min_x': 0, 'max_x': 3, 'min_y': 9, 'max_y': 12},
                                        8: {'min_x': 3, 'max_x': 6, 'min_y': 9, 'max_y': 12},
                                        9: {'min_x': 6, 'max_x': 9, 'min_y': 9, 'max_y': 12}})

    def test_create_sub_areas_with_neg(self):
        # try with easy negative numbers
        my_dict = {'min_x': -30, 'max_x': 30, 'min_y': -30, 'max_y': 30}
        min_and_max = mb.create_sub_areas(my_dict)
        #print min_and_max
        self.assertTrue(min_and_max == {1: {'min_x': -30, 'max_x': -10, 'min_y': -30, 'max_y': -10},
                                        2: {'min_x': -10, 'max_x': 10, 'min_y': -30, 'max_y': -10},
                                        3: {'min_x': 10, 'max_x': 30, 'min_y': -30, 'max_y': -10},
                                        4: {'min_x': -30, 'max_x': -10, 'min_y': -10, 'max_y': 10},
                                        5: {'min_x': -10, 'max_x': 10, 'min_y': -10, 'max_y': 10},
                                        6: {'min_x': 10, 'max_x': 30, 'min_y': -10, 'max_y': 10},
                                        7: {'min_x': -30, 'max_x': -10, 'min_y': 10, 'max_y': 30},
                                        8: {'min_x': -10, 'max_x': 10, 'min_y': 10, 'max_y': 30},
                                        9: {'min_x': 10, 'max_x': 30, 'min_y': 10, 'max_y': 30}})

    def test_subareas_line_up_in_courtyard(self):
        # want the number keys to correspond with the way the avatar is facing when the game starts.
        # 7 8 9   -x,y      x,y
        # 4 5 6
        # 1 2 3   -x,-y     x,-y
        #
        # So 7 should give you a negative x, positive y, etc., since mapping to avatar at 5, looking at 8.
        my_dict = {'min_x': -10, 'max_x': 10, 'min_y': -10, 'max_y': 10}
        min_and_max = mb.create_sub_areas(my_dict)
        # 7 x neg, y pos
        self.assertTrue(min_and_max[7]['min_x'] < 0)
        self.assertTrue(min_and_max[7]['min_y'] > 0)
        # 9 both pos
        self.assertTrue(min_and_max[9]['min_x'] > 0)
        self.assertTrue(min_and_max[9]['min_y'] > 0)
        # 1 both neg
        self.assertTrue(min_and_max[1]['min_x'] < 0)
        self.assertTrue(min_and_max[1]['min_y'] < 0)
        # 3 x pos, y neg
        self.assertTrue(min_and_max[3]['min_x'] > 0)
        self.assertTrue(min_and_max[3]['min_y'] < 0)

if __name__ == "__main__":
    unittest.main(verbosity=2)
