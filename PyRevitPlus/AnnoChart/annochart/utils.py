from functools import wraps
import logging

# Revit Globals
from annochart.revit import doc, uidoc

from Autodesk.Revit.DB import Transaction, Element
from Autodesk.Revit.DB import FilteredElementCollector
from Autodesk.Revit.Exceptions import InvalidOperationException
from Autodesk.Revit.DB import XYZ
from Autodesk.Revit.UI import TaskDialog

#  Filled Regions
from Autodesk.Revit.DB import FilledRegionType, FilledRegion

#  Drafting Views
from Autodesk.Revit.DB import ViewFamilyType, ViewDrafting, Element
from Autodesk.Revit.DB import ViewFamily

# Text
from Autodesk.Revit.DB import TextAlignFlags

VERBOSE = True
LOG_LEVEL = logging.INFO
if VERBOSE:
    LOG_LEVEL = logging.DEBUG
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger('AnnoChart')


def dialog(msg, title='AnnoChart'):
    TaskDialog.Show(title, msg)


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
        logger.debug('Color not specified or not found.')
        return fregion_type.Id


# @revit_transaction('Create Text') - Transaction Already Started on Chart
def create_text(view, text, point, align):
    """Creates a Revit Text.
    create_test(view, text_string, point)
    TODO: Add Justification as option
    """
    baseVec = XYZ.BasisX
    upVec = XYZ.BasisZ
    text_size = 10
    text_length = 0.5
    text = str(text)

    align_options = {'left': TextAlignFlags.TEF_ALIGN_LEFT |
                             TextAlignFlags.TEF_ALIGN_MIDDLE,
                     'right': TextAlignFlags.TEF_ALIGN_RIGHT |
                             TextAlignFlags.TEF_ALIGN_MIDDLE
                     }

    text_element = doc.Create.NewTextNote(view, point, baseVec, upVec,
                                          text_length,
                                          align_options[align],
                                          text)
    # text_element.TextNoteType = Bold


@revit_transaction('Create View')
def create_drafting_view(name=None):
    """Create a Drafting View"""
    def get_drafting_type_id():
        """Selects First available ViewType that Matches Drafting Type."""
        viewfamily_types = FilteredElementCollector(doc).OfClass(ViewFamilyType)
        for i in viewfamily_types:
            if i.ViewFamily == ViewFamily.Drafting:
                return i.Id

    drafting_type_id = get_drafting_type_id()
    drafting_view = ViewDrafting.Create(doc, drafting_type_id)
    if name is not None:
        drafting_view.Name = name
    return drafting_view
