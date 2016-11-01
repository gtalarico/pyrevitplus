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

def get_division_steps(delta, qty_items):
    """ADD DOC: Move to Point Collection"""
    step = abs(delta/(qty_items-1))
    steps = []
    for i in range(0, qty_items):
        steps.append(i*step)
    logger.debug('Step is: {}'.format(step))
    return steps

def main(ALIGN):
    """ ADD DOCS
    """
    align_axis = Align.axis[ALIGN]
    align_method = Align.method[ALIGN]

    logger.info('Align Class: {}'.format(ALIGN))
    logger.debug('Align Axis: {}'.format(align_axis))
    logger.debug('Align Methid: {}'.format(align_method))

    elements = get_selected_elements()
    point_collection = PointCollection()

    for element in elements:
        point_element = get_location(element, align_method)
        if point_element:
            point_element.element = element
            point_collection.points.append(point_element)

    point_collection.sort_points(align_axis)
    qty_items = len(point_collection)

    min_target = getattr(point_collection, 'min')
    max_target = getattr(point_collection, 'max')
    delta = getattr(max_target, align_axis) - getattr(min_target, align_axis)

    steps = get_division_steps(delta, qty_items)
    target_locations = [ getattr(min_target, align_axis) + step for step in steps]

    logger.debug('Min Location Target is: {}'.format(min_target))
    logger.debug('Max Location Target is: {}'.format(max_target))
    logger.debug('delta is: {}'.format(str(delta)))
    logger.debug('steps: {}'.format(steps))
    logger.debug('targer_locations: {}'.format(target_locations))

    t = Transaction(doc, 'Smart Align - Distribute')
    t.Start()

    for point_element, target_location in zip(point_collection, target_locations):
        current_location = getattr(point_element, align_axis)
        delta = current_location - target_location
        delta_vector = PointElement(0, 0, 0)
        setattr(delta_vector, align_axis,-delta)
        translation = XYZ(*delta_vector.as_tuple)

        move_element(point_element.element, translation)

        logger.debug('current: {}'.format(current_location))
        logger.debug('target: {}'.format(target_location))
        logger.debug('delta: {}'.format(delta))
        logger.debug('delta_vector: {}'.format(delta_vector))
        logger.debug('Translation: {}'.format(str(translation)))

    logger.info('Done.')
    t.Commit()
