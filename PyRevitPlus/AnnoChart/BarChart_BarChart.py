import sys
import os
sys.path.append(os.path.dirname(__file__))

from annochart.revit import doc, uidoc, ActiveView
from annochart.bar import BarChart
from annochart.schedules import get_schedule_values
from annochart.utils import (fregion_id_by_name, create_drafting_view,
                             create_text, logger)

__doc__ = """Creates Bar Chart from active Schedule.
             Schedule must have a numeric column labeled 'values'.
             Optional columns:
             colors: name of filled region to be used.
             labels: label to the left of bar.
             value_labels: label to the right of bar.
             """

schedule_dict = get_schedule_values(ActiveView, round_decimals=2)

if schedule_dict:

    values = schedule_dict['values']
    value_labels = schedule_dict.get('value_labels', values)
    colors = schedule_dict.get('colors', ['' for value in values])
    labels = schedule_dict.get('labels', None)
    title = schedule_dict.get('title','')

    fregion_ids = [fregion_id_by_name(color) for color in colors]

    view = create_drafting_view()

    logger.debug('Values: {}'.format(values))
    logger.debug('value_labels: {}'.format(value_labels))
    logger.debug('labels: {}'.format(labels))
    logger.debug('colors: {}'.format(colors))

    bar_chart = BarChart(values, fregion_ids,
                         bar_height=0.20, spacing=0.15, max_width=2,
                         labels=labels, value_labels=value_labels,
                         title=title)

    bar_chart.draw(view)
    uidoc.ActiveView = view
    print('Done')

    __window__.Close()
