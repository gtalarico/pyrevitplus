import sys
import os
sys.path.append(os.path.dirname(__file__))

from annochart.revit import doc, uidoc
from annochart.bar import BarChart
from annochart.schedules import get_schedule_values
from annochart.utils import (fregion_id_by_name, create_drafting_view,
                             create_text)

__doc__ = "Creates Bar Chart from active Schedule"


def make_chart(values, labels, colors, **options):
    view = create_drafting_view()  # or doc.ActiveView.Id

    fregion_ids = [fregion_id_by_name(color) for color in colors]
    max_width = options.get('max_width', 5.0)
    label_values = values

    scale_factor = max_width / max(values)
    scaled_values = [value * scale_factor for value in values]

    print('Values: ', values)
    print('Scale factor: ', scaled_values)
    print('Scaled values: ', scaled_values)

    bar_chart = BarChart(scaled_values, fregion_ids,
                         bar_height=0.10, spacing=0.075,
                         labels=labels, value_labels=values)

    bar_chart.draw(view)
    uidoc.ActiveView = view
    print('Done')
    # __window__.Close()

schedule_dict = get_schedule_values()
values = schedule_dict['values']
labels = schedule_dict['labels']
colors = schedule_dict['colors']

# if not all([values, colors, labels]):
    # print('Schedule not set correctly.')
# else:
make_chart(values, labels, colors, max_width=5)
    # try:
    #     values = [float(value) for value in string_values[2:]]
    # except ValueError as errmsg:
    #     print('I cannot understand this table.')
    #     print('Error:', errmsg)
    # else:
    #     # main(values)
