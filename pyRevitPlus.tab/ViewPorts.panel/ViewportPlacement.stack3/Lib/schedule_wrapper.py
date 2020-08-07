"""
ScheduleSheetWrapper
a part of ViewportPlacemenet Tools

@ejs-ejs
This script is part of PyRevitPlus: Extensions for PyRevit
github.com/ejs-ejs | @ejs-ejs

Based on the code of ViewportPlacemenet Tools

@gtalarico
This script is part of PyRevitPlus: Extensions for PyRevit
github.com/gtalarico | @gtalarico

--------------------------------------------------------
RevitPythonWrapper: revitpythonwrapper.readthedocs.io
pyRevit: github.com/eirannejad/pyRevit

"""

import rpw
from rpw import doc, DB
from collections import namedtuple

Point = namedtuple('Point', ['X', 'Y','Z'])

class ScheduleSheetWrapper():
    def __init__(self, schedule):
        if not isinstance(schedule, DB.ScheduleSheetInstance):
            raise TypeError('Element is not a schedule: {}'.format(schedule))

        # vp_outline
        # Space: Sheet | Origin: Sheet View Origin
        placement = schedule.Point
        self.placement = schedule.Point

    def print_attributes(self):
        for k, v in self.__dict__.iteritems():
            print('{} : {}'.format(k,v ))


def move_to_match_placement(schedule, saved_pt):
    """ Moved viewport so base point matches the pt saved """
    vp = ScheduleSheetWrapper(schedule)
    current_origin = vp.placement
    delta = saved_pt - current_origin
    if schedule.Pinned:
        with rpw.db.Transaction('Unpin Schedule'):
            schedule.Pinned = False
    with rpw.db.Transaction('Paste Schedule Placement'):
        try:
            schedule.Location.Move(delta)
            schedule.Pinned = True
            schedule = rpw.db.Element(schedule)
        except Exception as errmsg:
            print('Could not set some parameters: {}'.format(errmsg))
