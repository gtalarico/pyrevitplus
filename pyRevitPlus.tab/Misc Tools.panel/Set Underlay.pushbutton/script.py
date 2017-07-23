"""
RemoveUnderlay
Removes Underlay From Selected Views.
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

# Parts of this script were taken from:
# http://dp-stuff.org/revit-view-underlay-property-python-problem/

__doc__ = 'Set Underlay Parameter From Selected Views.'
__author__ = '@gtalarico'
__version__ = '0.3.0'
__title__ = "Set\nUnderlay"

import sys
import rpw
from rpw import doc, uidoc, DB, UI, platform

selection = rpw.ui.Selection()
selected_views = [e for e in selection.elements if isinstance(e, DB.View)]

if platform.get('revit') != '2015':
    UI.TaskDialog.Show('API Change', str('This Tool only works for Revit 2015'))
    sys.exit()

if not selected_views:
    UI.TaskDialog.Show('Set Underlay', 'Must have a view actively selected in Project Browser.')
    __window__.Close(); sys.exit()

levels = rpw.db.Collector(of_category='OST_Levels', is_not_type=True).elements

levels_dict = {level.Name: level.Id for level in levels}
levels_dict['None'] = DB.ElementId.InvalidElementId
level_id = rpw.ui.forms.SelectFromList('Select Underlay', levels_dict,
                                    description="Select a Level")

selected_underlay_id = level_id
with rpw.db.Transaction('Batch Set Underlay to None'):
    for view in selected_views:
        rpw_view = rpw.db.Element(view)
        rpw_view.parameters.builtins['VIEW_UNDERLAY_ID'] = selected_underlay_id

__window__.Close()
