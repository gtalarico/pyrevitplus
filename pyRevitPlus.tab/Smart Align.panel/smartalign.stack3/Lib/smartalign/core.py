"""
Smart Align
Provides Aligning functionality for various Revit Objects.

TESTED REVIT API: 2015 | 2016 | 2017

@gtalarico
This script is part of PyRevitPlus: Extensions for PyRevit
github.com/gtalarico | @gtalarico

--------------------------------------------------------
RevitPythonWrapper: revitpythonwrapper.readthedocs.io
pyRevit: github.com/eirannejad/pyRevit

"""

__author__ = '@gtalarico'
__version = '0.4.0'

import sys
import logging

from Autodesk.Revit.DB import XYZ
from Autodesk.Revit.DB import Transaction

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

VERBOSE = True  # True to Keep Window Open
VERBOSE = False

LOG_LEVEL = logging.ERROR
LOG_LEVEL = logging.INFO
if VERBOSE:
    LOG_LEVEL = logging.DEBUG
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger('SmarAlign')

TOLERANCE = 0.000001

class Align(object):
    """ Align Class.
    This class defines the name, location method, and axis for each
    alignment type

    TO DO:
    + Use class instanciation
    + Refactor Name Just > Alignment
    alignment = Align('HCENTER')
    alignment.axis    # returns x or y
    alignment.method  # returns min, max, average
    """

    VCENTER = 'Vertical Center'
    VTOP = 'Vertical Top'
    VBOTTOM = 'Vertical Bottom'
    HCENTER = 'Horizontal Center'
    HLEFT = 'Horizontal Left'
    HRIGHT = 'Horizontal Right'
    VDIST = 'Vertical Distribution'
    HDIST = 'Horizontal Distrution'

    method = {VCENTER: 'average', VTOP: 'max', VBOTTOM: 'min',
              HCENTER: 'average', HLEFT: 'min', HRIGHT: 'max',
              VDIST: 'average', HDIST:'average'}

    axis = {VCENTER: 'Y', VTOP: 'Y', VBOTTOM: 'Y',
            HCENTER: 'X', HLEFT: 'X', HRIGHT: 'X',
            VDIST: 'Y', HDIST:'X'}


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

    def sort_points(self, align_axis):
        sorted_points = self.points
        sorted_points.sort(key=lambda p: getattr(p, align_axis))
        self.points = sorted_points

    def __len__(self):
        return len(self.points)

    def __repr__(self):
        return '<PC: {points} points | Max={max} Min={min} |Avg:{avg}>'.format(
                                                              points=len(self),
                                                              max=self.max,
                                                              min=self.min,
                                                              avg=self.average
                                                              )

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
    def __init__(self, X=0, Y=0, Z=0, element=None, ignore_z=False):
        self.X = X
        self.Y = Y
        self.Z = Z
        self.element = element
        # if ignore_z:
        #     raise NotImplementedError
        #     self.Z = 0

    @property
    def as_tuple(self):
        return (self.X, self.Y, self.Z)

    def __sub__(self, other):
        return PointElement(self.X - other.X, self.Y - other.Y,
                            self.Z - other.Z)

    def __add__(self, other):
        return PointElement(self.X + other.X, self.Y + other.Y,
                            self.Z + other.Z)

    def __eq__(self, other):
        results = [self.X == other.X,
                   self.Y == other.Y,
                   self.Z == other.Z]
        return all(results)

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

def get_location(element, align_method):
    """ Add Doc """

    try:  # Try .Location Method First - Needed for Rooms
        location_pt = element.Location.Point
    except Exception as errmsg:
        logger.debug('Could not get .Location. Trying bbox...')
        logger.debug('Error: {}'.format(errmsg))
    else:
        location_pt = PointElement(location_pt.X, location_pt.Y, location_pt.Z)
        logger.debug('Got Location from .Location: {}'.format(location_pt))
        return location_pt

    try:  # Try Coord - For Text Elements
        location_pt = element.Coord
    except Exception as errmsg:
        logger.debug('Could not get .Coord.')
        logger.debug('Error: {}'.format(errmsg))
    else:
        location_pt = PointElement(location_pt.X, location_pt.Y, location_pt.Z)
        logger.debug('Got Location from .Location: {}'.format(location_pt))
        return location_pt

    try:  # Not Room: Try Bounding Box Method
        bbox = BoundingBoxElement(element)
    except Exception as errmsg:
        logger.debug('Could not get BBox for:{}'.format(type(element)))
        logger.debug('Error: {}'.format(errmsg))
    else:
        location_pt = getattr(bbox, align_method)  # min, max, or average
        logger.debug('Got Location by Bounding Box: {}'.format(location_pt))
        return location_pt



    # If got to this point, it failed.
    logger.warning('Failed to get_location for: {}'.format(str(type(element))))

def get_selected_elements():
    """ Add Doc """
    selection = uidoc.Selection
    selection_ids = selection.GetElementIds()
    selection_size = selection_ids.Count
    logger.debug('selection_size: {}'.format(selection_size))
    # selection = uidoc.Selection.Elements  # Revit 2015
    if not selection_ids:
        logger.error('No Elements Selected')
        sys.exit(0)
    elements = []
    for element_id in selection_ids:
        elements.append(doc.GetElement(element_id))
    return elements

def move_element(element, translation):
    try:
        element.Location.Move(translation)
    except Exception as errmsg:
        logger.error('Failed Moving Object: {}'.format(type(element)))
        logger.error('Error: {}'.format(errmsg))
    else:
        logger.info('Moved: {}'.format(str(type(element))))

if __name__ == '__main__':
    pass
