import sys
sys.path.append(r'C:\Users\gtalarico\Dropbox\Shared\dev-ubuntu\repos\pyRevit\pyRevit\pyRevitPlus')
sys.path.append(r'C:\python\Lib')

import annochart
#Assign your output to the OUT variable.
from annochart.bar import BarChart
from annochart.schedules import get_schedule_values
from annochart.utils import (fregion_id_by_name, create_drafting_view,
                             create_text)

from annochart.revit import doc, uidoc, ActiveView


__doc__ = "Creates Bar Chart from active Schedule"

values = IN[0]
schedule = IN[1]
view = UnwrapElement(IN[2]) or ActiveView

colors = values
if schedule is not None:
    schedule = UnwrapElement(schedule)
    schedule_dict = get_schedule_values(schedule)
    values = schedule_dict['values']
    colors = schedule_dict['colors']
    labels = colors
else:
    colors = ['live' for v in values]
    labels = ['' for v in values]

scale_factor = 5 / max(values)
scaled_values = [value * scale_factor for value in values]

fregion_ids = [fregion_id_by_name(str(color)) for color in colors]
bar_chart = BarChart(scaled_values, fregion_ids,
                     bar_height=0.20, spacing=0.125,
                     value_labels=values, labels=labels)
bar_chart.draw(view)

OUT = values
