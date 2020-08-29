"""
Save Levels

Save the view dependant properties - 
endpoint locations, level heads and leaders
of the selected building levels for re-use

Non-level elements will be skipped with dialog,
 so it's advisable to apply filtering beforehead

TESTED REVIT API: 2020

@ejs-ejs
This script is part of PyRevitPlus: Extensions for PyRevit
github.com/ejs-ejs | @ejs-ejs

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

Axis = namedtuple('Axis', ['Name', 'Start', 'End','StartBubble', 'EndBubble', 'StartBubbleVisible', 'EndBubbleVisible'])

tempfile = os.path.join(gettempdir(), 'LevelPlacement')

cView = doc.ActiveView



if not(cView.ViewType == DB.ViewType.Section or cView == DB.ViewType.Elevation):
    UI.TaskDialog.Show('pyRevitPlus', 'View type \'{}\' not supported'.format(cView.ViewType))
    
else:
    experimental = True
    UI.TaskDialog.Show('pyRevitPlus', 'Support for \'{}\' view type is experimental!'.format(cView.ViewType))
        
        
    selection = rpw.ui.Selection()

#if len(selection) <> 1:
#            UI.TaskDialog.Show('pyRevitPlus', 'Select a single grid line!')
#            exit(0);

    n=0
    LevelLines = dict()

    for cLevel in selection:
        el = cLevel.unwrap()
        if isinstance(el, DB.Level):
            curves=el.GetCurvesInView(DB.DatumExtentType.ViewSpecific, cView)
            if len(curves) <> 1:
                UI.TaskDialog.Show('pyRevitPlus', 'The level line is defind by {} curves, unable to proceed', len(curves))
            else:
                cLevelLine = {'Name':'', 'Start': Point(0,0,0), 'End': Point(0,0,0), 'StartBubble': False, 'StartBubbleVisible': False, 'EndBubble': False, 'EndBubbleVisible': False}
        
                cCurve = curves[0]
            
                leader0 = el.GetLeader(DB.DatumEnds.End0, cView)
                if leader0:
                    tmp = leader0.Elbow
                    cLevelLine['Leader0Elbow'] = Point(tmp.X, tmp.Y,tmp.Z)
                    tmp = leader0.End
                    cLevelLine['Leader0End'] = Point(tmp.X, tmp.Y,tmp.Z)
                    tmp = leader0.Anchor
                    cLevelLine['Leader0Anchor'] = Point(tmp.X, tmp.Y,tmp.Z)
                
            
                leader1 = el.GetLeader(DB.DatumEnds.End1, cView)
                if leader1:
                    tmp = leader1.Elbow
                    cLevelLine['Leader1Elbow'] = Point(tmp.X, tmp.Y,tmp.Z)
                    tmp = leader1.End
                    cLevelLine['Leader1End'] = Point(tmp.X, tmp.Y,tmp.Z)
                    tmp = leader1.Anchor
                    cLevelLine['Leader1Anchor'] = Point(tmp.X, tmp.Y,tmp.Z)
        
                cLevelLine['Name'] = el.Name
        
                tmp = cCurve.GetEndPoint(0)
                cLevelLine['Start'] = Point(tmp.X, tmp.Y,tmp.Z)
                tmp = cCurve.GetEndPoint(1)
                cLevelLine['End'] = Point(tmp.X, tmp.Y,tmp.Z)
                if el.HasBubbleInView(DB.DatumEnds.End0, cView):
                    cLevelLine['StartBubble']=True
                if el.HasBubbleInView(DB.DatumEnds.End1, cView):
                    cLevelLine['EndBubble']=True
                if el.IsBubbleVisibleInView(DB.DatumEnds.End0, cView):
                    cLevelLine['StartBubbleVisible']=True
                if el.IsBubbleVisibleInView(DB.DatumEnds.End1, cView):
                    cLevelLine['EndBubbleVisible']=True
                #if isinstance(cCurve, DB.Arc):
                #    tmp = cCurve.Center
                #    cLevelLine['Center'] = Point(tmp.X, tmp.Y,tmp.Z)
            
                LevelLines[cLevelLine['Name']] = cLevelLine
                n += 1
        else:
            #if isinstance(el, DB.MultiSegmentGrid):
            #    UI.TaskDialog.Show('pyRevitPlus', 'Skipping yet unsupported Multi-Segment grid \'{}\''.format(el.Name))
            #else: 
            UI.TaskDialog.Show('pyRevitPlus', 'Skipping non- level element \'{}\''.format(el.Name))
        
    if n<>1:
        msg = 'Saved {} level placements to {}'.format(n,tempfile)
    else:
        msg = 'Saved level \'{}\' placement to {}'.format(cLevelLine['Name'],tempfile)
 
    if n>0:
        with open(tempfile, 'wb') as fp:
            pickle.dump(LevelLines, fp)
        # close(fp)
        UI.TaskDialog.Show('pyRevitPlus', msg)
    else:
        UI.TaskDialog.Show('pyRevitPlus', 'Nothing to save')
