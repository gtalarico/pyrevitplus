#  python -m unittest discover -s tests -v

import unittest
import logging
from copy import deepcopy
from smartalign.core import PointElement, PointCollection


class TestPointElement(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.longMessage = True
        pointA = PointElement(2,2,2)
        pointB = PointElement(6,1,4)
        pointC = PointElement(4,6,3)
        points = [pointA, pointB, pointC]
        self.p_col = PointCollection(*points)

    def test_attributes(self):
        self.assertEqual(self.p_col.points[0], PointElement(2,2,2))

    def test_len(self):
        self.assertEqual(len(self.p_col), 3)

    def test_max(self):
        pointMax = PointElement(6,6,4)
        self.assertEqual(self.p_col.max, pointMax)

    def test_min(self):
        pointMin = PointElement(2,1,2)
        self.assertEqual(self.p_col.min, pointMin)

    def test_avg(self):
        pointAvg = PointElement(4,3,3)
        self.assertEqual(self.p_col.average, pointAvg)

    def test_avg(self):
        pointAvg = PointElement(4,3,3)
        self.assertEqual(self.p_col.average, pointAvg)

    def test_sort_points_x(self):
        points = deepcopy(self.p_col)
        points.sort_points('X')
        x_values = [pt.X for pt in points]
        self.assertEqual(x_values,[2,4,6])

    def test_sort_points_y(self):
        points = deepcopy(self.p_col)
        points.sort_points('Y')
        y_values = [pt.Y for pt in points]
        self.assertEqual(y_values,[1,2,6])
