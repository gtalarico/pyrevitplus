from rpw import doc, DB
from collections import namedtuple

# TODO: Move to RPW

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
