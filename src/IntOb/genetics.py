
from random import random, sample
from .utils import dominates, randVector, tossCoin, lerp, clamp


class Specimen(object):
    """ Single element of the population
    """

    def __init__(self, x):
        self.x = tuple(x)
        self.val = None

    def __str__(self):
        return '|{}|'.format(self.x)

    def domain_dim(self):
        return len(self.x)

    def value_dim(self):
        return len(self.val)

    @staticmethod
    def dominates(a, b):
        return dominates(a.val, b.val)


def randomPopulation(size, bounds):
    """ Creates random initial population - set of points.

    size   - number of points to create
    bounds - bounds for each dimension
    """
    return [Specimen(randVector(bounds)) for _ in xrange(size)]


def mutation(a, p, bounds, max_changes):
    """ Mutates each component of the vector with probability p, changing it
    by random amount, uniformly chosen from the symmetric intervals specified
    by max_changes vector, ensuring the result stays inside the region given
    by bounds.

    a           - vector to mutate
    p           - probability of mutation
    bounds      - solution domain
    max_changes - maximal acceptable changes due to mutation for each component

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
    tournament scheme with pressure p. Concretely, pair of individuals is
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

