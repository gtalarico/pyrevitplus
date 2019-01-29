"""
SelectMirroredWindows
Selects All Window Instances that have been Mirrored.
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
#pylint: disable=E0401,W0621,W0631,C0413,C0111,C0103
__doc__ = "Selects All Window Instances that have been Mirrored."
__author__ = '@gtalarico'
__title__ = "Select Mirrored\nWindows"

from rpw import db, ui

windows = db.Collector(of_category='Windows').elements
mirrored_windows = [x for x in windows if getattr(x, 'Mirrored', False)]

msg = "Mirrored: {} of {} Windows".format(len(mirrored_windows), len(windows))
ui.forms.Alert(msg, title="Mirrored Windows")

selection = ui.Selection(mirrored_windows)
