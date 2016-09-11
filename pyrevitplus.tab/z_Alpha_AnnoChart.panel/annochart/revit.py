try:
    # Running From Ribbon
    uidoc = __revit__.ActiveUIDocument
    doc = __revit__.ActiveUIDocument.Document
    ActiveView = uidoc.ActiveView
except NameError:
    # Running Inside Dynamo
    import clr
    clr.AddReference("RevitServices")
    import RevitServices
    from RevitServices.Persistence import DocumentManager
    doc = DocumentManager.Instance.CurrentDBDocument

    uiapp = DocumentManager.Instance.CurrentUIApplication
    uidoc = uiapp.ActiveUIDocument
    ActiveView = uidoc.ActiveView

    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
    import Autodesk
