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

"""

import os
import pickle
from tempfile import gettempdir

import rpw
from rpw import doc, uidoc, DB, UI
from logger import log
log(__file__)
from viewport_wrapper import Point, ViewPortWrapper, move_to_match_vp_placment

tempfile = os.path.join(gettempdir(), 'ViewPlacement')
selection = rpw.ui.Selection()

if __name__ == '__main__':

    if len(selection) == 1 and isinstance(selection[0].unwrap(), DB.Viewport):
        viewport = selection[0].unwrap()
        try:
            with open(tempfile, 'rb') as fp:
                pt = pickle.load(fp)
        except IOError:
            UI.TaskDialog.Show('pyRevitPlus', 'Could not find saved viewport placement.\nCopy a Viewport Placement first.')
        else:
            saved_pt = DB.XYZ(pt.X, pt.Y, pt.Z)
            move_to_match_vp_placment(viewport, saved_pt)
    else:
        if len(selection) <> 1:
            UI.TaskDialog.Show('pyRevitPlus', 'Select 1 Viewport. No more, no less!')
        else:
            UI.TaskDialog.Show('pyRevitPlus', 'Not a viewport selected')

  #__window__.Close()

    # START
    # import webbrowser, random
    # url = "https://goo.gl/azmcWU"
    # chance = 50
    # if random.randint(0, chance) == 1:
    #    webbrowser.open(url,new=1, autoraise=True)
    # END
