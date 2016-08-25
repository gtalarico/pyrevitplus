"""
Make Plans
Create Plans from Selected Rooms
TESTED REVIT API: 2015

Copyright (c) 2014-2016 Gui Talarico
github.com/gtalarico | gtalarico@gmail.com

This script is part of PyRevitPlus: Extensions for PyRevit
github.com/gtalarico | gtalarico@gmail.com

--------------------------------------------------------
PyRevit Notice:
Copyright (c) 2014-2016 Ehsan Iran-Nejad
pyRevit: repository at https://github.com/eirannejad/pyRevit

"""

__author__ = 'gtalarico@gmail.com'

import sys
import os
import logging
from functools import wraps
from collections import namedtuple

from Autodesk.Revit.UI import TaskDialog
from Autodesk.Revit.DB import XYZ, BoundingBoxXYZ
from Autodesk.Revit.DB import Element, ElementId, BuiltInParameter
from Autodesk.Revit.DB import Transaction, FilteredElementCollector
from Autodesk.Revit.DB import ViewPlanType, ViewFamilyType
from Autodesk.Revit.DB import ViewFamily, ViewPlan
from Autodesk.Revit.DB.Architecture import Room

sys.path.append(os.path.dirname(__file__))
from winforms import SelectViewTypeForm, DialogResult
# from .winforms import SelectViewTypeForm

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

VERBOSE = True  # True to Keep Window Open
VERBOSE = False

LOG_LEVEL = logging.ERROR
LOG_LEVEL = logging.INFO
if VERBOSE:
    LOG_LEVEL = logging.DEBUG
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger('MakePlan')


def get_selected_elements():
    """ Add Doc """
    selection = uidoc.Selection
    selection_ids = selection.GetElementIds()
    selection_size = selection_ids.Count
    logger.debug('selection_size: {}'.format(selection_size))
    # selection = uidoc.Selection.Elements  # Revit 2015
    if not selection_ids:
        TaskDialog.Show('MakePlans', 'No Elements Selected.')
        # logger.error('No Elements Selected')
        __window__.Close()
        sys.exit(0)
    elements = []
    for element_id in selection_ids:
        elements.append(doc.GetElement(element_id))
    return elements


def revit_transaction(transaction_name):
    def wrap(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            try:
                t = Transaction(doc, transaction_name)
                t.Start()
            except InvalidOperationException as errmsg:
                print('Transaciton Error: {}'.format(errmsg))
                return_value = f(*args, **kwargs)
            else:
                return_value = f(*args, **kwargs)
                t.Commit()
            return return_value
        return wrapped_f
    return wrap


def offset_bbox(bbox, offset):
    # From:
    # http://archi-lab.net/create-view-by-room-with-dynamo/
    bboxMinX = bbox.Min.X - offset
    bboxMinY = bbox.Min.Y - offset
    bboxMinZ = bbox.Min.Z - offset
    bboxMaxX = bbox.Max.X + offset
    bboxMaxY = bbox.Max.Y + offset
    bboxMaxZ = bbox.Max.Z + offset
    newBbox = BoundingBoxXYZ()
    newBbox.Min = XYZ(bboxMinX, bboxMinY, bboxMinZ)
    newBbox.Max = XYZ(bboxMaxX, bboxMaxY, bboxMaxZ)
    return newBbox


@revit_transaction('Create View')
def create_plan(name, chosen_view_type_name, level_id, bbox=None):
    """Create a Drafting View"""

    def update_view_crop(view, bbox):
        view.CropBoxActive = True
        # view.CropBoxVisible  = False
        underlay = view.get_Parameter(BuiltInParameter.VIEW_UNDERLAY_ID)
        underlay.Set(ElementId.InvalidElementId)
        view.CropBox = bbox

    floorplan_type_id = get_plan_type_id(chosen_view_type_name)
    floorplan_view = ViewPlan.Create(doc, floorplan_type_id, level_id)
    if bbox:
        update_view_crop(floorplan_view, bbox)
    try:
        floorplan_view.Name = name
    except Exception as errmsg:
        logger.error(errmsg)
        floorplan_view.Name = name + '-Copy2'
    return floorplan_view


def get_plan_types_names():
    type_names = []
    viewfamily_types = FilteredElementCollector(doc).OfClass(
                            ViewFamilyType).WhereElementIsElementType()
    for view_type in viewfamily_types:
        if view_type.ViewFamily == ViewFamily.FloorPlan or view_type.ViewFamily == ViewFamily.CeilingPlan:
            view_type_name = Element.Name.GetValue(view_type)
            type_names.append(view_type_name)
    return type_names


def get_plan_type_id(chosen_view_type_name):
    """Selects First available ViewType that Matches Drafting Type."""
    viewfamily_types = FilteredElementCollector(doc).OfClass(
                            ViewFamilyType).WhereElementIsElementType()
    for view_type in viewfamily_types:
        view_type_name = Element.Name.GetValue(view_type)
        if view_type.ViewFamily == ViewFamily.FloorPlan or view_type.ViewFamily == ViewFamily.CeilingPlan:
            if view_type_name == chosen_view_type_name:
                return view_type.Id
    else:
        logger.info('Did not Match any types')


__window__.Close()

elements = get_selected_elements()


# chosen_view_type_name = 'LFP - KeyPlan - Enlarged'
options = get_plan_types_names()

form = SelectViewTypeForm(options)
form.ShowDialog()
if form.DialogResult == DialogResult.OK:
    chosen_view_type_name = form.selected

NewView = namedtuple('NewView', ['name', 'bbox', 'level_id'])
new_views = []


for element in elements:
    if isinstance(element, Room):
        room = element
        room_level_id = room.Level.Id
        room_name = room.LookupParameter('Name').AsString()
        room_number = room.LookupParameter('Number').AsString()
        new_room_name = '{}-{}'.format(room_name, room_number)

        room_bbox = element.get_BoundingBox(doc.ActiveView)
        new_bbox = offset_bbox(room_bbox, 0.5)  # 6"

        view_name = '{} - {}'.format(room.Level.Name, new_room_name)
        new_view = NewView(name=view_name, bbox=new_bbox,
                           level_id=room_level_id)

        new_views.append(new_view)
        logger.info('New View: ' + new_room_name)


if not new_views:
    TaskDialog.Show('MakePlan', 'No Rooms in Selection')

for new_view in new_views:
    view = create_plan(new_view.name, chosen_view_type_name, new_view.level_id,
                       bbox=new_view.bbox)
