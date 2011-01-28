from math import sqrt

def get_scale(gc):
    """  Get the scaling from the ctm.
    """
    ctm = gc.get_ctm()
    if hasattr(ctm, "__len__") and len(ctm) == 6:
        return sqrt( (ctm[0]+ctm[1]) * (ctm[0]+ctm[1]) / 2.0 + \
                     (ctm[2]+ctm[3]) * (ctm[2]+ctm[3]) / 2.0 )

    if hasattr(ctm, "scale"):
        return gc.get_ctm().scale()

    if hasattr(gc, "get_ctm_scale"):
        return gc.get_ctm_scale()

    raise RuntimeError("Unable to get scale from GC.")

