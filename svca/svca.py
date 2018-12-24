"""Strict Venn Classes with Axes

We use the Strict Venn Class paradigm, but need to extend it to include so that:
1. Each class has a set svc_axes_names, equal to the union of its base classes svc_axes_names
and additional names specified in svc_add_axes_names.
2. A specific type of proper subset (only one SVC base), denoted by boolean
svc_fixed_axes, indicates whether subclasses are defined by having the same
svc_axes_names as the base. This feature allows special case classes for plotting, which
cannot handle extra axes.

To use this module, inherit :class:`svca.Object`. To create a class with fixed axes,
add svc_fixed_axes=True in the bases specification. Other useful functions are
:func:`svca.get_class`, :func:`svca.include_base` and :func:`svca.get_proper_subset`.
"""
import svc

# Mapping of single base class to fixed axes class
fixed_axes_classes={}

class Metaclass(svc.Metaclass):
    def __new__(meta,name,bases,class_dict,svc_fixed_axes=False,svc_add_axes_names=()):
        # Cannot inherit from fixed axes class. To get an intersection of a fixed axes class and another one, inherit
        # from the superclass of the fixed axes class (or equivalent intersection) as well as the other class, and set
        # svc_fixed_axes=True. The fixed axes class will be automatically inherited.
        assert not any(getattr(base,'svc_fixed_axes',False) for base in bases)
        if svc_fixed_axes:
            # Classes with fixed axes are a specific type of proper subset. Get
            # the superset (single base class) first.
            if len(bases)>1:
                bases=(svc.get_intersection(bases),)
            assert bases[0] not in fixed_axes_classes
        class_dict['svc_fixed_axes']=svc_fixed_axes
        class_dict['svc_axes_names']=frozenset.union(frozenset(svc_add_axes_names),*[getattr(base,'svc_axes_names',()) for base in bases])
        # Create class
        cls=svc.Metaclass.__new__(meta,name,bases,class_dict)
        # If a fixed axes subset, add to registry
        if svc_fixed_axes:
            fixed_axes_classes[bases[0]]=cls
        return cls
        
    def __init__(cls,name,bases,class_dict,svc_fixed_axes=False,svc_add_axes_names=()):
        cls=svc.Metaclass.__init__(cls,name,bases,class_dict)

class Object(svc.Universal,metaclass=Metaclass):
    @classmethod
    def is_superset(cls,proper_subsets,class_dict):
        """Is cls a superclass (proper or not) of the class defined by the intersection given proper subsets.

        Args:
            proper_subsets: sequence of proper subset classes
        """
        if cls.svc_fixed_axes and 'svc_axes_names' in class_dict:
            # cls is a fixed axes subset. Therefore it is a superset of the proposed
            # class if the proposed class also has fixed axes AND the two classes
            # have the same axes names AND the (single) base class of cls is a 
            # superset of the intersection of the bases of the proposed class.
            svc_axes_names=class_dict['svc_axes_names']
            assert not cls.is_intersection_class
            return class_dict['svc_fixed_axes'] and cls.svc_axes_names==svc_axes_names and \
                cls.superset.is_superset(proper_subsets,class_dict)
        else:
            return super().is_superset(proper_subsets,class_dict)

def get_class(bases,fixed_axes=False,name=None):
    """Return class defined by tuple of bases and fixed axes specification."""
    if fixed_axes:
        if len(bases)>1:
            base=svc.get_intersection(bases)
        else:
            base=bases[0]
        try:
            return fixed_axes_classes[base]
        except KeyError:
            if name is None:
                name=base.__name__+'FixedAxes'
            return Metaclass(name,bases,{},svc_fixed_axes=True)
    else:
        return svc.get_class(bases,name)
        
def include_base(cls,base):
    """Ensure base is superclass of cls.
    
    If cls is a subclass of base, cls is returned. Otherwise the class with bases
    (base,cls) is returned."""
    if issubclass(cls,base):
        return cls
    else:
        if cls.svc_fixed_axes:
            # Cannot inherit from fixed axes class, so add base to its parent class
            # and create with fixed axes specified
            return get_class((base,cls.superset),fixed_axes=True)
        else:
            return get_class((base,cls))
        
def replace_proper_subset(cls,a,b):
    """Replace proper subset a in bases of cls with b, retaining fixed axes.

    Args:
        cls (type): to be modified
        a (type): proper subset class of which cls is a subclass
        b (type): a is replaced by this
    """
    if cls.svc_fixed_axes:
        proper_subsets=list(cls.superset.intersecting_sets)
    else:
        proper_subsets=list(cls.intersecting_sets)
    ai=proper_subsets.index(a)
    if b is None:
        del proper_subsets[ai]
    else:
        proper_subsets[ai]=b
    return get_class(tuple(proper_subsets),cls.svc_fixed_axes)
        
