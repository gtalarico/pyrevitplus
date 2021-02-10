"""
BatchPasteVP
Paste the placement of Plan Views on All Sheets.

Select All sheets on the Project Browser.
Note:
Only the first VP found will be aligned. If you have multiple Viewports,
use the PasteVP on each individual Viewport.


TESTED REVIT API: 2015 | 2016 | 2017

@gtalarico
This script is part of PyRevitPlus: Extensions for PyRevit
github.com/gtalarico | @gtalarico

--------------------------------------------------------
RevitPythonWrapper: revitpythonwrapper.readthedocs.io
pyRevit: github.com/eirannejad/pyRevit

"""

import os
import sys
import pickle
from tempfile import gettempdir

import rpw
from rpw import doc, uidoc, DB, UI
#from logger import log
#log(__file__)
from viewport_wrapper import Point, ViewPortWrapper
from viewport_wrapper import Point, ViewPortWrapper, move_to_match_vp_placment

tempfile = os.path.join(gettempdir(), 'ViewPlacement')
selection = rpw.ui.Selection()

try:
    with open(tempfile, 'rb') as fp:
        pt = pickle.load(fp)
except IOError:
    UI.TaskDialog.Show('pyRevitPlus', 'Could not find saved viewport placement.\nCopy a Viewport Placement first.')
    sys.exit()
else:
    saved_pt = DB.XYZ(pt.X, pt.Y, pt.Z)

for viewsheet in [e for e in selection.elements if isinstance(e, DB.ViewSheet)]:
    viewports = rpw.db.Collector(view=viewsheet, of_class='Viewport').elements
    for viewport in viewports:
        view = doc.GetElement(viewport.ViewId)
        if isinstance(view, DB.ViewPlan):
            move_to_match_vp_placment(viewport, saved_pt)
        break

__window__.Close()
