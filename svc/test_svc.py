from svc import *

def test_compare_orderings():
    assert compare_orderings([1,2],[1,3])==None
    assert compare_orderings([1,2],[2,1])==(2,1,0,1,0,1)
    assert compare_orderings([1,2,3,5],[1,3,5])==None
    assert compare_orderings([1,2,3,5],[1,5,3])==(5,3,1,3,2,2)

def test_ABC():
    class A(Universal):
        pass

    class B(Universal):
        pass

    class C(Universal):
        pass

    class AB(A,B):
        pass

    class ABO(AB):
        pass

    class BC(B,C):
        pass

    class AC(A,C):
        pass

    class ABC(AB,AC):
        pass

    assert issubclass(ABC,BC)
    assert issubclass(ABO,AB)
    assert not issubclass(ABC,ABO)

    class A2(A):
        pass

    class B2(B):
        pass

    class A2B(A2,B):
        pass

    assert issubclass(A2B,AB)

    class AB2(A,B2):
        pass

    assert issubclass(AB2,AB)

    class A2C(A2,C):
         pass

    class A2BC(A2,B,C):
        pass

    assert issubclass(A2BC,BC)

    class A2B2(A2,B2):
        pass

    class A2B2C(A2B2,C):
        pass

    class C2(C):
        pass

    class AC2(A,C2):
        pass

    class ABC2(ABC,C2):
        pass

    class A2BC2(A2B,C2):
        pass

    class A2B2C2(A2,B2,C2):
        pass

    class D(Universal):
        pass

    assert get_intersection((A,B))==AB
    assert get_intersection((A2,B2,C2))==A2B2C2
    assert issubclass(get_intersection((A,B,D)),AB)
    assert replace_proper_subset(ABC,A,None)==BC
    
    
# assert ABC.get_prime_bases()==frozenset((A,B,C))
# assert ABC.__bases__==(BC,AC,AB,C,B,A)
# assert Metaclass.add_supersets((A,B))==(A,B,AB)
# assert A2.__bases__==(A,)