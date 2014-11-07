
from operator import mul
from .utils import weaklyInverslyDominates, inverslyDominates, maximal


def volBetween(a, b):
    """ Computes volume of cuboid spanned by a and b
    """
    sides = [abs(x - y) for x, y in zip(a, b)]
    return reduce(mul, sides, 1)


def findSmallestGreater(x, xs, i):
    """ Finds element of collection xs that has smallest i-th component greater
    than that of x
    """
    best = float('+inf')
    for v in xs:
        if v[i] > x[i] and v[i] < best:
            best = v[i]
    return best


def changed(x, i, xi):
    """ Returns copy of vector x with i-th coordinate changed to xi
    """
    xx = list(x)
    xx[i] = xi
    return tuple(xx)


def oppositeVertex(x, p, xs):
    """ Finds opposite vertex of the cuboid (inversly) dominated exclusively
    by x, not by any other element of xs, with respect to reference point p.
    """
    n = len(x)
    xs = list(xs)
    xs.append(p)
    v = [findSmallestGreater(x, xs, i) for i in xrange(n)]
    for i in xrange(n):
        if v[i] == float('+inf'):
            v[i] = p[i]
    return tuple(v)


def spawns(x, z, v, p, xs):
    """
    x  - vertex
    z  -
    v  - opposite vertex
    p  - reference point
    xs - all the points
    """
    ys = []
    for i in xrange(z):
        if x[i] != p[i]:
            y = changed(x, i, v[i])
            if not any(weaklyInverslyDominates(y, xx) for xx in xs):
                ys.append((y, i))
    return ys


def hypervolume(p, xs):
    """ Computes hypervolume of union of cuboids spanned by p and xs.

    p    - reference point
    xs - solution
    """
    n = len(p)
    points = [(x, n) for x in maximal(xs, inverslyDominates)]
    volume = 0

    while points:
        x, z = points.pop()
        xxs = [a for a, _ in points]
        v = oppositeVertex(x, p, xxs)
        volume += volBetween(x, v)
        ys = spawns(x, z, v, p, xxs)
        points = ys + points

    return volume

