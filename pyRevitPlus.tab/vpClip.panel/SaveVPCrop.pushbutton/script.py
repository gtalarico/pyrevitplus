"""
Save ViewPort Crop
Save crop boundary of a Viewport


Saves the cropping boundary of the active viewport for reuse.


TESTED REVIT API: 2020

github.com/ejs-ejs
--------------------------------------------------------
RevitPythonWrapper: revitpythonwrapper.readthedocs.io
pyRevit: github.com/eirannejad/pyRevit

"""

import os
import pickle
from tempfile import gettempdir
from collections import namedtuple
import rpw
from rpw import doc, uidoc, DB, UI

Point = namedtuple('Point', ['X', 'Y','Z'])


tempfile = os.path.join(gettempdir(), 'ViewCrop')
cActiveView = doc.ActiveView
cShpMan = cActiveView.GetCropRegionShapeManager()
cBoundaryList = cShpMan.GetCropShape()
cIterator = cBoundaryList[0].GetCurveLoopIterator()

myCurve = []
myPoints = []

i=0
for cCurve in cIterator:
# print("i={}".format(i))
 cPoint =  cCurve.GetEndPoint(1)
 point = Point(cPoint.X, cPoint.Y, cPoint.Z)
 myPoints.append(point)
 i = i+1
 
with open(tempfile, 'wb') as fp:
 	pickle.dump(myPoints, fp)
fp.close()

msg = 'Saved active view crop boundary of {} points to {}'.format(i,tempfile)
#print(msg)

UI.TaskDialog.Show('pyRevitPlus+', msg)

