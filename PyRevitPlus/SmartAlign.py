"""
Copyright (c) 2014-2016 Gui Talarico

Smart Align
Smart Align is part of PyRevit Plus Optional Extensions for PyRevit
github.com/gtalarico | gtalarico@gmail.com

--------------------------------------------------------

Copyright (c) 2014-2016 Ehsan Iran-Nejad
pyRevit: repository at https://github.com/eirannejad/pyRevit

"""
# TO DO:
# 2016 Compatibility: Elements.Selection
# http://thebuildingcoder.typepad.com/blog/2015/06/cnc-direct-export-wall-parts-to-dxf-and-sat.html#2015.1

import logging

LOG_LEVEL = logging.ERROR
# LOG_LEVEL = logging.DEBUG

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger('SmarAlign')

# True to Keep Window Open
verbose = True
# verbose = False

from Autodesk.Revit.DB import XYZ
from Autodesk.Revit.DB import Transaction
# from Autodesk.Revit.DB import ElementTransformUtils

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

__doc__ = 'Smart Align'
__author__ = 'gtalarico@gmail.com'
TOLERANCE = 0.000001

class Justification():

    VCENTER = 'Vertical Center'
    VTOP = 'Vertical Top'
    VBOTTOM = 'Vertical Bottom'
    HCENTER = 'Horizontal Center'
    HLEFT = 'Horiztontal Left'
    HRIGHT = 'Horizontal Right'

    method = {
              VCENTER: 'average',
              VTOP: 'max',
              VBOTTOM: 'min',
              HCENTER: 'average',
              HLEFT: 'min',
              HRIGHT: 'max'
              }
    axis = {
              VCENTER: 'Y',
              VTOP: 'Y',
              VBOTTOM: 'Y',
              HCENTER: 'X',
              HLEFT: 'X',
              HRIGHT: 'X'
              }


class PointCollection(object):
    ''' ADD DOC'''
    def __init__(self, *points):
        self.points = list(points)

    def __iter__(self):
        for point in self.points:
            yield point

    @property
    def average(self):
        ''' Returns PointElement Average of list of point objects.
        PointElement objects must support X,Y,Z attributes.
        '''
        x_values = [point.X for point in self.points]
        y_values = [point.Y for point in self.points]
        z_values = [point.Z for point in self.points]
        x_avg = sum(x_values)/len(x_values)
        y_avg = sum(y_values)/len(y_values)
        z_avg = sum(z_values)/len(z_values)
        logger.debug('Average Point Collection:')
        logger.debug('In X > {}'.format(str(x_values)))
        logger.debug('In Y > {}'.format(str(y_values)))
        logger.debug('In Z > {}'.format(str(z_values)))
        logger.debug('Final > {}'.format(PointElement(x_avg, y_avg, z_avg)))

        return PointElement(x_avg, y_avg, z_avg)

    @property
    def max(self):
        ''' Returns PointElement Average of list of point objects.
        PointElement objects must support X,Y,Z attributes.
        '''
        x_values = [point.X for point in self.points]
        y_values = [point.Y for point in self.points]
        z_values = [point.Z for point in self.points]
        x_max = max(x_values)
        y_max = max(y_values)
        z_max = max(z_values)
        return PointElement(x_max, y_max, z_max)

    @property
    def min(self):
        ''' Returns PointElement of lowest point of list of point objects.
        PointElement objects must support X,Y,Z attributes.
        '''
        x_values = [point.X for point in self.points]
        y_values = [point.Y for point in self.points]
        z_values = [point.Z for point in self.points]
        x_min = min(x_values)
        y_min = min(y_values)
        z_min = min(z_values)
        return PointElement(x_min, y_min, z_min)


class PointElement(object):
    ''' ADD DOC '''
    def __init__(self, X, Y, Z, element=None, ignore_z=False):
        self.X = X
        self.Y = Y
        self.Z = Z
        self.element = element
        if ignore_z:
            self.Z = 0

    @property
    def as_tuple(self):
        return (self.X, self.Y, self.Z)

    def __sub__(self, other):
        return PointElement(self.X - other.X, self.Y - other.Y,
                            self.Z - other.Z)

    def __add__(self, other):
        return PointElement(self.X + other.X, self.Y + other.Y,
                            self.Z + other.Z)

    def __repr__(self):
        return '<P:X={x} Y={y} Z={z} |E:{el}>'.format(x=self.X, y=self.Y,
                                                      z=self.Z,
                                                      el=bool(self.element))

    def __str__(self):
        return repr(self)


class BoundingBoxElement(object):

    def __init__(self, element):
        self.element = element
        self.bbox = element.get_BoundingBox(doc.ActiveView)
        # bbox = Revit BoundingBoxElement

    @property
    def min(self):
        x, y, z = self.bbox.Min.X, self.bbox.Min.Y, self.bbox.Min.Z
        return PointElement(x, y, z)

    @property
    def max(self):
        x, y, z = self.bbox.Max.X, self.bbox.Max.Y, self.bbox.Max.Z
        return PointElement(x, y, z)

    @property
    def average(self):
        return PointCollection(self.min, self.max).average

    def __repr__(self):
        return '<BB: MIN{} MAX={} CENTER={}>'.format(self.min, self.max,
                                                     self.center)

    def __str__(self):
        return repr(self)


def get_location(element, align):
    ''' ADD DOC '''
    align_method = Justification.method[align]

    try:  # Try Room Method First
        room_point = element.Location.Point
    except:
        logger.debug('Is not a room. Trying bbox...')
    else:
        logger.debug('Sweet: Got room center')
        return PointElement(room_point.X, room_point.Y, room_point.Z)

    try:  # Not Room: Try Bounding Box Method
        bbox = BoundingBoxElement(element)
    except:
        logger.debug('Could not get BBox for:{}'.format(type(element)))
    else:
        logger.debug('Sweet. Got Bounding Box.')
        return getattr(bbox, align_method)

    # If got to this point, it failed.
    logger.warning('Failed to get location for: {}'.format(str(type(element))))


def main(ALIGN):
    """ Main Smart Align Funciton.
    ALIGN argument define align method (min, max, average)
    and axis (X, Y) based on Justification class
    """
    axis = Justification.axis[ALIGN]

    point_collection = PointCollection()
    selection = uidoc.Selection.Elements

    for element in selection:
        point_element = get_location(element, ALIGN)
        if point_element:
            point_element.element = element
            point_collection.points.append(point_element)

    average_target = getattr(point_collection, Justification.method[ALIGN])

    t = Transaction(doc, 'Smart Align')
    t.Start()

    for point_element in point_collection:

        #  delta is the distance the object needs to travel on selected axis.
        delta = getattr(average_target, axis) - getattr(point_element, axis)

        logger.debug('Delta is: {}'.format(str(delta)))
        if abs(delta) < TOLERANCE:
            logger.info('Translation smaller than tolerance. Skipping...')

        else:
            delta_vector = PointElement(0, 0, 0)  # Blank Vector
            setattr(delta_vector, axis, delta)    # Replace Axis with Delta
            translation_vector = XYZ(*delta_vector.as_tuple)  # Revit PTvector
            logger.debug('Translation: {}'.format(str(translation_vector)))
            try:
                point_element.element.Location.Move(translation_vector)
                # ElementTransformUtils.MoveElement(
                # doc, point_element.element.Id, translation_vector)
            except:
                logger.error('Failed Moving Object: {}'.format(
                             type(point_element.element)))
            else:
                logger.debug('Moved: {}'.format(
                             str(type(point_element.element))))
    logger.info('Done.')

    t.Commit()
