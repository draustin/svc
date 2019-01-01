# Strict Venn Classes

When introducing object-oriented programming, an analogy is often made between classes and sets (in the mathematical sense), with objects (instances of the classes) analogous to elements of the set. Defining a subclasses is analogous to defining a proper subset. SVC is a base class and set of associated tools for dynamically creating classes using semantics closely related to set theory. Specifically, in SVC there
is a one-to-one mapping between classes and sets. Classes are declared in one of
two ways:
1. as a proper subset of a single existing class, just as in 'normal' Python/C++/Java/...,
2. as the set intersection of two or more existing classes.

Method 2 replaces regular multiple inheritance. In most languages (including Python and C++), multiple inheritance is technically analogous to "proper subset of the set intersection". For example in Python, if I define `class C1(A, B):` and `class C2(A, B):` then `C1` and `C2` are different, but in SVC they would be the same. If we wanted them to be different, we would first define `class C(A, B)` and then define `class C1(C)` and `class C2(C)`.

# Motivation
I wrote SVC in order to handle large numerical simulations with many different parameters. 

Imagine a set of classes representing a calculation or simulation that depends on many parameters, such as the physical parameters of the system under study and/or numerical parameters. We might use a base class to represent the dependence of the result on a parameter. Say class X incorporates dependence of the calculation on some parameter x. For example,
X might have methods for plotting results as a function of x. Let V and W be classes representing
different types of calculations. We might define subclasses VX and WX with specific
methods for dealing with a dependence on X of a V or W respectively. Now imagine
we have some generic code for converting a simulation represented by class C
from a type V to a type W, regardless of its parameters, such as x. We need some generic way of saying "replace V with W in the bases of C". SVC offers a way of performing these kinds of transformations automatically.

# Introduction
The class Universal is a superset of all classes and is a superclass of all strict
Venn classes.

Apart from that see the tests.
