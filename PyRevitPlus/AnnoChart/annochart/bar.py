import itertools

from Autodesk.Revit.DB import Transaction
from Autodesk.Revit.DB import CurveLoop, Line, XYZ
from Autodesk.Revit.DB import FilledRegion
from System.Collections.Generic import List

from annochart.utils import revit_transaction, create_text
from annochart.revit import doc, uidoc

class BarChart(object):
    def __init__(self, values, fregion_ids, **options):
        """BarChart: Creates a Bar Chart.
        bar_chart = BarChart(values:list, fregion_ids:list,
                             bar_height=1,spacing=0.25)
        bar_chart.draw(view_id)
        """
        # Hard coded settings
        self.start_x = 0
        self.start_y = 0

        # Required Arguments
        self.values = values
        self.fregion_ids = itertools.cycle(fregion_ids)

        # Optional Configutarions
        self.bar_height = options.get('bar_height', 1)
        self.spacing = options.get('spacing', 0.25)
        self.legend_values = options.get('legend_values', values)

        self.make_bars()

    def make_bars(self):
        self.bars = []
        legend_padding = self.spacing / 2

        y = self.start_y
        for value, legend_value in zip(self.values, self.legend_values):
            y += self.bar_height + self.spacing
            bar = Bar(self.start_x, y, value, self.bar_height,
                      legend_value=legend_value,
                      legend_padding=legend_padding)
            self.bars.append(bar)


    @revit_transaction("Draw Bar Chart")
    def draw(self, view):
        for bar, fregion_id in zip(self.bars,self.fregion_ids):
            bar.draw(view, fregion_id)
            create_text(view, bar.legend_value, bar.legend_pt)

class Bar(object):
    def __init__(self, start_x, start_y, width, height,
                 legend_padding=None, legend_value=None):
        self.start_x = start_x
        self.start_y = start_y
        self.width = width
        self.height = height

        self.legend_padding = legend_padding or 0
        self.legend_value = str(legend_value) or str(width)

        self.profile_loops = self.make_loops()

    def make_loops(self):
        start_x = self.start_x
        start_y = self.start_y
        end_x = start_x + self.width
        end_y = start_y + self.height
        p1 = XYZ(start_x, start_y, 0.0)
        p2 = XYZ(end_x, start_y, 0.0)
        p3 = XYZ(end_x, end_y, 0.0)
        p4 = XYZ(start_x, end_y, 0.0)
        p5 = XYZ(start_x, start_y, 0.0)
        points = [p1,p2,p3,p4,p5]
        profileloop = CurveLoop()
        profileloops = List[CurveLoop]()

        for n, p in enumerate(points):
            try:
                line = Line.CreateBound(points[n], points[n+1])
            except:
                continue
            else:
                profileloop.Append(line)

        profileloops.Add(profileloop)
        legend_x = start_x - self.legend_padding
        legend_y = start_y + (self.height/2)
        self.legend_pt = XYZ(legend_x, legend_y, 0)
        return profileloops

    def draw(self, view, filled_region_type_id):
        FilledRegion.Create(doc, filled_region_type_id,
                            view.Id, self.profile_loops)
