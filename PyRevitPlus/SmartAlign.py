"""
Copyright (c) 2014-2016 Gui Talarico

Smart Align
is part of PyRevitPlus: Extensions for PyRevit
github.com/gtalarico | gtalarico@gmail.com

--------------------------------------------------------
PyRevit Notice:
Copyright (c) 2014-2016 Ehsan Iran-Nejad
pyRevit: repository at https://github.com/eirannejad/pyRevit

"""

__author__ = 'gtalarico@gmail.com'
__version = '0.0.2'

# TO DO:
# Arrange/Distribute Obects
# 3D (z axis) capability
# Add Compatibility for Window Family (x + y are reversed)

import logging

LOG_LEVEL = logging.ERROR
LOG_LEVEL = logging.DEBUG

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

TOLERANCE = 0.000001


class Justification():
    """ Justification Class.
    This class defines the name, location method, and axis for each
    alignment type

    TO DO:
    + Use class instanciation
    + Refactor Name Just > Alignment
    alignment = Justification('HCENTER')
    alignment.axis    # returns x or y
    alignment.method  # returns min, max, average
    """

    VCENTER = 'Vertical Center'
    VTOP = 'Vertical Top'
    VBOTTOM = 'Vertical Bottom'
    HCENTER = 'Horizontal Center'
    HLEFT = 'Horiztontal Left'
    HRIGHT = 'Horizontal Right'

    method = {VCENTER: 'average', VTOP: 'max', VBOTTOM: 'min',
              HCENTER: 'average', HLEFT: 'min', HRIGHT: 'max'}
    axis = {VCENTER: 'Y', VTOP: 'Y', VBOTTOM: 'Y',
            HCENTER: 'X', HLEFT: 'X', HRIGHT: 'X'}


class PointCollection(object):
    """ Provides methods for getting calculated values from list of Points.
    Usage:
    points = [p1,p2,p3,p4, ...]
    point_collection = PointCollection(*points)
    or
    point_collection = PointCollection(pt1, pt2, pt)
    or
    point_collection = PointCollection() - then
    point_collection.points = [p1, p2, p3]
    Note: Supplied point objects must have attributes .X, .Y, and .Z

    Properties:
    point_collection.average
    point_collection.min
    point_collection.max
    """
    def __init__(self, *points):
        self.points = list(points)

    def __iter__(self):
        for point in self.points:
            yield point

    @property
    def average(self):
        """ Returns PointElement representing average of point collection.
        PointElement objects must support X,Y,Z attributes.
        points = [(0,0,0), (4,4,2)]
        points.average = (2,2,1)
        """
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
        """ Returns PointElement representing MAXIMUM of point collection.
        PointElement objects must support X,Y,Z attributes.
        Example:
        points = [(0,0,5), (2,2,2)]
        points.max = (2,2,5)
        """
        x_values = [point.X for point in self.points]
        y_values = [point.Y for point in self.points]
        z_values = [point.Z for point in self.points]
        x_max = max(x_values)
        y_max = max(y_values)
        z_max = max(z_values)
        return PointElement(x_max, y_max, z_max)

    @property
    def min(self):
        """ Returns PointElement representing MINIMUM of point collection.
        PointElement objects must support X,Y,Z attributes.
        Example:
        points = [(0,0,5), (2,2,2)]
        points.min = (0,0,2)
        """
        x_values = [point.X for point in self.points]
        y_values = [point.Y for point in self.points]
        z_values = [point.Z for point in self.points]
        x_min = min(x_values)
        y_min = min(y_values)
        z_min = min(z_values)
        return PointElement(x_min, y_min, z_min)


class PointElement(object):
    """ Similar to Revit XYZ, but also stores associated element.
    Includes magic methods for addition and subtraciton of points.
    Usage:
    point_element = PointElement(0,0,0)
    point_element.element = revit_element
    or
    point_element = get_location(element, ALIGN)
    if point_element:
        point_element.element = element

    PointElement(2,2,2) + PointElement(2,2,2):
    PointElement(4,4,4)

    Methods:
    point_element.as_tuple: (x, y,z)

    ignore_z: not implemented
    """
    def __init__(self, X, Y, Z, element=None, ignore_z=False):
        self.X = X
        self.Y = Y
        self.Z = Z
        self.element = element
        if ignore_z:
            raise NotImplementedError
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
    """ BoundingBoxElement receives a Revit Object for access to properties.
    Usage:
    bbox = BoundingBoxElement(element)
    bbox.element: element
    Properties:
    bbox.min: min coordinate of bounding box
    bbox.max: min coordinate of bounding box
    bbox.average: min coordinate of bounding box

    """

    def __init__(self, element):
        self.element = element
        self.bbox = element.get_BoundingBox(doc.ActiveView)

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

    try:  # Try .Location Method First - Needed for Rooms
        location_pt = element.Location.Point
    except:
        logger.debug('Could not get .Location. Trying bbox...')
    else:
        location_pt = PointElement(location_pt.X, location_pt.Y, location_pt.Z)
        logger.debug('Got Location from .Location: {}'.format(location_pt))
        return location_pt

    try:  # Not Room: Try Bounding Box Method
        bbox = BoundingBoxElement(element)
    except:
        logger.debug('Could not get BBox for:{}'.format(type(element)))
    else:
        location_pt = getattr(bbox, align_method)  # min, max, or average
        logger.debug('Got Location by Bounding Box: {}'.format(location_pt))
        return location_pt

    # If got to this point, it failed.
    logger.warning('Failed to get_location for: {}'.format(str(type(element))))


def main(ALIGN):
    """ Main Smart Align Funciton.
    ALIGN argument define align method (min, max, average)
    and axis (X, Y) based on Justification class
    """
    axis = Justification.axis[ALIGN]
    logger.debug('ALIGN: {}'.format(ALIGN))
    logger.debug('AXIS: {}'.format(axis))

    point_collection = PointCollection()
    selection = uidoc.Selection
    selection_ids = selection.GetElementIds()
    selection_size = selection_ids.Count
    logger.debug('selection_size: {}'.format(selection_size))
    # selection = uidoc.Selection.Elements  # Revit 2015
    if not selection_ids:
        logger.error('No Elements Selected')
        # return
    # for element in selection:
    for element_id in selection_ids:
        element = doc.GetElement(element_id)
        point_element = get_location(element, ALIGN)
        if point_element:
            point_element.element = element
            point_collection.points.append(point_element)

    average_target = getattr(point_collection, Justification.method[ALIGN])
    logger.debug('Location Target is: {}'.format(average_target))

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
