"""
Make Floors
Create Floors from Selected Rooms
TESTED REVIT API: 2015 | 2016 | 2017

This script is part of PyRevitPlus: Extensions for PyRevit
github.com/gtalarico | @gtalarico

--------------------------------------------------------
PyRevit Notice:
Copyright (c) 2014-2016 Ehsan Iran-Nejad
pyRevit: repository at https://github.com/eirannejad/pyRevit
"""

__doc__ = 'Makes Floor objects from selected rooms.'
__author__ = '@gtalarico'
__title__ = "Make\nFloors"


__window__.Close()

import sys
import os
from collections import namedtuple

from Autodesk.Revit.DB.Architecture import Room

import rpw
from rpw import doc, uidoc, DB, UI

selection = rpw.Selection()

selected_rooms = [e for e in selection.elements if isinstance(e, Room)]
if not selected_rooms:
    UI.TaskDialog.Show('MakeFloors', 'You need to select at lest one Room.')
    sys.exit()

floor_types = rpw.Collector(of_category='OST_Floors', is_type=True).elements
floor_type_options = {DB.Element.Name.GetValue(t): t for t in floor_types}

form = rpw.forms.SelectFromList('Make Floors', floor_type_options.keys(),
                                description='Select Floor Type')
form.show()

if not form.selected:
    __window__.Close()
    sys.exit()

floor_type_id = floor_type_options[form.selected].Id


@rpw.Transaction.ensure('Make Floor')
def make_floor(new_floor):
    floor_curves = DB.CurveArray()
    for boundary_segment in new_floor.boundary:
        try:
            floor_curves.Append(boundary_segment.Curve)       # 2015, dep 2016
        except AttributeError:
            floor_curves.Append(boundary_segment.GetCurve())  # 2017

    floorType = doc.GetElement(new_floor.floor_type_id)
    level = doc.GetElement(new_floor.level_id)
    normal_plane = DB.XYZ.BasisZ
    doc.Create.NewFloor(floor_curves, floorType, level, False, normal_plane)


NewFloor = namedtuple('NewFloor', ['floor_type_id', 'boundary', 'level_id'])
new_floors = []
room_boundary_options = DB.SpatialElementBoundaryOptions()

for room in selected_rooms:
    room_level_id = room.Level.Id
    # List of Boundary Segment comes in an array by itself.
    room_boundary = room.GetBoundarySegments(room_boundary_options)[0]
    new_floor = NewFloor(floor_type_id=floor_type_id, boundary=room_boundary,
                         level_id=room_level_id)
    new_floors.append(new_floor)

for new_floor in new_floors:
    make_floor(new_floor)
