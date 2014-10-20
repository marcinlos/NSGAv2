
from random import random, randint, sample, shuffle
from collections import defaultdict
from operator import itemgetter, mul



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


def randomPopulation(size, bounds):
    """ Creates random initial population - set of points.
    
    size   - number of points to create
    bounds - bounds for each dimension
    """
    return [randVector(bounds) for _ in xrange(size)]


def dominates(a, b):
    """ Tests whether b dominates a, where a, b are vectors with the same
    number of components.
    """
    ab = zip(a, b)
    return all(x <= y for x, y in ab) and any(x  < y for x, y in ab)


def inverslyDominates(a, b):
    """ Tests whether b dominates a inversly, or is equal to a, where a, b 
    are vectors with the same number of components.
    """
    ab = zip(a, b)
    return all(x >= y for x, y in ab) and any(x > y for x, y in ab)


def weaklyInverslyDominates(a, b):
    """ Tests whether b dominates a inversly, or is equal to a, where a, b 
    are vectors with the same number of components.
    """
    ab = zip(a, b)
    return all(x >= y for x, y in ab)


def nonDominatedSort(points, vals):
    """ Partitions set of points into non-dominance classes with respect to
    their values, i.e. calculates subsets such that no points of "lower"
    subset dominate points of "higher" subsets, and no points dominate
    others in each set.

    points  - points in domain space
    vals    - values at points

    Returns: tuple consisting of list of sets (classes of dominance), and map
             with index of class for each point
    """
    S = defaultdict(list)
    n = defaultdict(int)
    rank = defaultdict(int)
    front = [list()]
    pairs = zip(points, vals)

    for p, fp in pairs:
        for q, fq in pairs:
            if dominates(fp, fq):
                S[p].append(q)
            elif dominates(fq, fp):
                n[p] += 1
        if n[p] == 0:
            rank[p] = 0
            front[0].append(p)
    i = 0
    while front[i]:
        Q = list()
        for p in front[i]:
            for q in S[p]:
                n[q] -= 1
                if n[q] == 0:
                    rank[q] = i + 1
                    Q.append(q)
        i += 1
        front.append(Q)

    front.pop()  # last set on the list is empty
    return (front, rank)


def partialSort(xs, less):
    S = defaultdict(list)
    n = defaultdict(int)
    rank = defaultdict(int)
    front = [[]]

    for x in xs:
        for y in xs:
            if less(x, y):
                S[x].append(y)
            elif less(y, x):
                n[x] += 1
        if n[x] == 0:
            rank[x] = 0
            front[0].append(x)
    i = 0
    while front[i]:
        Q = []
        for x in front[i]:
            for y in S[x]:
                n[y] -= 1
                if n[y] == 0:
                    rank[y] = i + 1
                    Q.append(y)
        i += 1
        front.append(Q)

    front.pop()  # last set on the list is empty
    return (front, rank)


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


def sortByValue(points, vals):
    """ Sorts points according to values
    """
    return sorted(zip(points, vals), key=itemgetter(1))


def crowdingDistance(points, vals, ranges):
    """ Calculates 'crowding distance' - approximation to the perimeter of the
    hypercube around the value for each point that does not contain any other
    values.

    points - points in domain space
    values - precalculated values of the evaluation functions for each point
    ranges - extremal values of each evaluation functions
    """
    dist = defaultdict(float)
    n = len(vals[0])

    for i in xrange(0, n):
        ivals = [v[i] for v in vals]
        ipoints = sortByValue(points, ivals)

        dist[ipoints[0][0]] += float('+inf')
        dist[ipoints[-1][0]] += float('+inf')

        d = ranges[i][1] - ranges[i][0]

        for j in xrange(1, len(points) - 1):
            p  = ipoints[j][0]
            vp = ipoints[j - 1][1]
            vn = ipoints[j + 1][1]
            dist[p] += (vn - vp) / float(d)

    return dist

# Hypervolume metric

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



def mutation(a, p, bounds, max_changes):
    """ Mutates each component of the vector with probability p, changing it
    by random amount, uniformly choosen from the symmetric intervals specified
    by max_changes vector, ensuring the result stays inside the region given
    by bounds.

    a           - vector to mutate
    p           - probability of mutation
    bounds      - solution domain
    max_changes - maximal acceptable changes due to mutation for each somponent
    """
    b = []
    for i, x in enumerate(a):
        if tossCoin(p):
            c = max_changes[i]
            d = lerp(-c, c, random())
            m, M = bounds[i]
            x = clamp(x + d, m, M)
        b.append(x)
    return tuple(b) 


