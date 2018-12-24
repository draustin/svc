"""Strict Venn classes

Introduction

Imagine a set of classes representing calculation or simulation of some sort. Let 
class X incorporate dependence of the calculation on some parameter x. For example,
X might have methods for plotting results versus x. Let V and W be classes representing
different types of calculations. We might define subclasses VX and WX with specific
methods for dealing with a dependence on X of a V or W respectively. Now imagine
we have some generic code for converting a simulation represented by class C
from a V to a W, regardless of additional
parameters such as x. We need some generic way of saying "replace V with W in the
bases of C". Strict Venn classes is a way of dealing this this problem.

In SVC, relationships between classes are precisely analogous to set theory. There
is a one-to-one mapping between classes and sets. Classes are declared in one of
two ways:
1. as the intersection of two or more existing classes
2. as a proper subset of a single existing class
The class Universal is a superset of all classes and is a superclass of all strict
Venn classes.
"""
import itertools
from toposort import toposort
from decorators import classproperty

# We want an ordering of classes that is consistent with inheritance (subclasses first) and deterministic (doesn't depend
# on creation order). We use topological sorting.
# Input to toposort: mapping of classes to set of bases
gmro_bases={}
# Global method resolution order derived from bases using toposort. Updated whenever a class is created.
gmro=[]
# Mapping of tuple of proper subsets to intersection classes
intersection_classes={}

def compare_orderings(a,b):
    """a and b are two orderings (lists which each item appearing once)"""
    e_prev=None
    ib_prev=-1
    for ia,e in enumerate(a):
        if e not in b:
            # Element not in b, so ignore it
            continue
        ib=b.index(e)
        if ib<=ib_prev:
            return e,ia,ib,e_prev,ia_prev,ib_prev
        e_prev=e
        ia_prev=ia
        ib_prev=ib
    return None

def update_gmro():
    """Update the GMRO based on the subclass list."""
    global gmro
    # List of classes sorted by inheritance, then by concatenation of module name and name.
    gmro=list(itertools.chain.from_iterable(sorted(classes,key=lambda cls:cls.__module__+cls.__name__)[::-1] for classes in toposort(gmro_bases)))[::-1]

def is_intersection_superset(s1,s2):
    """Is (intersection of all in s1) a superset of (intersection of all in s2).

    The superset may be proper or improper.
    """
    return all(any(issubclass(e2,e1) for e2 in s2) for e1 in s1)

def ispropersubclass(a,b):
    return a is not b and issubclass(a,b)

class Metaclass(type):
    def __new__(meta,name,bases,class_dict):
        if len(bases)==0:
            # Creating Universal
            cls=type.__new__(meta,name,bases,class_dict)
        else:
            other_bases=tuple(base for base in bases if not issubclass(base,Universal))
            bases=tuple(base for base in bases if issubclass(base,Universal))
            if len(bases)==1:
                # Creating a proper subset
                proper_subsets=(bases[0],)
            else:
                # Intersection class requested
                # No-redundancy set of proper_subsets whose intersection defines the class to be created
                proper_subsets=get_proper_subsets(bases)
                # Class shouldn't exist
                assert proper_subsets not in intersection_classes,proper_subsets
            # All existing superclasses (proper or improper)
            superclasses=set(cls for cls in gmro if cls.is_superset(proper_subsets,class_dict))
            # Order consistent with GMRO
            bases=tuple(cls for cls in gmro if cls in superclasses)
            # Create class
            cls=type.__new__(meta,name,bases+other_bases,class_dict)
            if len(proper_subsets)==1:
                # Proper subset class
                cls.superset=proper_subsets[0]
                cls.intersecting_sets=None
            else:
                # Intersction class - store its intersection
                cls.intersecting_sets=proper_subsets
                cls.superset=None
                # Register
                intersection_classes[proper_subsets]=cls
        # Register bases of cls.
        gmro_bases[cls]=set(bases)
        # Since gmro_bases has changed, need to update the GMRO.
        update_gmro()
        return cls

def get_proper_subsets(bases):
    """Get minimal tuple of proper subsets of class with given bases consistent with GMRO.

    The tuple is minimal i.e. has no redundant supersets."""
    # Collect all proper subsets.
    all_proper_subsets=set.union(*[set(base.defining_sets) for base in bases])
    # Make minimal set by rejecting redundant proper_subsets.
    proper_subsets=set()
    for candidate in all_proper_subsets:
        # If candidate proper_subset is a superclass of any other proper_subset (except itself), then reject it.
        if any(issubclass(proper_subset,candidate) for proper_subset in all_proper_subsets if
               candidate is not proper_subset):
            continue
        proper_subsets.add(candidate)
    # Sort according to position in GMRO
    proper_subsets=tuple(cls for cls in gmro if cls in proper_subsets)
    return proper_subsets

def get_intersection(bases,default_name=None):
    """Get intersection class given sequence of bases."""
    assert len(bases)>1
    proper_subsets=get_proper_subsets(bases)
    try:
        # Lookup existing intersections
        cls=intersection_classes[proper_subsets]
    except KeyError:
        # Create class
        if default_name is None:
            default_name=''.join(base.__name__ for base in bases)
        cls=type(default_name,bases,{})
    return cls

def remove_supersets(bases):
    return tuple(candidate for candidate in bases if not any(ispropersubclass(cls,candidate) for cls in bases))

def get_class(bases,default_name=None):
    """If only one base, return it, otherwise return intersection."""
    bases=remove_supersets(bases)
    if len(bases)>1:
        return get_intersection(bases,default_name)
    else:
        return bases[0]
    
def replace_proper_subset(cls,a,b):
    """Replace proper subset a in definition of cls with b."""
    proper_subsets=list(cls.intersecting_sets)
    ai=proper_subsets.index(a)
    if b is None:
        del proper_subsets[ai]
    else:
        proper_subsets[ai]=b
    return get_class(proper_subsets)
    
class Universal(metaclass=Metaclass):
    @classproperty
    def defining_sets(cls):
        if cls is Universal:
            return ()
        elif cls.is_intersection_class:
            return cls.intersecting_sets
        else:
            return (cls,)

    @classproperty
    def is_intersection_class(cls):
        return cls.intersecting_sets is not None

    @classmethod
    def is_superset(cls,proper_subsets,class_dict):
        """Is cls a superclass (proper or not) of the class defined by the intersection given proper subsets.

        Args:
            proper_subsets: sequence of proper subset classes
        """
        return is_intersection_superset(cls.defining_sets,proper_subsets)

    # @classmethod
    # def get_proper_subsets(cls):
    #     """For an intersection class, returns a tuple of proper subset classes whose
    #     intersection defines the class. For a proper subset, returns a tuple containing
    #     cls. A tuple is returned so the result can be used as a key (hashable).
    #     """
    #     # Remove bases that aren't subclasses of Universal (i.e. ignore them)
    #     if len(cls.svc_bases)==0:
    #         # No SVC bases explicitly listed so cls is Universal
    #         return ()
    #     elif len(cls.svc_bases)==1:
    #         # One SVC base, so is proper subset class
    #         return (cls,)
    #     else:
    #         # More than one SVC base, so is intersection class. Get minimal (no supersets) set of proper_subset classes
    #         # that define cls.
    #         proper_subsets=get_proper_subsets(cls.svc_bases)
    #         # Sort these according to their position in the mro
    #         return tuple(x for x in cls.mro() if x in proper_subsets)
    #
    # @classmethod
    # def get_svc_superclasses(cls):
    #     return set.union(set((cls,)),*[base.svc_superclasses for base in cls.__bases__ if issubclass(base,Universal) and base is not Universal])

