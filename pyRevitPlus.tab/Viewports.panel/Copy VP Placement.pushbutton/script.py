"""
Copyright (c) 2016 Gui Talarico @ WeWork

CopyPasteViewportPlacemenet
Copy and paste the placement of viewports across sheets
github.com/gtalarico | @gtalarico

--------------------------------------------------------
pyRevit Notice:
pyRevit: repository at https://github.com/eirannejad/pyRevit

"""

__doc__ = 'Copy a Viewport Placement into memory'
__author__ = '@gtalarico'
__version__ = '0.2.0'
__title__ = "Copy VP\nPlacement"

import os
import pickle
from tempfile import gettempdir
from collections import namedtuple

# TODO: Move VP wrapper to rpw.
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import rpw
from rpw import doc, uidoc, DB, UI
from viewport_wrapper import Point, ViewPortWrapper

if __name__ == '__main__':

    tempfile = os.path.join(gettempdir(), 'ViewPlacement')
    selection = rpw.Selection()

    if len(selection) == 1 and isinstance(selection[0], DB.Viewport):
        viewport = selection[0]
        vp = ViewPortWrapper(viewport)
        origin = vp.project_origin_in_sheetspace
        pt = Point(origin.X, origin.Y, origin.Z)
        with open(tempfile, 'wb') as fp:
            pickle.dump(pt, fp)
    else:
        UI.TaskDialog.Show('pyRevitPlus', 'Select 1 Viewport. No more, no less!')

    __window__.Close()