def onePointCrossover(a, b):
    """ Simplest crossover schema - pick random component, and paste opposite
    ends.

    AAAAAAAAAAA
    BBBBBBBBBBB
        ^
    AAAAABBBBBB
    BBBBBAAAAAA
    """
    n = len(a)
    i = randint(0, n - 1)
    ab = a[:i] + b[i:]
    ba = b[:i] + a[i:]
    return (ab, ba)


def crossover(a, b):
    c1 = []
    c2 = []
    for x, y in zip(a, b):
        u = random()
        f = u #pow(2 * u, 1 / (1 + 0.3))

        c1.append(0.5 * ((1 - f) * x + (1 + f) * y))
        c2.append(0.5 * ((1 + f) * x + (1 - f) * y))
    return (tuple(c1), tuple(c2))


def select(population, compare, N, p):
    """ Performs selection of N individuals from the population, using binary
    tournament scheme with pressure p. Concretly, pair of individuals is
    drawn randomly from the population, they are compared with specified
    comparator and with probability p the winner is selected.

    population - population to select from
    compare    - function used to compare individuals, accepts two arguments,
                 and returns True if the first one is not better than the second
    N          - number of individuals to select
    p          - selection pressure
    """
    res = []
    for _ in xrange(N):
        a, b = sample(population, 2) 
        if compare(a, b):
            a, b = b, a
        # Here a >= b
        choosen = a if tossCoin(p) else b
        res.append(choosen)
    return res


class NSGA(object):

    defparams = {
        'mutation_prob': 0.2,
        'crossover_prob': 0.7,
        'population_size': 300,
        'selection_pressure': 1.0,
    }

    def __init__(self, fs, bounds, ranges, **params):
        self.f = lambda x: tuple(f(x) for f in fs)
        self.bounds = bounds
        self.ranges = ranges
        self.params = dict(NSGA.defparams, **params)

        s = 0.1 
        self.max_changes = [s * (M - m) for m, M in bounds]


    @staticmethod
    def crowdedComparison(a, b):
        _, a_rank, a_crowd = a
        _, b_rank, b_crowd = b
        # better = greater rank, or smaller crowding distance
        return (a_rank, -a_crowd) >= (b_rank, -b_crowd)
        #return a_rank >= b_rank or (a_rank == b_rank and a_crowd <= b_crowd)

    @staticmethod
    def crowdKey(a):
        _, a_rank, a_crowd = a
        return 0
        return a_crowd


    def createOffspring(self, evaluated, N):
        p = self.params['selection_pressure']
        selected = select(evaluated, NSGA.crowdedComparison, N, p)
        Q = [p for p, _, _ in selected]
        shuffle(Q)
        cp = self.params['crossover_prob']
        pairsToMate = int(lerp(0, N / 2, random()))

        for i in xrange(pairsToMate):
            a = Q[2 * i]
            b = Q[2 * i + 1]
            ab, ba = crossover(a, b) #onePointCrossover(a, b)
            Q[2 * i] = ab
            Q[2 * i + 1] = ba

        mp = self.params['mutation_prob']
        return [mutation(a, mp, self.bounds, self.max_changes) for a in Q]


    def optimize(self, steps, callback=None):
        N = self.params['population_size']

        P = randomPopulation(N, self.bounds)
        vals = map(self.f, P)
        v = dict(zip(P, vals))

        fronts, ranks = nonDominatedSort(P, vals)
        cdist = crowdingDistance(P, vals, self.ranges)
        evaluated = [(p, ranks[p], cdist[p]) for p in P]
        Q = self.createOffspring(evaluated, N)

        for step in xrange(steps):
            R = P + Q
            vals = map(self.f, R)
            v = dict(zip(R, vals))
            fronts, ranks = nonDominatedSort(R, vals)
            cdist = {}

            Pnext = []
            i = 0

            while len(Pnext) + len(fronts[i]) <= N:
                F = fronts[i]
                Pnext.extend(F)
                vals = [v[p] for p in F]
                cdist.update(crowdingDistance(F, vals, self.ranges))
                i += 1

            reminder = N - len(Pnext)
            if reminder > 0:
                F = fronts[i]
                vals = [v[p] for p in F]
                cdist.update(crowdingDistance(F, vals, self.ranges))

                evaluated = [(p, ranks[p], cdist[p]) for p in F]
                evaluated.sort(key=NSGA.crowdKey)
                F = [p for p, _, _ in evaluated]
                Pnext.extend(F[-reminder:])
            P = Pnext

            evaluated = [(p, ranks[p], cdist[p]) for p in P]
            Q = self.createOffspring(evaluated, N)
            
            if callback:
                callback(step, P)

        return Pnext



