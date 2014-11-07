
from random import random


def lerp(a, b, t):
    """ Linear interpolation between a and b

    a - start point
    b - end point
    t - interpolation weight
    """
    return (1.0 - t) * a + t * b


def clamp(a, m, M):
    """ Returns a if it lies in [m, M], otherwise returns m or M,
    depending on which side of [m, M] does a lie.
    """
    return m if a < m else M if a > M else a


def rand(a, b):
    """ Returns random, uniformly distributed real number
    between a and b.
    """
    t = random() # [0, 1)
    return lerp(a, b, t)


def tossCoin(p):
    """ Returns True with probability p, and False otherwise"""
    return random() <= p


def randVector(bounds):
    """ Returns random vector with components distributed uniformly on the
    interval defined by bounds.

    bounds - sequence of pairs of numbers (a, b), defining minimal and maximal
             values of each component
    """
    return tuple(rand(a, b) for (a, b) in bounds)


def maximal(xs, less):
    """ Finds maximal (nondominated) elements of collection xs, wrt ordering
    defined by argument 'less'.

    xs   - iterable collection
    less - comparator representing strong order relation <, function of two
           arguments with less(a, b) == True iff a < b
    """
    M = []
    for x in xs:
        for y in xs:
            if less(x, y):
                break
        else:
            M.append(x)
    return M

