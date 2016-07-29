from Autodesk.Revit.DB import ViewSchedule
from Autodesk.Revit.DB import SectionType

from annochart.revit import doc, uidoc


def get_schedule_values(schedule=None):
    def coerce_value(value):
        try:
            value = float(value)
        except Exception as errmsg:
            pass
        else:
            # if value.is_integer():
                # return int(value)
            return value

    """Gets list of values from first column.
    Move Data parsing here
    """
    if schedule is None:
        schedule = doc.GetElement(doc.ActiveView.Id)

    if not isinstance(schedule, ViewSchedule):
        print('Active View must be a schedule.')
        return 'Not a Schedule'
    else:
        body = schedule.GetTableData().GetSectionData(SectionType.Body)
        header = schedule.GetTableData().GetSectionData(SectionType.Body)
        first_row = body.FirstRowNumber
        schedule_name = schedule.Title

        qty_rows = body.NumberOfRows
        qty_cols = body.NumberOfColumns
        schedule_dict = {}
        for col in range(0, qty_cols):
            col_header = schedule.GetCellText(SectionType.Body, 0, col)
            schedule_dict[col_header] = []
            for row in range(1, qty_rows):
                cells = []
                cell = schedule.GetCellText(SectionType.Body, row, col)
                if cell:
                    if col_header == 'values':
                        cell = coerce_value(cell)
                    schedule_dict[col_header].append(cell)

        return schedule_dict
