import itertools
import sys

from annochart.utils import revit_transaction, create_text, dialog
from annochart.revit import doc, uidoc

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

        fregion_ids = [list of field_region_type ids]
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
        if not values:
            dialog('Invalid Values: [{}]'.format(values))
            raise ValueError('values column is a valid sequence')
        self.values = values
        self.fregion_ids = fregion_ids

        # Optional Configutarions
        self.title = options.get('title')
        self.bar_height = options.get('bar_height', 1)
        self.spacing = options.get('spacing', 0.25)
        self.max_width = options.get('max_width', 1)

        self.value_labels = options.get('value_labels') or [str(v) for
                                                            v in values]
        self.labels = options.get('labels') or ['' for v in values]

        self.label_padding = options.get('label_padding', self.spacing / 2)

        scale_factor = self.max_width / max(self.values)
        if self.max_width is None:
            self.scaled_values = values
        else:
            self.scaled_values = [value * scale_factor for value in values]

        self.make_bars()

    def make_bars(self):
        self.bars = []
        y = self.start_y

        for n, value in enumerate(self.scaled_values):
            y += self.bar_height + self.spacing
            bar = Bar(self.start_x, y, value, self.bar_height,
                      self.fregion_ids[n],
                      self.value_labels[n], label=self.labels[n],
                      label_padding=self.label_padding)

            self.bars.append(bar)

    @revit_transaction("Draw Bar Chart")
    def draw(self, view):
        for bar in self.bars:

            bar.draw(view)
            create_text(view, bar.value_label, bar.value_label_pt, 'left')
            create_text(view, bar.label, bar.label_pt, 'right')
        if self.title:
            title_y = self.start_y
            title_pt = XYZ(self.start_x, title_y, 0)
            create_text(view, self.title, title_pt, 'left')


class Bar(object):
    """ Bar class.
    bar = Bar(start_x, start_y, width, height, value_label=None, label=None,
              label_padding=None)
    """
    def __init__(self, start_x, start_y, width, height,
                 fregion_id, value_label,
                 label=None, label_padding=None):
        DEFAULT_MIN = 0.01
        self.start_x = start_x
        self.start_y = start_y
        self.width = width or DEFAULT_MIN  # Zero Widht cannot be drawn
        self.height = height
        self.value_label = value_label
        self.fregion_id = fregion_id


        self.label_padding = label_padding or 0
        self.label = label

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

        profileloop = CurveLoop()
        profileloops = List[CurveLoop]()

        for n, p in enumerate(points):
            try:
                line = Line.CreateBound(points[n], points[n + 1])
            except:
                continue
            else:
                profileloop.Append(line)
        try:
            profileloops.Add(profileloop)
        except Exception as errmsg:
            dialog('Something wrong processing points: {}'.format(self.points))
            # ADD LOGGER
            logger.error('width: {}'.format(self.width))
            logger.error('height: {}'.format(self.height))
            logger.error('start_x: {}'.format(start_x))
            logger.error('start_y: {}'.format(start_y))
            for n, point in enumerate(points):
                logger.error('Point {}:{}'.format(n, point))

        # Defines Location for Label and Value Label
        label_x = start_x - self.label_padding
        label_y = start_y + (self.height / 2)
        value_label_x = start_x + self.width + self.label_padding
        value_label_y = label_y
        self.label_pt = XYZ(label_x, label_y, 0)
        self.value_label_pt = XYZ(value_label_x, value_label_y, 0)

        return profileloops

    def draw(self, view):
        FilledRegion.Create(doc, self.fregion_id,
                            view.Id, self.profile_loops)
