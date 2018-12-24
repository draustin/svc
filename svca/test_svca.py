import svc
from svca import *

def test_svca():
    class XDep(Object,svc_add_axes_names=('x',)):
        pass

    class YDep(Object,svc_add_axes_names=('y',)):
        pass

    class XYDep(XDep,YDep):
        pass

    class XYDepOnly(XDep,YDep,svc_fixed_axes=True):
        pass
    assert issubclass(XYDepOnly,XYDep)

    class ZDep(Object,svc_add_axes_names=('z',)):
        pass

    class Feature(Object):
        pass

    class XYZDep(XDep,YDep,ZDep):
        pass

    class XYDepFeature(XDep,YDep,Feature):
        pass

    class WDep(Object,svc_add_axes_names=('w',)):
        pass

    class XDepOnly(XDep,svc_fixed_axes=True):
        pass

    class XDepS(XDep):
        pass

    class XDepSS(XDepS):
        pass

    assert issubclass(get_class((XDepSS,),fixed_axes=True),XDepOnly)

    svc.get_intersection((XDep,YDep))
    XWDep=svc.get_intersection((XDep,WDep))
    assert XWDep is svc.get_intersection((XDep,WDep))
    assert XWDep.svc_axes_names==frozenset(('x','w'))

    XYWDep=svc.get_intersection((XDep,YDep,WDep))
    assert issubclass(XYWDep,XYDep)
    assert not issubclass(XYWDep,XYDepOnly)

    T=get_class((XDep,YDep),fixed_axes=True)
    assert T is XYDepOnly

    assert get_class((XDep,YDep))==XYDep

    assert issubclass(get_class((XDep,YDep,Feature),fixed_axes=True),XYDepOnly)

    assert replace_proper_subset(XYDep,YDep,None)==XDep

    assert replace_proper_subset(XYDepOnly,YDep,None)==XDepOnly

    assert replace_proper_subset(get_class([XDep,YDep,ZDep],fixed_axes=True),ZDep,None)==XYDepOnly
    assert issubclass(replace_proper_subset(get_class([XDep,YDep,ZDep],fixed_axes=True),ZDep,Feature),XYDepOnly)
