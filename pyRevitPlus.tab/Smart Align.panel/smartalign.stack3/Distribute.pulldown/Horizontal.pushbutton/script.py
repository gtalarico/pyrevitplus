"""
Copyright (c) 2014-2016 Gui Talarico

Smart Align
Smart Align is part of PyRevit Plus Optional Extensions for PyRevit
github.com/gtalarico | @gtalarico

--------------------------------------------------------
pyRevit Notice:
pyRevit: repository at https://github.com/eirannejad/pyRevit

"""

__author__ = 'Gui Talarico | @gtalarico'
__version__ = '0.4.0'
__doc__ = 'Distribute Elements Horizontally'

import sys
import os
sys.path.append(os.path.dirname(__file__))
from smartalign.distribute import main
from smartalign.core import Align, VERBOSE

if not VERBOSE:
    __window__.Close()

ALIGN = Align.HDIST
# ALIGN = Align.VDIST
main(ALIGN)
