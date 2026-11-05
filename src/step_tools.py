"""Load the XIAO ESP32-S3 Sense STEP, keep every solid with its assembly path.
Used by design.py (placement), verify.py (exact booleans) and render.py."""
import functools
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.TDataStd import TDataStd_Name
from OCP.TopLoc import TopLoc_Location
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
import cadquery as cq


def _name(l):
    n = TDataStd_Name()
    return n.Get().ToExtString() if l.FindAttribute(TDataStd_Name.GetID_s(), n) else '?'


@functools.lru_cache(maxsize=2)
def load_step_solids(path):
    """Return list of (assembly_path, cq.Solid) in the STEP's own frame."""
    doc = TDocStd_Document(TCollection_ExtendedString("doc"))
    r = STEPCAFControl_Reader()
    r.SetNameMode(True)
    r.ReadFile(path)
    r.Transfer(doc)
    labels = TDF_LabelSequence()
    XCAFDoc_DocumentTool.ShapeTool_s(doc.Main()).GetFreeShapes(labels)
    out = []

    def walk(l, loc, path):
        if XCAFDoc_ShapeTool.IsReference_s(l):
            ref = TDF_Label()
            XCAFDoc_ShapeTool.GetReferredShape_s(l, ref)
            walk(ref, loc.Multiplied(XCAFDoc_ShapeTool.GetLocation_s(l)), path + [_name(l)])
            return
        if XCAFDoc_ShapeTool.IsAssembly_s(l):
            c = TDF_LabelSequence()
            XCAFDoc_ShapeTool.GetComponents_s(l, c)
            for i in range(1, c.Length() + 1):
                walk(c.Value(i), loc, path)
            return
        sh = XCAFDoc_ShapeTool.GetShape_s(l).Moved(loc)
        ex = TopExp_Explorer(sh, TopAbs_SOLID)
        while ex.More():
            out.append(('/'.join(path), cq.Solid(ex.Current())))
            ex.Next()

    for i in range(1, labels.Length() + 1):
        walk(labels.Value(i), TopLoc_Location(), [])
    return out
