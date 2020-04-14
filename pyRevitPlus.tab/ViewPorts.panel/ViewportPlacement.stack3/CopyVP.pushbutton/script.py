"""
CopyPasteViewportPlacemenet
Copy placement of selected viewport

TESTED REVIT API: 2015 | 2016 | 2017

@gtalarico
This script is part of PyRevitPlus: Extensions for PyRevit
github.com/gtalarico | @gtalarico

--------------------------------------------------------
RevitPythonWrapper: revitpythonwrapper.readthedocs.io
pyRevit: github.com/eirannejad/pyRevit

"""

import os
import pickle
from tempfile import gettempdir
from collections import namedtuple

import rpw
from rpw import doc, uidoc, DB, UI
from logger import log
log(__file__)
from viewport_wrapper import Point, ViewPortWrapper, move_to_match_vp_placment

if __name__ == '__main__':

    tempfile = os.path.join(gettempdir(), 'ViewPlacement')
    selection = rpw.ui.Selection()

    if len(selection) == 1 and isinstance(selection[0].unwrap(), DB.Viewport):
        viewport = selection[0].unwrap()
        vp = ViewPortWrapper(viewport)
        origin = vp.project_origin_in_sheetspace
        pt = Point(origin.X, origin.Y, origin.Z)
        with open(tempfile, 'wb') as fp:
            pickle.dump(pt, fp)
    else:
        if len(selection) <> 1:
            UI.TaskDialog.Show('pyRevitPlus', 'Select 1 Viewport. No more, no less!')
        else:
            UI.TaskDialog.Show('pyRevitPlus', 'Not a viewport selected')

  #__window__.Close()
