import sys
import os
sys.path.append(os.path.dirname(__file__))

from annochart.bar import BarChart
from annochart.utils import fregion_id_by_name, create_drafting_view, create_text
from annochart.schedules import get_schedule_values
from annochart.revit import doc, uidoc


def main(values):
    max_length = 2.0
    scale_factor = max_length / max(values)
    print('Max:', max(values))
    print('Scale:', scale_factor)
    scaled_values = [value * scale_factor for value in values]

    view = create_drafting_view() # or doc.ActiveView.Id

    fregion_ids = [fregion_id_by_name('Chart1')]
    # fregion_ids = [fregion_id_by_name('Chart1'), fregion_id_by_name('Chart2')]

    bar_chart = BarChart(scaled_values, fregion_ids,
                         bar_height=0.10, spacing=0.075,
                         legend_values=values)
    bar_chart.draw(view)

    uidoc.ActiveView = view
    print('Done')
    # __window__.Close()

string_values = get_schedule_values()
if string_values is not None:
    try:
        values = [float(value) for value in string_values[2:]]
    except ValueError as errmsg:
        print('I cannot understand this table.')
        print('Error:', errmsg)
    else:
        main(values)