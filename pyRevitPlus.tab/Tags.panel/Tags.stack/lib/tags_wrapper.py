import os
from collections import namedtuple

from pyrevit import revit, DB, forms, script

import rpw
from rpw import doc, uidoc, DB, UI

logger = script.get_logger()
output = script.get_output()

# shortcut for DB.BuiltInCategory
BIC = DB.BuiltInCategory


def toggle_element_selection_handles(target_view, bicat, state=True):
    """Toggle handles for spatial elements"""
    with revit.Transaction("Toggle handles"):
        # if view has template, toggle temp VG overrides
        if state:
            target_view.EnableTemporaryViewPropertiesMode(target_view.Id)

        rr_cat = revit.query.get_subcategory(bicat, 'Reference')
        try:
            rr_cat.Visible[target_view] = state
        except Exception as vex:
            logger.debug(
                'Failed changing category visibility for \"%s\" '
                'to \"%s\" on view \"%s\" | %s',
                bicat,
                state,
                target_view.Name,
                str(vex)
                )
        rr_int = revit.query.get_subcategory(bicat, 'Interior Fill')
        if not rr_int:
            rr_int = revit.query.get_subcategory(bicat, 'Interior')
        try:
            rr_int.Visible[target_view] = state
        except Exception as vex:
            logger.debug(
                'Failed changing interior fill visibility for \"%s\" '
                'to \"%s\" on view \"%s\" | %s',
                bicat,
                state,
                target_view.Name,
                str(vex)
                )
        # disable the temp VG overrides after making changes to categories
        if not state:
            target_view.DisableTemporaryViewMode(
                DB.TemporaryViewMode.TemporaryViewProperties)
                
class EasilySelectableElements(object):
    """Toggle spatial element handles for easy selection."""
    def __init__(self, target_view, bicat):
        self.supported_categories = [
            BIC.OST_Tags
            ]
        self.target_view = target_view
        self.bicat = bicat

    def __enter__(self):
        if self.bicat in self.supported_categories:
            toggle_element_selection_handles(
                self.target_view,
                self.bicat
                )
        return self

    def __exit__(self, exception, exception_value, traceback):
        if self.bicat in self.supported_categories:
            toggle_element_selection_handles(
                self.target_view,
                self.bicat,
                state=False
                )

def match_orientation(tagType, starting_or):
    # all actions under one transaction
    with revit.TransactionGroup("Match tag orientation"):
        # make sure target elements are easily selectable
#        with EasilySelectableElements(revit.active_view, BIC.OST_Tags):
            
        # ask user to pick a tag and allign them
        for picked_element in revit.get_picked_elements_by_category(
                revit.query.get_category(tagType),
                message="Select a tag to match"):
            # need nested transactions to push revit to update view
            # on each allignment
            with revit.Transaction("Setting tag \'{}\' orientation".format(picked_element.Id)):
                picked_element.TagOrientation = starting_or



def allign_X(tagType, starting_pt):
    # all actions under one transaction
    with revit.TransactionGroup("Allign tags vertically"):
        # make sure target elements are easily selectable
#        with EasilySelectableElements(revit.active_view, BIC.OST_Tags):
            
        # ask user to pick a tag and allign them
        for picked_element in revit.get_picked_elements_by_category(
                revit.query.get_category(tagType),
                message="Select a tag to allign"):
            # need nested transactions to push revit to update view
            # on each allignment
            with revit.Transaction("Allign tag \'{}\' by X".format(picked_element.Id)):
                # actual allignment
                cPosition = picked_element.TagHeadPosition
                picked_element.TagHeadPosition = DB.XYZ(starting_pt.X, cPosition.Y, cPosition.Z)


def allign_Y(tagType, starting_pt):
    """Main renumbering routine for elements of given category."""
    # all actions under one transaction
    with revit.TransactionGroup("Allign tags horizontally"):
        # make sure target elements are easily selectable
#        with EasilySelectableElements(revit.active_view, BIC.OST_Tags):
            
        # ask user to pick a tag and allign them
        for picked_element in revit.get_picked_elements_by_category(
                revit.query.get_category(tagType),
                message="Select a tag to allign"):
            # need nested transactions to push revit to update view
            # on each allignment
            with revit.Transaction("Allign tag \'{}\' by Y".format(picked_element.Id)):
                # actual allignment
                cPosition = picked_element.TagHeadPosition
                picked_element.TagHeadPosition = DB.XYZ(cPosition.X, starting_pt.Y, cPosition.Z)
                
def allign_XY(tagType, starting_pt):
    """Main renumbering routine for elements of given category."""
    # all actions under one transaction
    with revit.TransactionGroup("Allign tags vertically in section / elevation"):
        # make sure target elements are easily selectable
#        with EasilySelectableElements(revit.active_view, BIC.OST_Tags):
            
        # ask user to pick a tag and allign them
        for picked_element in revit.get_picked_elements_by_category(
                revit.query.get_category(tagType),
                message="Select a tag to allign"):
            # need nested transactions to push revit to update view
            # on each allignment
            with revit.Transaction("Allign tag \'{}\' by XY".format(picked_element.Id)):
                # actual allignment
                cPosition = picked_element.TagHeadPosition
                picked_element.TagHeadPosition = DB.XYZ(starting_pt.X, starting_pt.Y, cPosition.Z)
                
def allign_Z(tagType, starting_pt):
    """Main renumbering routine for elements of given category."""
    # all actions under one transaction
    with revit.TransactionGroup("Allign tags horizontally"):
        # make sure target elements are easily selectable
#        with EasilySelectableElements(revit.active_view, BIC.OST_Tags):
            
        # ask user to pick a tag and allign them
        for picked_element in revit.get_picked_elements_by_category(
                revit.query.get_category(tagType),
                message="Select a tag to allign"):
            # need nested transactions to push revit to update view
            # on each allignment
            with revit.Transaction("Allign tag \'{}\' by Z".format(picked_element.Id)):
                # actual allignment
                cPosition = picked_element.TagHeadPosition
                picked_element.TagHeadPosition = DB.XYZ(cPosition.X, cPosition.Y, starting_pt.Z)
