"""
Smart Align
Provides Aligning functionality for various Revit Objects.
TESTED REVIT API: 2015 | 2016

Copyright (c) 2014-2016 Gui Talarico
github.com/gtalarico | @gtalarico

This script is part of PyRevitPlus: Extensions for PyRevit
github.com/gtalarico | @gtalarico

--------------------------------------------------------
PyRevit Notice:
Copyright (c) 2014-2016 Ehsan Iran-Nejad
pyRevit: repository at https://github.com/eirannejad/pyRevit

"""

__author__ = '@gtalarico'
__version = '0.4.0'

import sys
import os
sys.path.append(os.path.dirname(__file__))

from Autodesk.Revit.DB import XYZ
from Autodesk.Revit.DB import Transaction

from core import logger
from core import Align
from core import PointElement, PointCollection, BoundingBoxElement
from core import get_location, get_selected_elements, move_element
from core import TOLERANCE

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

def main(ALIGN):
    """ Main Smart Align Funciton.
    ALIGN argument define align method (min, max, average)
    and axis (X, Y) based on Align class
    """
    align_axis = Align.axis[ALIGN]
    align_method = Align.method[ALIGN]
    logger.debug('ALIGN: {}'.format(ALIGN))
    logger.debug('AXIS: {}'.format(align_axis))

    point_collection = PointCollection()
    elements = get_selected_elements()

    for element in elements:
        point_element = get_location(element, align_method)
        if point_element:
            point_element.element = element
            point_collection.points.append(point_element)

    average_target = getattr(point_collection, align_method)
    logger.debug('Location Target is: {}'.format(average_target))

    t = Transaction(doc, 'Smart Align - Align')
    t.Start()

    for point_element in point_collection:
        delta = getattr(average_target, align_axis) - getattr(point_element, align_axis)

        logger.debug('Delta is: {}'.format(str(delta)))
        if abs(delta) < TOLERANCE:
            logger.info('Translation smaller than tolerance. Skipping...')
            
        else:
            delta_vector = PointElement(0, 0, 0)  # Blank Vector
            setattr(delta_vector, align_axis, delta)    # Replace Axis with Delta
            translation = XYZ(*delta_vector.as_tuple)  # Revit PTvector
            logger.debug('Translation: {}'.format(str(translation)))
            move_element(point_element.element, translation)

    logger.info('Done.')
    t.Commit()
