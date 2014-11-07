
from random import shuffle
from operator import attrgetter
from .utils import tossCoin, partialSort
from .genetics import Specimen, randomPopulation, mutation, crossover, select


def crowdedCmp(a, b):
    return (a.rank, -a.crowd) < (b.rank, -b.crowd)


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
        Q = select(P, crowdedCmp, N, p)
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



