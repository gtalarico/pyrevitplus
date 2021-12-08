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
__doc__ = 'Align Elements Vertically: Top'

import sys
import os
sys.path.append(os.path.dirname(__file__))
from smartalign.align import main
from smartalign.core import Alignment, VERBOSE

# ALIGN = Alignment.HCENTER
# ALIGN = Alignment.HLEFT
# ALIGN = Alignment.HRIGHT
# ALIGN = Alignment.VCENTER
ALIGN = Alignment.VTOP
# ALIGN = Alignment.VBOTTOM

main(ALIGN)
