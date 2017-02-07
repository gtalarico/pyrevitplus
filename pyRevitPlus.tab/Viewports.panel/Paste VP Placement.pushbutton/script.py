"""
Copyright (c) 2016 Gui Talarico @ WeWork

Paste Viewport Placemenet
Paste the placement of viewports
github.com/gtalarico | @gtalarico

--------------------------------------------------------
pyRevit Notice:
pyRevit: repository at https://github.com/eirannejad/pyRevit

"""

__doc__ = 'Paste a Viewport Placement from memory'
__author__ = '@gtalarico'
__version__ = '0.2.0'
__title__ = "Paste VP\nPlacement"


import os
import pickle
from tempfile import gettempdir

# TODO: Move VP wrapper to rpw.
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import rpw
from rpw import doc, uidoc, DB, UI
from viewport_wrapper import Point, ViewPortWrapper

tempfile = os.path.join(gettempdir(), 'ViewPlacement')
selection = rpw.Selection()


if __name__ == '__main__':

    if len(selection) == 1 and isinstance(selection[0], DB.Viewport):
        viewport = selection[0]
        try:
            with open(tempfile, 'rb') as fp:
                pt = pickle.load(fp)
        except IOError:
            UI.TaskDialog.Show('pyRevitPlus', 'Could not find saved viewport placement.\nCopy a Viewport Placement first.')
        else:
            saved_pt = DB.XYZ(pt.X, pt.Y, pt.Z)

            vp = ViewPortWrapper(viewport)
            current_origin = vp.project_origin_in_sheetspace
            delta = saved_pt - current_origin
            if viewport.Pinned:
                with rpw.Transaction('Unpin Viewport'):
                    viewport.Pinned = False
            with rpw.Transaction('Paste Viewport Placement'):
                viewport.Location.Move(delta)
                viewport.Pinned = True
                viewport = rpw.Element(viewport)
                try:
                    # TODO: Make these optional
                    viewport.parameters.builtins['VIEWER_CROP_REGION_VISIBLE'] = 0
                    viewport.parameters.builtins['VIEWER_ANNOTATION_CROP_ACTIVE'] = 0
                    viewport.parameters.builtins['VIEWER_CROP_REGION'] = 1
                except Exception as errmsg:
                    print('Could not set some parameters: {}'.format(errmsg))
    else:
        UI.TaskDialog.Show('pyRevitPlus', 'Select 1 Viewport. No more, no less!')

    __window__.Close()
