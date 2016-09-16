"""
CycleType
Cycle through available types in family manager
TESTED REVIT API: 2015

Copyright (c) 2016 Gui Talarico
github.com/gtalarico

This script is part of PyRevitPlus: Extensions for PyRevit
github.com/gtalarico/pyrevitplus/

--------------------------------------------------------
PyRevit Notice:
Copyright (c) 2014-2016 Ehsan Iran-Nejad
pyRevit: repository at https://github.com/eirannejad/pyRevit

"""

__doc__ = 'Cycle through available types in family manager. \n' \
          'Must be in Family Document.'
__author__ = '@gtalarico'

from Autodesk.Revit.DB import Transaction
from Autodesk.Revit.UI import TaskDialog

import os
import subprocess

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

t = Transaction(doc, 'Cycle Type')
__window__.Close()

if doc.IsFamilyDocument:
    current_type = doc.FamilyManager.CurrentType
    print('Current:', current_type.Name)
    family_types = doc.FamilyManager.Types
    for n, family_type in enumerate(family_types):
        t.Start()

        doc.FamilyManager.CurrentType = family_type
        t.Commit()
        break
else:
    TaskDialog.Show('pyRevitPlus', 'Must be in Family Document.')
