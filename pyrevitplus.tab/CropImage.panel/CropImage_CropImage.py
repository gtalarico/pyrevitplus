"""
Crop Image
Create Plans from Selected Rooms
TESTED REVIT API: 2015

Copyright (c) 2014-2016 Gui Talarico
github.com/gtalarico | gtalarico@gmail.com

This script is part of PyRevitPlus: Extensions for PyRevit
github.com/gtalarico | gtalarico@gmail.com

--------------------------------------------------------
PyRevit Notice:
Copyright (c) 2014-2016 Ehsan Iran-Nejad
pyRevit: repository at https://github.com/eirannejad/pyRevit

"""

__author__ = 'gtalarico@gmail.com'

import sys
import os
import logging
from functools import wraps
from collections import namedtuple
from random import randint

from Autodesk.Revit.UI import TaskDialog
from Autodesk.Revit.DB import XYZ, BoundingBoxXYZ
from Autodesk.Revit.DB import ImageView, ImageType, ImageImportOptions, BoxPlacement
from Autodesk.Revit.DB import Element, ElementId, BuiltInParameter
from Autodesk.Revit.DB import Transaction, FilledRegion

import clr
clr.AddReference('System')
clr.AddReference('System.IO')
clr.AddReference('System.Drawing')
clr.AddReference("System.Windows.Forms")

#  Windows Forms Elements
from System.Drawing.Graphics import DrawImage
from System.Drawing import GraphicsUnit, Graphics
from System.Drawing import Image, Rectangle, Bitmap
from System.Drawing.Imaging import ImageFormat
from System.Drawing import Point, Icon, Color, Size
from System import IO

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

VERBOSE = True  # True to Keep Window Open
VERBOSE = False

LOG_LEVEL = logging.ERROR
LOG_LEVEL = logging.INFO
if VERBOSE:
    LOG_LEVEL = logging.DEBUG
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger('Crop Image')

def get_selected_elements():
    """ Add Doc """
    selection = uidoc.Selection
    selection_ids = selection.GetElementIds()
    selection_size = selection_ids.Count
    logger.debug('selection_size: {}'.format(selection_size))
    # selection = uidoc.Selection.Elements  # Revit 2015
    if not selection_ids:
        TaskDialog.Show('MakePlans', 'No Elements Selected.')
        # logger.error('No Elements Selected')
        __window__.Close()
        sys.exit(0)
    elements = []
    for element_id in selection_ids:
        elements.append(doc.GetElement(element_id))
    return elements

class BoundingBoxElement(object):
    """ BoundingBoxElement receives a Revit Object for access to properties.
    Usage:
    bbox = BoundingBoxElement(element)
    bbox.element: element
    Properties:
    bbox.min: min coordinate of bounding box
    bbox.max: min coordinate of bounding box
    bbox.average: min coordinate of bounding box

    """

    def __init__(self, element):
        self.element = element
        self.bbox = element.get_BoundingBox(doc.ActiveView)

    @property
    def min(self):
        x, y, z = self.bbox.Min.X, self.bbox.Min.Y, self.bbox.Min.Z
        return XYZ(x, y, z)

    @property
    def max(self):
        x, y, z = self.bbox.Max.X, self.bbox.Max.Y, self.bbox.Max.Z
        return XYZ(x, y, z)

    @property
    def center(self):
        x = (self.min.X + self.max.X) / 2
        y = (self.min.Y + self.max.Y) / 2
        return XYZ(x, y, 0)

    def __str__(self):
        return repr(self)

