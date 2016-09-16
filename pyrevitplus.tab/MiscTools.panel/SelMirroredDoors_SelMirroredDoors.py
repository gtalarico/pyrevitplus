"""
SelectMirroredDoors
Selects All Door Instances that have been Mirrored.
TESTED REVIT API: 2015 | 2016

Copyright (c) 2014-2016 Gui Talarico
github.com/gtalarico

This script is part of PyRevitPlus: Extensions for PyRevit
github.com/gtalarico

--------------------------------------------------------
PyRevit Notice:
Copyright (c) 2014-2016 Ehsan Iran-Nejad
pyRevit: repository at https://github.com/eirannejad/pyRevit

"""

__doc__ = "Selects All Door Instances that have been Mirrored."
__author__ = '@gtalarico'
__version__ = '0.3.0'

import clr

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference("System")

from Autodesk.Revit.UI import TaskDialog
from Autodesk.Revit.DB import FilteredElementCollector
from Autodesk.Revit.DB import BuiltInCategory, ElementId
from System.Collections.Generic import List
# Required for collection

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document

try:
    # Try to close PyRevit window
    __window__.Close()
except:
    pass

collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors)
doors = collector.ToElements()

mir_doors = []

for door in doors:
    try:
        if door.Mirrored:
            mir_doors.append(door)
    except AttributeError:
        pass  # foor Symbols that don't have Mirrored attribute.

TaskDialog.Show("Mirrored Doors", "Mirrored: {} of {} Doors".format(
                len(mir_doors), len(doors)))

# SELECT MIRRORED DOORS                 | 2015 + 2016 API
selection = uidoc.Selection
collection = List[ElementId]([door.Id for door in mir_doors])
selection.SetElementIds(collection)

# selection = uidoc.Selection.Elements  | 2015 API
# for door in mir_doors:                | 2015 API
    # selection.Add(door)               | 2015 API
