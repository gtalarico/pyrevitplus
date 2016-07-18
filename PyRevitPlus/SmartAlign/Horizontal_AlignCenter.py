"""
Copyright (c) 2014-2016 Gui Talarico

Smart Align
Smart Align is part of PyRevit Plus Optional Extensions for PyRevit
github.com/gtalarico | gtalarico@gmail.com

--------------------------------------------------------
pyRevit Notice:
pyRevit: repository at https://github.com/eirannejad/pyRevit

"""

import sys
import os
sys.path.append(os.path.dirname(__file__))
from SmartAlign import *

if not verbose:
    __window__.Close()

ALIGN = Justification.HCENTER
# ALIGN = Justification.HLEFT
# ALIGN = Justification.HRIGHT
# ALIGN = Justification.VCENTER
# ALIGN = Justification.VTOP
# ALIGN = Justification.VBOTTOM

main(ALIGN)
