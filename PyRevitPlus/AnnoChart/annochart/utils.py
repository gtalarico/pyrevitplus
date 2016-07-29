from functools import wraps

from Autodesk.Revit.DB import Transaction, Element

from Autodesk.Revit.DB import FilteredElementCollector
from Autodesk.Revit.DB import FilledRegionType, FilledRegion

from Autodesk.Revit.DB import ViewFamilyType, ViewDrafting, Element
from Autodesk.Revit.DB import ViewFamily

# UNUSED
from Autodesk.Revit.Exceptions import InvalidOperationException
from Autodesk.Revit.UI import TaskDialog

from annochart.revit import doc, uidoc

def revit_transaction(transaction_name):
    def wrap(f):
        @wraps(f)
        def wrapped_f(*args):
            try:
                t = Transaction(doc, transaction_name)
                t.Start()
            except InvalidOperationException as errmsg:
                print('Transaciton Error: {}'.format(errmsg))
                return_value = f(*args)
            else:
                return_value = f(*args)
                t.Commit()
            return return_value
        return wrapped_f
    return wrap

def fregion_id_by_name(name=None):
    """Get Id of Filled Region Type by Name.
    Loops through all types, tries to match name.
    If name not supplied, first type is used.
    If name supplied does not match, last type is used
    """
    f_region_types = FilteredElementCollector(doc).OfClass(FilledRegionType)
    for fregion_type in f_region_types:
        fregion_name = Element.Name.GetValue(fregion_type)
        if not name or name.lower() == fregion_name.lower():
            return fregion_type.Id
    # Loops through all, not found: use last
    else:
        return fregion_type.Id

from Autodesk.Revit.DB import TextAlignFlags
from Autodesk.Revit.DB import XYZ


# @revit_transaction('Create Text')
def create_text(view, text, point):
    baseVec = XYZ.BasisX
    upVec = XYZ.BasisZ
    text_size = 10
    text_length = 0.1

    text_element = doc.Create.NewTextNote(view, point,
        baseVec, upVec, text_length, TextAlignFlags.TEF_ALIGN_RIGHT |
        TextAlignFlags.TEF_ALIGN_MIDDLE, text)
    # text_element.TextNoteType = Bold


@revit_transaction('Create View')
def create_drafting_view(name=None):
    """Create a Drafting View"""
    def get_drafting_type_id():
        """Selects First available ViewType that Matches Drafting Type."""
        view_family_types = FilteredElementCollector(doc).OfClass(ViewFamilyType)
        for i in view_family_types:
            if i.ViewFamily == ViewFamily.Drafting:
                return i.Id

    drafting_type_id = get_drafting_type_id()
    drafting_view = ViewDrafting.Create(doc, drafting_type_id)
    if name is not None:
        drafting_view.Name = name
    return drafting_view
