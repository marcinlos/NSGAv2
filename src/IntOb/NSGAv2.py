
from random import random
from collections import defaultdict
from operator import itemgetter


def lerp(a, b, t):
    """ Linear interpolation between a and b

    a - start point
    b - end point
    t - interpolation weight
    """
    return (1.0 - t) * a + t * b


def rand(a, b):
    """ Returns random, uniformly distributed real number
    between a and b.
    """
    t = random() # [0, 1)
    return lerp(a, b, t)


def randVector(bounds):
    """ Returns random vector with components distributed uniformly on the
    interval defined by bounds.

    bounds - sequence of pairs of numbers (a, b), defining minimal and maximal
             values of each component
    """
    return tuple(rand(a, b) for (a, b) in bounds)


def randomPopulation(size, bounds):
    """ Creates random initial population - set of points.
    
    size   - number of points to create
    bounds - bounds for each dimension
    """
    return {randVector(bounds) for _ in xrange(size)}


def dominates(a, b):
    """ Tests whether b dominates a, where a, b are vectors with the same
    number of components.
    """
    ab = zip(a, b)
    return all(x <= y for x, y in ab) and any(x  < y for x, y in ab)


def nonDominatedSort(f, points):
    """ Partitions set of points into non-dominance classes with respect to
    their values of p, i.e. calculates subsets such that no points of "lower"
    subset dominate points of "higher" subsets, and no points dominate
    others in each set.

    f       - evaluating function
    points  - points in domain space

    Returns: tuple consisting of list of sets (classes of dominance), and map
             with index of class for each point
    """
    S = defaultdict(set)
    n = defaultdict(int)
    rank = defaultdict(int)
    front = [set()]

    for p in points:
        for q in points:
            fp = f(p)
            fq = f(q)
            if dominates(fp, fq):
                S[p].add(q)
            elif dominates(fq, fp):
                n[p] += 1
        if n[p] == 0:
            rank[p] = 0
            front[0].add(p)
    i = 0
    while front[i]:
        Q = set()
        for p in front[i]:
            for q in S[p]:
                n[q] -= 1
                if n[q] == 0:
                    rank[q] = i + 1
                    Q.add(q)
        i += 1
        front.append(Q)

    front.pop()  # last set on the list is empty
    return (front, rank)


def sortByValue(points, vals):
    """ Sorts points according to values
    """
    return sorted(zip(points, vals), key=itemgetter(1))


def crowdingDistance(points, vals, bounds):
    """ Calculates 'crowding distance' - approximation to the perimeter of the
    hypercube around the value for each point that does not contain any other
    values.

    points - points in domain space
    values - precalculated values of the evaluation functions for each point
    bounds - extremal values of each evaluation functions
    """
    dist = defaultdict(float)
    n = len(vals[0])

    for i in xrange(0, n):
        ivals = [v[i] for v in vals]
        ipoints = sortByValue(points, ivals)

        dist[ipoints[0][0]] += float('+inf')
        dist[ipoints[-1][0]] += float('+inf')

        d = bounds[i][1] - bounds[i][0]

        for j in xrange(1, len(points) - 1):
            p  = ipoints[j][0]
            vp = ipoints[j - 1][1]
            vn = ipoints[j + 1][1]
            dist[p] += (vn - vp) / float(d)

    return dist



