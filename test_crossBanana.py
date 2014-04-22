import unittest
from crossBanana import CrossBanana


class CrossBananaTests(unittest.TestCase):

    def setUp(self):
        self.cb = CrossBanana()
        self.config = {}
        execfile('config_test.py', self.config)

    def test_move_crosshair(self):
        """
        test that crosshair moves amount we expect
        """
        dist = self.config['xHairDist']
        start = self.config['xStartPos']
        t_dist = start[0] + dist
        self.assertEquals(cb.move_crosshair(), t_dist)

