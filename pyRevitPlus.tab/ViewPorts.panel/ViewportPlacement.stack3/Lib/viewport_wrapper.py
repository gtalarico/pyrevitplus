"""
ViewportPlacemenet Tools

@gtalarico
This script is part of PyRevitPlus: Extensions for PyRevit
github.com/gtalarico | @gtalarico

--------------------------------------------------------
RevitPythonWrapper: revitpythonwrapper.readthedocs.io
pyRevit: github.com/eirannejad/pyRevit

"""

import rpw
from rpw import doc, DB
from collections import namedtuple

Point = namedtuple('Point', ['X', 'Y','Z'])

def uv_to_pt(uv):
    return DB.XYZ(uv.U, uv.V, 0)

class ViewPortWrapper():
    def __init__(self, viewport):
        if not isinstance(viewport, DB.Viewport):
            raise TypeError('Element is not a viewport: {}'.format(viewport))

        # vp_outline
        # Space: Sheet | Origin: Sheet View Origin
        vp_outline = viewport.GetBoxOutline()
        vp_outline_min = DB.XYZ(vp_outline.MinimumPoint.X, vp_outline.MinimumPoint.Y, 0)
        vp_outline_max = DB.XYZ(vp_outline.MaximumPoint.X, vp_outline.MaximumPoint.Y, 0)

        # view_outline
        # Space: Sheet | Origin: Project Base Point
        view = doc.GetElement(viewport.ViewId)
        view_outline = view.Outline
        view_outline_min = uv_to_pt(view_outline.Min)
        view_outline_max = uv_to_pt(view_outline.Max)

        self.project_origin_in_sheetspace = vp_outline_min - view_outline_min


    def print_attributes(self):
        for k, v in self.__dict__.iteritems():
            print('{} : {}'.format(k,v ))


def move_to_match_vp_placment(viewport, saved_pt):
    """ Moved viewport so base point matches the pt saved """
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
            viewport.parameters.builtins['VIEWER_CROP_REGION_VISIBLE'] = 0
            viewport.parameters.builtins['VIEWER_ANNOTATION_CROP_ACTIVE'] = 0
            viewport.parameters.builtins['VIEWER_CROP_REGION'] = 1
        except Exception as errmsg:
            print('Could not set some parameters: {}'.format(errmsg))
