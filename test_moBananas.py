import unittest
import moBananas as mb

class initMoBananasTests(unittest.TestCase):

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
        p0 = mb.setXY(pList, 0.5)
        print p0
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
        p0 = mb.setXY(pList, 0.5)
        print p0
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
        pList = [(5, 2), (2, 2), (-5, -5)]
        p0 = mb.setXY(pList, 0.5)
        print p0
        for p in pList:
            #print p
            dist = mb.distance(p0, p)
            #print dist
            self.assertTrue(dist > 0.5)

if __name__ == "__main__":
    unittest.main()
