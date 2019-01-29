"""
Copyright (c) 2014-2016 Gui Talarico

Smart Align
Smart Align is part of PyRevit Plus Optional Extensions for PyRevit
github.com/gtalarico | @gtalarico

--------------------------------------------------------
pyRevit Notice:
pyRevit: repository at https://github.com/eirannejad/pyRevit

"""
#pylint: disable=E0401,W0621,W0631,C0413,C0111,C0103
__author__ = 'Gui Talarico | @gtalarico'
__version__ = '0.4.0'
__doc__ = 'Align Elements Vertically: Bottom'

import sys
import os
sys.path.append(os.path.dirname(__file__))
from smartalign.align import main
from smartalign.core import Align, VERBOSE

if not VERBOSE:
    #__window__.Close()
    pass

# ALIGN = Align.HCENTER
# ALIGN = Align.HLEFT
# ALIGN = Align.HRIGHT
# ALIGN = Align.VCENTER
# ALIGN = Align.VTOP
ALIGN = Align.VBOTTOM

main(ALIGN)
