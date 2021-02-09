"""
CopyPasteViewportPlacemenet
Copy placement of selected viewport or schedule

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
from collections import namedtuple

import rpw
from rpw import doc, uidoc, DB, UI
#from logger import log
#log(__file__)
from viewport_wrapper import Point, ViewPortWrapper, move_to_match_vp_placment
from schedule_wrapper import ScheduleSheetWrapper, move_to_match_placement

if __name__ == '__main__':

    tempfile = os.path.join(gettempdir(), 'ViewPlacement')
    selection = rpw.ui.Selection()
    
    if len(selection) <> 1:
            UI.TaskDialog.Show('pyRevitPlus', 'Select a single Viewport or Schedule. No more, no less!')
            exit(0);
           
    if isinstance(selection[0].unwrap(), DB.Viewport) or isinstance(selection[0].unwrap(), DB.ScheduleSheetInstance):
        el = selection[0].unwrap()
        if isinstance(el, DB.Viewport):
            vp = ViewPortWrapper(el)
            origin = vp.project_origin_in_sheetspace
            msg = 'Saved viewport placement to {}'.format(tempfile)
        else:
            #UI.TaskDialog.Show('pyRevitPlus', 'Schedules not implemented yet')
            #exit(1);
            shd = ScheduleSheetWrapper(el)
            origin = shd.placement
            msg = 'Saved schedule placement to {}'.format(tempfile)
        
        pt = Point(origin.X, origin.Y, origin.Z)
        with open(tempfile, 'wb') as fp:
            pickle.dump(pt, fp)
        UI.TaskDialog.Show('pyRevitPlus', msg)
    else:
        UI.TaskDialog.Show('pyRevitPlus', 'Not a viewport or schedule selected')

  #__window__.Close()
