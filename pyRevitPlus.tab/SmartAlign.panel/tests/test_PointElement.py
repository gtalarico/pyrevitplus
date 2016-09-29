#  python -m unittest discover -s tests -v

import unittest
from smartalign.core import PointElement

class TestPointElement(unittest.TestCase):
    def setUp(self):
        self.pointA = PointElement(2,2,2)
        self.pointB = PointElement(10,6,0)

    def test_attributes(self):
        self.assertEqual(self.pointA.X, 2)
        self.assertEqual(self.pointA.Y, 2)
        self.assertEqual(self.pointA.Z, 2)
        self.assertEqual(self.pointB.X, 10)
        self.assertEqual(self.pointB.Y, 6)
        self.assertEqual(self.pointB.Z, 0)

    def test_eq(self):
        pointA = PointElement(2, 2, 2)
        pointB = PointElement(2, 2, 2)
        pointC = PointElement(0, 0, 0)
        self.assertEqual(pointA, pointB)
        self.assertNotEqual(pointA, pointC)

    def test_tuple(self):
        self.assertEqual(self.pointA.as_tuple, (2,2,2))

    def test_init(self):
        point = PointElement()
        self.assertEqual(point.as_tuple, (0,0,0))

    def test_add(self):
        pointSum = self.pointA + self.pointB
        sum_result = PointElement(12, 8, 2)
        self.assertEqual(pointSum, sum_result)

    def test_sub(self):
        pointSub = self.pointB - self.pointA
        sub_result = PointElement(8, 4, -2)
        self.assertEqual(pointSub, sub_result)
