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
__title__ = "Select Mirrored\nDoors"

from rpw import doc, uidoc, DB, UI, db, ui

doors = db.Collector(of_category='Doors').elements
mirrored_door = [door for door in doors if getattr(door, 'Mirrored', False)]

msg = "Mirrored: {} of {} Doors".format(len(mirrored_door), len(doors))
ui.forms.Alert(msg, title="Mirrored Doors")

selection = ui.Selection(mirrored_door)
