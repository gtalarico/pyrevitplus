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

__doc__ = 'Cycles through available types in family manager. \n' \
          'Must be in Family Document.'
__author__ = '@gtalarico'

from Autodesk.Revit.DB import Transaction
from Autodesk.Revit.UI import TaskDialog

import os
import pickle
import sys
from tempfile import gettempdir

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
__window__.Close()


def dump_types():
    type_list = []
    for family_type in family_type_names:
        type_list.append(family_type.Name)

    with open(temp, 'w') as fp:
        pickle.dump(type_list, fp)
    return type_list


if not doc.IsFamilyDocument:
    TaskDialog.Show('pyRevitPlus', 'Must be in Family Document.')

else:
    family_types = [x for x in doc.FamilyManager.Types]
    current_type = doc.FamilyManager.CurrentType
    temp = os.path.join(gettempdir(), 'CycleTypes')
    
    try:
        with open(temp, 'r') as fp:
            type_list = pickle.load(fp)
    except IOError:
            type_list = dump_types()

    is_next = False
    max = 0
    while True:
        max += 1
        if max > 10:
            raise Exception('Max Limit')

        for family_type in family_types:
            if family_type.Name == current_type.Name:
                print('Found Current.')
                is_next = True
                continue
            if is_next:
                t = Transaction(doc, 'Cycle Type')
                t.Start()
                doc.FamilyManager.CurrentType = family_type
                t.Commit()
                sys.exit()




        #
