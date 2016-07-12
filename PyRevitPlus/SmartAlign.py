"""
Copyright (c) 2014-2016 Gui Talarico

Smart Align
Smart Align is part of PyRevit Plus Optional Extensions for PyRevit
github.com/gtalarico | gtalarico@gmail.com

--------------------------------------------------------

Copyright (c) 2014-2016 Ehsan Iran-Nejad
pyRevit: repository at https://github.com/eirannejad/pyRevit

"""

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
        # print('X >', str(x_values))
        # print('Y >', str(y_values))
        # print('Z >', str(z_values))
        # print('FINAL >', str(PointElement(x_avg, y_avg, z_avg)))
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

    #Try Room Method First
    try:
        room_point = element.Location.Point
    except:
        pass
        # print('Is not a room. Trying bbox...')
    else:
        # print('Sweet: Got room center')
        return PointElement(room_point.X, room_point.Y, room_point.Z)

    #Try Then Bounding Box
    try:
        bbox = BoundingBoxElement(element)
    except:
        pass
        # print('Failed. Could not get BBox for:{}'.format(type(element)))
    else:
        # print('Sweet. Got Bounding Box.')
        return getattr(bbox, align_method)

    # print('Failed to Point for: '. type(element))


def main(ALIGN):
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
        delta = getattr(average_target, axis) - getattr(point_element, axis)
        # print('Delta is:', str(delta))
        # if False and abs(delta) < TOLERANCE:
            # pass
            # print('Translation smaller than tolerance')
        if True:
            delta_vector = PointElement(0, 0, 0)
            setattr(delta_vector, axis, delta)
            translation = XYZ(*delta_vector.as_tuple)
            # print('translation:', str(translation))
            try:
                point_element.element.Location.Move(translation)
                # ElementTransformUtils.MoveElement(doc, point_element.element.Id, translation)
            except:
                pass
                # print('Failed Moving Object:', type(point_element.element))
            else:
                pass
                # print('Moved: ' + str(type(point_element.element)))
    # print('Done.')

    t.Commit()

verbose = True
verbose = False
