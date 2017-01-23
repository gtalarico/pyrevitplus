"""

Copyright (c) 2016 WeWork | Gui Talarico
Base script taken from pyRevit Respository.

pyRevit Notice
#################################################################
Copyright (c) 2014-2016 Ehsan Iran-Nejad
Python scripts for Autodesk Revit

This file is part of pyRevit repository at https://github.com/eirannejad/pyRevit

pyRevit is a free set of scripts for Autodesk Revit: you can redistribute it and/or modify
it under the terms of the GNU General Public License version 3, as published by
the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

See this link for a copy of the GNU General Public License protecting this package.
https://github.com/eirannejad/pyRevit/blob/master/LICENSE
"""

__doc__ = "Opens Selected Schedules in a Spreadsheet (Excel, LibreOffice)"
__title__ = "Open in\nExcel"

from Autodesk.Revit.DB import ViewSchedule, ViewScheduleExportOptions
from Autodesk.Revit.DB import ExportColumnHeaders, ExportTextQualifier
from Autodesk.Revit.DB import BuiltInCategory

import os

engine = None
editors_paths = [
    r"C:\Program Files\Programs\Office 2010\Office14\EXCEL.exe",
    r"C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE",
    r"C:\Program Files (x86)\Microsoft Office\Office14\EXCEL.exe",
    r"C:\Program Files (x86)\Microsoft Office\Office15\EXCEL.EXE",
    
    r"C:\Program Files (x86)\LibreOffice 5\program\scalc.exe",
    r"C:\Program Files (x86)\LibreOffice 4\program\scalc.exe",
]   # to add another editor, just check if the name can be used as cmd shortcut

def export():    
    uidoc = __revit__.ActiveUIDocument
    doc = __revit__.ActiveUIDocument.Document    
    
    destination = os.path.expandvars('%temp%\\')
    # destination = os.path.expandvars('%userprofile%\\desktop')        
    # destination = os.path.dirname(doc.PathName) #+ '\\schedules'

    vseop = ViewScheduleExportOptions()
    # vseop.ColumnHeaders = ExportColumnHeaders.None
    # vseop.TextQualifier = ExportTextQualifier.None
    # vseop.FieldDelimiter = ','
    # vseop.Title = False

    selected_ids = uidoc.Selection.GetElementIds()

    if not selected_ids.Count:
        '''If nothing is selected, use Active View'''
        selected_ids=[ doc.ActiveView.Id ]
        
    passed = 0
    for element_id in selected_ids:
        passed += 1
        element = doc.GetElement(element_id)
        if not isinstance(element, ViewSchedule):
            print('No schedule in Selection. Skipping...')
            continue

        filename = "".join(x for x in element.ViewName if x not in {'/','*'}) + '.txt'
        full_filepath = os.path.join(destination, filename)
        
        try:
            step='EXPORTING schedule {} to TEXTFILE'.format(element.ViewName)
            element.Export(destination, filename, vseop)
            print('EXPORTED: {0}\n      TO: {1}\n'.format(element.ViewName, filename))
            
            step='OPENING with {}'.format(engine)
            os.system('start {0} \"{1}\"'.format(engine, full_filepath))
            if passed == selected_ids.Count:
                __window__.Close()
            
        except:
            passed -= 1
            print('Sorry, an Error occured in {}'.format(step))
            print('...Maybe another dialog is opened ?')
            print('- Filename: {}'.format(filename))
            print('- Destination: {}'.format(destination))
            print('- Editor used : {}\n'.format(lpath))
    
    print('Export Ended. You can close this dialog.')
    
# loop then split the name to adapt the command in func export()
for lpath in editors_paths:
    if os.path.exists(lpath):    
        basepath = os.path.basename(lpath)
        engine = os.path.splitext(basepath)[0]
        if engine : 
            print('Editor Found. Trying to export...\n')
            export()
            break
else:
    print('Could not find editor with the following paths:\n'
    '{}\n'.format('\n'.join(editors_paths)))
    print('You can edit this script to add another folder :\n'
    '{}\n'.format(os.path.realpath(__file__)))
    
