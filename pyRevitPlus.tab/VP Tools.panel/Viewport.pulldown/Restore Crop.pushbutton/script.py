"""
Restore ViewPort Crop
Restore the saved crop boundary to a Viewport


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
from rpw import doc, uidoc
from Autodesk.Revit import DB
from Autodesk.Revit import UI
#import math

Point = namedtuple('Point', ['X', 'Y','Z'])
ptArray = []

tempfile = os.path.join(gettempdir(), 'ViewCrop')

try:
    with open(tempfile, 'rb') as fp:
    #myPoints = []
    	myPoints = pickle.load(fp)
    	fp.close()
except IOError:
    UI.TaskDialog.Show('pyRevitPlus-', 'Could not find saved viewport crop boundary.\nSave a Viewport Crop first.')
    sys.exit()
else:    
   #pprint(myPoints)
    for cPoint in myPoints:
    	saved_pt = DB.XYZ(cPoint.X, cPoint.Y, cPoint.Z)
    	ptArray.append(saved_pt)
#
#print('pyRevitPlus: Proceeding to view')
cActiveView = doc.ActiveView
cShpMan = cActiveView.GetCropRegionShapeManager()
cBoundaryList = cShpMan.GetCropShape()

if (ptArray.Count> 4) and not(cShpMan.CanHaveShape):
	UI.TaskDialog.Show('pyRevitPlus-', 'Unable to set non=rectangular crop to the viewport.')
else:	
	newBoundaryList = DB.CurveLoop()
	#print('pyRevitPlus: Creating new boundary')
	for idx, value in enumerate(ptArray):
		pt0 = ptArray[idx-1]
		pt1 = ptArray[idx]
		#print("Curve {}: Start {}, curve end {}, distance {}".format(idx, pt0, pt1, math.sqrt( ((pt1[0]-pt0[0])**2)+((pt1[1]-pt0[1])**2) )))
		cLine = DB.Line.CreateBound(pt0, pt1)
		newBoundaryList.Append(cLine)
	#print('pyRevitPlus: Updating boundary')
	t = DB.Transaction(doc, 'Paste Viewport Clipping')
	t.Start()
	#	print('pyRevitPlus: In transaction')
	cActiveView.CropBoxVisible = True
	cActiveView.CropBoxActive =True
		
	if cShpMan.IsCropRegionShapeValid(newBoundaryList):
		try:
			cShpMan.RemoveCropRegionShape()
			cShpMan.SetCropShape(newBoundaryList)
		except InvalidOperationException:
			print('The crop of the associated view is not permitted to have a non-rectangular shape.')
		except ArgumentException :
			print('Boundary in boundary should represent one closed curve loop without self-intersections, consisting of non-zero length straight lines in a plane parallel to the view plane. ')
	doc.Regenerate()
	t.Commit()
	#print('pyRevitPlus: regenerating')
		
	#cActiveView1 = doc.ActiveView
	#cShpMan1 = cActiveView1.GetCropRegionShapeManager()
	#cBoundaryList1 = cShpMan1.GetCropShape()
	#cIterator1 = cBoundaryList1[0].GetCurveLoopIterator()
	#for idx1, cCurve1 in enumerate(cIterator1):
		# print("i={}".format(i))
 	#	cPoint =  cCurve1.GetEndPoint(1)
 	#	print(' Current point {}: [{}, {}, {}]'.format(idx1, cPoint.X, cPoint.Y, cPoint.Z))
 
	

#msg = 'Loaded saved view crop boundary of {} points to {}'.format(ptArray.Count,tempfile)
#print(msg)
#UI.TaskDialog.Show('pyRevitPlus+', msg)

