"""
OpenInExcel
Opens Selected schedules in Excel
TESTED REVIT API: 2015 | 2016 | 2017

Copyright (c) 2014-2016 Gui Talarico @ WeWork
github.com/gtalarico

This script is part of PyRevitPlus: Extensions for PyRevit
github.com/gtalarico

--------------------------------------------------------
PyRevit Notice:
Copyright (c) 2014-2016 Ehsan Iran-Nejad
pyRevit: repository at https://github.com/eirannejad/pyRevit

"""

__doc__ = 'Opens Selected schedules in Excel'
__author__ = '@gtalarico'
__version__ = '0.3.0'
__title__ = "Open in\nExcel"

import os
import sys
import subprocess
import time

import rpw
from rpw import doc, uidoc, DB, UI

# Export Settings
temp_folder = os.path.expandvars('%temp%\\')
export_options = DB.ViewScheduleExportOptions()

# Get Saved Excelp Paths
saved_paths = os.path.join(os.path.dirname(__file__), 'OpenInExcel_UserPaths.txt')
with open(saved_paths) as fp:
    excel_paths = fp.read().split('\n')

for excel_path in excel_paths:
    if os.path.exists(excel_path):
        break
else:
    UI.TaskDialog.Show('OpenInExcel', 'Could not find Excel Path \n'
                       'Please add your Excel path to OpenInExcel_UserPaths.txt'
                       'and try again.')
    os.system('start notepad \"{path}\"'.format(path=saved_paths))
    sys.exit()


selection = rpw.Selection()

# Get any selected View Schedules or Schedule Instances
selected_schedules = [e for e in selection.elements
                      if isinstance(e, (DB.ViewSchedule, DB.ScheduleSheetInstance))]

# If no view is selected, check if Active View is a schedule
if not selected_schedules and isinstance(uidoc.ActiveView, DB.ViewSchedule):
    selected_schedules = [uidoc.ActiveView]
elif not selected_schedules:
    UI.TaskDialog.Show('OpenInExcel', 'Must have a schedule open or selected \
                       in the Project Browser.')

for schedule in selected_schedules:
    schedule_name = "".join([x for x in schedule.ViewName if x.isalnum()])

    # Adds random digits to avoid name clash
    filename = '{}_{}.txt'.format(schedule_name, str(time.time())[-2:])

    schedule.Export(temp_folder, filename, export_options)

    try:
        full_filepath = os.path.join(temp_folder, filename)
        os.system('start excel \"{path}\"'.format(path=full_filepath))
        continue
    except:
        print('Sorry, something failed:')

__window__.Close()
