
from random import random, randint, sample, shuffle
from collections import defaultdict
from operator import itemgetter, attrgetter, mul
from utils import lerp, clamp, rand, tossCoin, randVector, maximal


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


def partialSort(xs, less):
    """ Partitions set of points into classes wrt strong order given by
    comparator function 'less'.

    xs   - iterable collection
    less - comparator representing strong order relation <, function of two
           arguments with less(a, b) == True iff a < b

    Returns: tuple consisting of list of sets (classes of dominance)
    """
    S = defaultdict(list)
    n = defaultdict(int)
    front = [[]]

    for x in xs:
        for y in xs:
            if less(x, y):
                S[x].append(y)
            elif less(y, x):
                n[x] += 1
        if n[x] == 0:
            front[0].append(x)
    i = 0
    while front[i]:
        Q = []
        for x in front[i]:
            for y in S[x]:
                n[y] -= 1
                if n[y] == 0:
                    Q.append(y)
        i += 1
        front.append(Q)

    front.pop()  # last set on the list is empty
    return front



class Specimen(object):
    """ Single element of the population
    """

    def __init__(self, x):
        self.x = tuple(x)
        self.rank = None
        self.val = None
        self.crowd = None

    def __str__(self):
        return '|{}|'.format(self.x)

    def domain_dim(self):
        return len(self.x)

    def value_dim(self):
        return len(self.val)

    @staticmethod
    def dominates(a, b):
        return dominates(a.val, b.val)

    @staticmethod
    def crowdedCmp(a, b):
        return (a.rank, -a.crowd) < (b.rank, -b.crowd)


def randomPopulation(size, bounds):
    """ Creates random initial population - set of points.

    size   - number of points to create
    bounds - bounds for each dimension
    """
    return [Specimen(randVector(bounds)) for _ in xrange(size)]


def computeCrowdingDistance(guys, ranges):
    """ Calculates 'crowding distance' - approximation to the perimeter of the
    hypercube around the value for each point that does not contain any other
    values.

    guys   - elements of the population
    ranges - extremal values of each evaluation functions
    """
    n = guys[0].value_dim()

    for guy in guys:
        guy.crowd = 0

    for i in xrange(0, n):
        guys.sort(key=lambda guy: guy.val[i])

        guys[ 0].crowd += float('+inf')
        guys[-1].crowd += float('+inf')

        d = ranges[i][1] - ranges[i][0]

        for j in xrange(len(guys) - 1):
            x_prev = guys[j - 1].x[i]
            x_next = guys[j + 1].x[i]
            guys[j].crowd += (x_next - x_prev) / d


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


# Genetic operators

def mutation(a, p, bounds, max_changes):
    """ Mutates each component of the vector with probability p, changing it
    by random amount, uniformly choosen from the symmetric intervals specified
    by max_changes vector, ensuring the result stays inside the region given
    by bounds.

    a           - vector to mutate
    p           - probability of mutation
    bounds      - solution domain
    max_changes - maximal acceptable changes due to mutation for each somponent

    Returns: new, modified specimen
    """
    b = []
    for i, x in enumerate(a.x):
        if tossCoin(p):
            c = max_changes[i]
            d = lerp(-c, c, random())
            m, M = bounds[i]
            x = clamp(x + d, m, M)
        b.append(x)
    return Specimen(b)


def crossover(a, b):
    """ Performs crossover of to specimens, effectively interpolating between
    their components.

    a, b - specimens to mate
    Returns: pair of children
    """
    c1 = []
    c2 = []
    for x, y in zip(a.x, b.x):
        u = random()
        f = u #pow(2 * u, 1 / (1 + 0.3))

        c1.append(0.5 * ((1 - f) * x + (1 + f) * y))
        c2.append(0.5 * ((1 + f) * x + (1 - f) * y))
    return (Specimen(c1), Specimen(c2))


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
        'mutation_prob': 0.08,
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


    def createOffspring(self, P, N):
        p = self.params['selection_pressure']
        Q = select(P, Specimen.crowdedCmp, N, p)
        shuffle(Q)

        cp = self.params['crossover_prob']
        # max_pairs = int(cp * N/2)
        # pairs = randint(0, max_pairs)
        crossed = 0

        for i in xrange(N/2):
            if tossCoin(cp):
                a = Q[2 * i]
                b = Q[2 * i + 1]
                ab, ba = crossover(a, b)
                Q[2 * i] = ab
                Q[2 * i + 1] = ba
                crossed += 1

        print 'Crossover for {} pairs'.format(crossed)

        mp = self.params['mutation_prob']
        return [mutation(a, mp, self.bounds, self.max_changes) for a in Q]


    def evaluate(self, guys):
        for guy in guys:
            if guy.val is None:
                guy.val = self.f(guy.x)


    def nonDominatedSort(self, guys):
        fronts = partialSort(guys, Specimen.dominates)

        for rank, front in enumerate(fronts):
            for guy in front:
                guy.rank = rank

        return fronts


    def optimize(self, steps, callback=None):
        N = self.params['population_size']

        P = randomPopulation(N, self.bounds)
        self.evaluate(P)
        self.nonDominatedSort(P)

        computeCrowdingDistance(P, self.ranges)
        Q = self.createOffspring(P, N)

        for step in xrange(steps):
            R = P + Q
            self.evaluate(R)
            fronts = self.nonDominatedSort(R)

            print 'Fronts: {}'.format(len(fronts))

            Pnext = []
            i = 0

            while len(Pnext) + len(fronts[i]) <= N:
                F = fronts[i]
                Pnext += F
                self.evaluate(F)
                computeCrowdingDistance(F, self.ranges)
                i += 1

            reminder = N - len(Pnext)
            print 'Whole {} fronts taken, reminder = {}'.format(i, reminder)

            if reminder > 0:
                F = fronts[i]
                self.evaluate(F)
                computeCrowdingDistance(F, self.ranges)

                F.sort(key=attrgetter('crowd'))
                Pnext += F[-reminder:]

            P = Pnext
            Q = self.createOffspring(P, N)

            if callback:
                callback(step, P)

        return Pnext



