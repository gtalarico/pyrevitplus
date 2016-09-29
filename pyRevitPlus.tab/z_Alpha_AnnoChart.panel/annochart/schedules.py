from Autodesk.Revit.DB import ViewSchedule
from Autodesk.Revit.DB import SectionType

from annochart.revit import doc, uidoc
from annochart.utils import dialog


def get_schedule_values(view, round_decimals=2):
    """Gets list of values from first column.
    Move Data parsing here
    """
    HEADER_VALUES = 'values'

    def coerce_value(value):
        try:
            value = float(value)
        except Exception as errmsg:
            dialog('Found non-number in values column: {}'.format(value))
            raise ValueError('All cells in teh values column must be numbers')
        else:
            return round(value, round_decimals)

    def validate_schedule(schedule_dict):
        if HEADER_VALUES in schedule_dict.keys():
            return schedule_dict
        else:
            dialog('You must have a numeric column labeled: values')


    if not isinstance(view, ViewSchedule):
        dialog('View must be a schedule')
    else:
        schedule = view
        body = schedule.GetTableData().GetSectionData(SectionType.Body)
        header = schedule.GetTableData().GetSectionData(SectionType.Body)
        first_row = body.FirstRowNumber
        schedule_name = schedule.Title

        qty_rows = body.NumberOfRows
        qty_cols = body.NumberOfColumns
        schedule_dict = {}
        schedule_dict['title'] = schedule_name
        for col in range(0, qty_cols):
            col_header = schedule.GetCellText(SectionType.Body, 0, col)
            schedule_dict[col_header] = []
            for row in range(2, qty_rows):
                cells = []
                cell = schedule.GetCellText(SectionType.Body, row, col)
                print('Cell:', cell)

                if col_header == 'values':
                    cell = coerce_value(cell)
                schedule_dict[col_header].append(cell)

        return validate_schedule(schedule_dict)
