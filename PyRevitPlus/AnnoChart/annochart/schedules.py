from Autodesk.Revit.DB import ViewSchedule
from Autodesk.Revit.DB import SectionType

from annochart.revit import doc, uidoc

def get_schedule_values():
    """Gets list of values from first column.
    Needs Improvement to eliminate Header, Pick Column, Etc
    """
    schedule = doc.GetElement(doc.ActiveView.Id)
    print(schedule)
    if not isinstance(schedule, ViewSchedule):
        print('Active View must be a schedule.')
    else:
        bodySection = schedule.GetTableData().GetSectionData(SectionType.Body)
        headerSection = schedule.GetTableData().GetSectionData(SectionType.Body)
        first_row = bodySection.FirstRowNumber
        schedule_name = schedule.Title

        # print('Exporting Schedule: {}'.format(schedule_name))
        # print('Header:', headerSection)
        # print('Body:', bodySection)
        # print('FirstRow:', first_row)

        qty_rows = bodySection.NumberOfRows
        qty_cols = bodySection.NumberOfColumns
        values = []
        for row in range(0, qty_rows):
            for col in range(0, 1):
                cell = schedule.GetCellText(SectionType.Body, row, col)
                values.append(cell)

        return values