def revit_transaction(transaction_name):
    def wrap(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            try:
                t = Transaction(doc, transaction_name)
                t.Start()
            except InvalidOperationException as errmsg:
                print('Transaciton Error: {}'.format(errmsg))
                return_value = f(*args, **kwargs)
            else:
                return_value = f(*args, **kwargs)
                t.Commit()
            return return_value
        return wrapped_f
    return wrap

def crop_image(bmp_source, rectangle):
    # An empty bitmap which will hold the cropped image
    bmp = Bitmap(rectangle.Width, rectangle.Height)
    print('Rectangle will be: {} X {}'.format(rectangle.Width, rectangle.Height))
    # bmp = Bitmap(rectangle.Width, rectangle.Height)
    g = Graphics.FromImage(bmp)
    #  // Draw the given area (rectangle) of the source image
    #  // at location 0,0 on the empty bitmap (bmp)
    g.DrawImage(source, 0, 0, rectangle, GraphicsUnit.Pixel)
    return bmp

def create_img_copy(img_path):
    """ Creates a Copy of an image in the same folder"""
    split_path = img_path.split('.')
    extension = split_path.pop(-1)
    full_path = ''.join(split_path) # Rejoins in case there are other dots
    rnd = randint(0,1000)
    new_img_path = '{}_cropped{}.{}'.format(full_path, rnd, extension)

    try:
        IO.File.Copy(img_path, new_img_path)
    except Exception as errmsg:
        print('Cropped copy already exists')
    return new_img_path

__window__.Close()

img_element, fregion = None, None

elements = get_selected_elements()

for element in elements:

    if isinstance(element, FilledRegion):
        fregion = element
        fregion_bbox = BoundingBoxElement(fregion)
        continue

    for valid_type_id in element.GetValidTypes():
        valid_type = doc.GetElement(valid_type_id)

        if isinstance(valid_type, ImageType):
            img_element = element
            img_type = valid_type

            bip_filename = BuiltInParameter.RASTER_SYMBOL_FILENAME
            bip_pxl_height = BuiltInParameter.RASTER_SYMBOL_PIXELHEIGHT
            bip_pxl_width = BuiltInParameter.RASTER_SYMBOL_PIXELWIDTH
            bip_resolution = BuiltInParameter.RASTER_SYMBOL_RESOLUTION

            # Type Parameters
            img_path = img_type.get_Parameter(bip_filename).AsString()
            img_pxl_width = img_type.get_Parameter(bip_pxl_width).AsInteger()
            img_pxl_height = img_type.get_Parameter(bip_pxl_height).AsInteger()
            img_resolution = img_type.get_Parameter(bip_resolution).AsInteger()

            # Instance Parameters
            img_width = img_element.LookupParameter('Width').AsDouble()
            img_height = img_element.LookupParameter('Height').AsDouble()
            img_bbox = BoundingBoxElement(img_element)

            bip_scale = BuiltInParameter.RASTER_VERTICAL_SCALE
            img_scale = img_element.get_Parameter(bip_scale).AsDouble()

            break

if not img_element or not fregion:
    print('Need a filled region and image selected.')
else:
    x_ft_to_px_scale = img_pxl_width / img_width
    y_ft_to_px_scale = img_pxl_height / img_height

    crop_height = fregion_bbox.max.Y - fregion_bbox.min.Y
    crop_width = fregion_bbox.max.X - fregion_bbox.min.X
    lw_left_crop_pt = fregion_bbox.min - img_bbox.min
    up_left_crop_pt = lw_left_crop_pt + XYZ(0, crop_height, 0)

    origin_x = up_left_crop_pt.X
    origin_y = img_height - up_left_crop_pt.Y

    origin_x = origin_x * x_ft_to_px_scale
    origin_y = origin_y * y_ft_to_px_scale
    width = crop_width * x_ft_to_px_scale
    height = crop_height * y_ft_to_px_scale


    new_img_path = create_img_copy(img_path)
    source = Bitmap(img_path)
    rectangle = Rectangle(origin_x, origin_y, width, height)
    cropped_img = crop_image(source, rectangle)
    cropped_img.Save(new_img_path)

    # New Image Options
    options = ImageImportOptions()
    options.Placement = BoxPlacement.Center
    options.RefPoint = fregion_bbox.center
    options.Resolution = img_resolution

    t = Transaction(doc, 'Crop Image')
    t.Start()
    new_img = clr.StrongBox[Element]()
    view = doc.ActiveView
    doc.Import(new_img_path, options , view, new_img)
    new_width = new_img.LookupParameter('Width')
    new_width.Set(crop_width)
    t.Commit()


    print('Img Width: ', img_width)
    print('Img Height: ', img_height)
    print('Img Pxl Width: ', img_pxl_width)
    print('Img Pxl Height: ', img_pxl_height)
    print('Img Resolution: ', img_resolution)

    print('Upper_left Crop Pt: [{},{}]'.format(up_left_crop_pt.X, up_left_crop_pt.Y))
    print('Lower Left Crop Pt: [{},{}]'.format(lw_left_crop_pt.X, lw_left_crop_pt.Y))
    print('Crop Width: ', crop_width)
    print('Crop Height: ', crop_height)

    print('SCALE X: ', x_ft_to_px_scale)
    print('SCALE Y: ', y_ft_to_px_scale)
    print('IMG SCALE: ', img_scale)

    print('SCALED: Upper_left Crop Pt: [{},{}]'.format((up_left_crop_pt * x_ft_to_px_scale).X, (up_left_crop_pt * x_ft_to_px_scale).Y))
    print('SCALED: Lower Crop Pt: [{},{}]'.format((lw_left_crop_pt * x_ft_to_px_scale).X, (lw_left_crop_pt * x_ft_to_px_scale).Y))
    print('SCALED: Crop Width: ', crop_width * x_ft_to_px_scale)
    print('SCALED: Crop Height: ', crop_height * y_ft_to_px_scale)
