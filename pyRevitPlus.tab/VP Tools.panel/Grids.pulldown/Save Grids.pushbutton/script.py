"""
Save Grids

Save the view dependant properties - 
endpoint locations, grid heads and leaders
of the selected building grids for re-use

Non-grid elements will be skipped with dialog,
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

tempfile = os.path.join(gettempdir(), 'GridPlacement')

cView = doc.ActiveView



if cView.ViewType in [DB.ViewType.Section, DB.ViewType.Elevation]:
    experimental = True
    UI.TaskDialog.Show('pyRevitPlus', 'Support for \'{}\' view type is experimental!'.format(cView.ViewType))
    

if cView.ViewType  in [DB.ViewType.FloorPlan, DB.ViewType.CeilingPlan, DB.ViewType.Detail, DB.ViewType.AreaPlan, DB.ViewType.Section, DB.ViewType.Elevation]:
        #UI.TaskDialog.Show('pyRevitPlus', 'View type \'{}\' not supported'.format(cView.ViewType))
        #exit(0)

    selection = rpw.ui.Selection()

    #if len(selection) <> 1:
    #            UI.TaskDialog.Show('pyRevitPlus', 'Select a single grid line!')
    #            exit(0);

    n=0
    GridLines = dict()

    for cGrid in selection:
        el = cGrid.unwrap()
        if isinstance(el, DB.Grid):
            curves=el.GetCurvesInView(DB.DatumExtentType.ViewSpecific, cView)
            if len(curves) <> 1:
                UI.TaskDialog.Show('pyRevitPlus', 'The grid line is defind by {} curves, unable to proceed', len(curves))
            else:
                cGridLine = {'Name':'', 'Start': Point(0,0,0), 'End': Point(0,0,0), 'StartBubble': False, 'StartBubbleVisible': False, 'EndBubble': False, 'EndBubbleVisible': False}
        
                cCurve = curves[0]
            
                leader0 = el.GetLeader(DB.DatumEnds.End0, cView)
                if leader0:
                    tmp = leader0.Elbow
                    cGridLine['Leader0Elbow'] = Point(tmp.X, tmp.Y,tmp.Z)
                    tmp = leader0.End
                    cGridLine['Leader0End'] = Point(tmp.X, tmp.Y,tmp.Z)
                    tmp = leader0.Anchor
                    cGridLine['Leader0Anchor'] = Point(tmp.X, tmp.Y,tmp.Z)
                    
                
                leader1 = el.GetLeader(DB.DatumEnds.End1, cView)
                if leader1:
                    tmp = leader1.Elbow
                    cGridLine['Leader1Elbow'] = Point(tmp.X, tmp.Y,tmp.Z)
                    tmp = leader1.End
                    cGridLine['Leader1End'] = Point(tmp.X, tmp.Y,tmp.Z)
                    tmp = leader1.Anchor
                    cGridLine['Leader1Anchor'] = Point(tmp.X, tmp.Y,tmp.Z)
            
                cGridLine['Name'] = el.Name
            
                tmp = cCurve.GetEndPoint(0)
                cGridLine['Start'] = Point(tmp.X, tmp.Y,tmp.Z)
                tmp = cCurve.GetEndPoint(1)
                cGridLine['End'] = Point(tmp.X, tmp.Y,tmp.Z)
                if el.HasBubbleInView(DB.DatumEnds.End0, cView):
                    cGridLine['StartBubble']=True
                if el.HasBubbleInView(DB.DatumEnds.End1, cView):
                    cGridLine['EndBubble']=True
                if el.IsBubbleVisibleInView(DB.DatumEnds.End0, cView):
                    cGridLine['StartBubbleVisible']=True
                if el.IsBubbleVisibleInView(DB.DatumEnds.End1, cView):
                    cGridLine['EndBubbleVisible']=True
                if isinstance(cCurve, DB.Arc):
                    tmp = cCurve.Center
                    cGridLine['Center'] = Point(tmp.X, tmp.Y,tmp.Z)
                
                GridLines[cGridLine['Name']] = cGridLine
                n += 1
        else:
            if isinstance(el, DB.MultiSegmentGrid):
                UI.TaskDialog.Show('pyRevitPlus', 'Skipping yet unsupported Multi-Segment grid \'{}\''.format(el.Name))
            else: 
                UI.TaskDialog.Show('pyRevitPlus', 'Skipping non- grid element \'{}\''.format(el.Name))
            
    if n<>1:
        msg = 'Saved {} grid placements to {}'.format(n,tempfile)
    else:
        msg = 'Saved gris \'{}\' placement to {}'.format(cGridLine['Name'],tempfile)
     
        
    if n>0:
        with open(tempfile, 'wb') as fp:
            pickle.dump(GridLines, fp)
            # close(fp)
        UI.TaskDialog.Show('pyRevitPlus', msg)
    else:
        UI.TaskDialog.Show('pyRevitPlus', 'Nothing to save')
    
            
else:
    UI.TaskDialog.Show('pyRevitPlus', 'View type \'{}\' not supported'.format(cView.ViewType))
