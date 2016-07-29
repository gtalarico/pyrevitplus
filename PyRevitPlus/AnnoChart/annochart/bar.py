import itertools
import sys

from annochart.utils import revit_transaction, create_text
from annochart.revit import doc, uidoc, Autodesk

# from annochart.revit import Autodesk
from Autodesk.Revit.DB import Transaction
from Autodesk.Revit.DB import CurveLoop, Line, XYZ
from Autodesk.Revit.DB import FilledRegion
from System.Collections.Generic import List

class BarChart(object):
    def __init__(self, values, fregion_ids, **options):
        """BarChart: Creates a Bar Chart.
        bar_chart = BarChart(values:list, fregion_ids:list,
                             labels:list, value_labels:list,
                             bar_height=1,spacing=0.25,)
        bar_chart.draw(view_id)

        OPTIONS: [DEFAULT]
        bar_height: 1
        spacing: 0.25
        labels: defaults to None: Does not Print
        value_labels: defaults str() of values
        label_padding: spacing / 2
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

        self.value_labels = options.get('value_labels',
                                        [str(v) for v in values])
        self.labels = options.get('labels', ['' for v in values])
        self.label_padding = options.get('label_padding', self.spacing / 2)

        self.make_bars()

    def make_bars(self):
        self.bars = []
        y = self.start_y

        for n, value in enumerate(self.values):
            y += self.bar_height + self.spacing
            bar = Bar(self.start_x, y, value, self.bar_height,
                      value_label=self.value_labels[n], label=self.labels[n],
                      label_padding=self.label_padding)

            self.bars.append(bar)

    @revit_transaction("Draw Bar Chart")
    def draw(self, view):

        for bar, fregion_id in zip(self.bars, self.fregion_ids):

            bar.draw(view, fregion_id)
            create_text(view, bar.value_label, bar.value_label_pt, 'left')
            create_text(view, bar.label, bar.label_pt, 'right')


class Bar(object):
    """ Bar class.
    bar = Bar(start_x, start_y, width, height, value_label=None, label=None,
              label_padding=None)
    """
    def __init__(self, start_x, start_y, width, height,
                 value_label=None, label=None, label_padding=None):
        self.start_x = start_x
        self.start_y = start_y
        self.width = width
        self.height = height

        self.label_padding = label_padding or 0
        self.label = label
        self.value_label = value_label or str(width)

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
        points = [p1, p2, p3, p4, p5]
        print('=')
        print('width:', self.width)
        print('height:', self.height)
        print('start_x', start_x)
        print('start_y', start_y)
        for p in points:
            print('point:', p)

        profileloop = CurveLoop()
        profileloops = List[CurveLoop]()

        for n, p in enumerate(points):
            try:
                line = Line.CreateBound(points[n], points[n + 1])
            except:
                continue
            else:
                profileloop.Append(line)

        profileloops.Add(profileloop)

        # Defines Location for Label and Value Label
        label_x = start_x - self.label_padding
        label_y = start_y + (self.height / 2)
        value_label_x = start_x + self.width + self.label_padding
        value_label_y = label_y
        self.label_pt = XYZ(label_x, label_y, 0)
        self.value_label_pt = XYZ(value_label_x, value_label_y, 0)

        return profileloops

    def draw(self, view, filled_region_type_id):
        FilledRegion.Create(doc, filled_region_type_id,
                            view.Id, self.profile_loops)
