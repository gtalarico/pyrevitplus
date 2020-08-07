"""
CopyPasteViewportPlacemenet
Paste the placement of on selected viewport

TESTED REVIT API: 2015 | 2016 | 2017

@gtalarico
This script is part of PyRevitPlus: Extensions for PyRevit
github.com/gtalarico | @gtalarico

--------------------------------------------------------
RevitPythonWrapper: revitpythonwrapper.readthedocs.io
pyRevit: github.com/eirannejad/pyRevit

Schedule support added by @ejs-ejs
github.com/ejs-ejs | @ejs-ejs
TESTED REVIT API: 2020
"""

import os
import pickle
from tempfile import gettempdir

import rpw
from rpw import doc, uidoc, DB, UI
#from logger import log
#log(__file__)
from viewport_wrapper import Point, ViewPortWrapper, move_to_match_vp_placment
from schedule_wrapper import ScheduleSheetWrapper, move_to_match_placement

tempfile = os.path.join(gettempdir(), 'ViewPlacement')
selection = rpw.ui.Selection()

if __name__ == '__main__':

    if len(selection) <> 1:
            UI.TaskDialog.Show('pyRevitPlus', 'Select single Viewport or Schedule. No more, no less!')
            
    if isinstance(selection[0].unwrap(), DB.Viewport) or isinstance(selection[0].unwrap(), DB.ScheduleSheetInstance):
        ent = selection[0].unwrap()
        try:
            with open(tempfile, 'rb') as fp:
                pt = pickle.load(fp)
        except IOError:
            UI.TaskDialog.Show('pyRevitPlus', 'Could not find saved viewport or schedule placement.\nCopy a Viewport or Schedule placement first.')
        else:
            saved_pt = DB.XYZ(pt.X, pt.Y, pt.Z)
        if isinstance(ent, DB.Viewport):
            move_to_match_vp_placment(ent, saved_pt)
        else:
            move_to_match_placement(ent, saved_pt)
    else:
        UI.TaskDialog.Show('pyRevitPlus', 'Not a viewport or schedule selected')

  #__window__.Close()

