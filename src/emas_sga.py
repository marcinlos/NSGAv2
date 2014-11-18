#!/usr/bin/env python
# encoding: utf-8

from IntOb.NSGAv2 import NSGA
from IntOb.EMAS import EMAS, Stats
from IntOb.hypervolume import hypervolume
from IntOb.problems import *

from pyevolve import Util
from pyevolve import GSimpleGA
from pyevolve import GenomeBase
from pyevolve import Selectors
from pyevolve import Initializators, Mutators
from pyevolve import Consts
from random import random, randint, uniform as rand_uniform
import sys


problem = ZDT2
steps = 100
generations = 20
population_size = 30


def eval_func(genome, steps=100):
    F, bounds, ranges, volume = problem()
    refpoint = tuple(r[1] for r in ranges)

    print 'Eval...',
    sys.stdout.flush()

    alg = EMAS(F, bounds, ranges, **genome.conf)
    guys = alg.optimize(steps, None)

    vals = [guy.val for guy in guys]

    print 'HVR for {} points...'.format(len(vals)),
    sys.stdout.flush()

    V = hypervolume(refpoint, vals)

    print 'done.'
    sys.stdout.flush()

    hvr = V / volume
    return 100 * hvr


def mutate(genome, what, s, m=None, M=None, rand_gen=rand_uniform):
    val = genome.conf[what] + rand_gen(-s, s)

    if m is not None:
        val = max(m, val)
    if M is not None:
        val = min(M, val)

    genome.conf[what] = val


def mutate_uniform(genome, what, s, m=None, M=None):
    mutate(genome, what, s, m, M, rand_uniform)


def mutate_int(genome, what, s, m=None, M=None):
    mutate(genome, what, s, m, M, randint)


def mutator(genome, **kwargs):
    p = kwargs['pmut']
    mutations = 0

    if Util.randomFlipCoin(p):
        mutate_uniform(genome, 'init_energy', 0.1)
        mutations += 1

    if Util.randomFlipCoin(p):
        mutate_uniform(genome, 'fight_transfer', 0.1)
        mutations += 1

    if Util.randomFlipCoin(p):
        mutate_uniform(genome, 'travel_threshold', 0.1)
        mutations += 1

    if Util.randomFlipCoin(p):
        mutate_uniform(genome, 'travel_cost', 0.1)
        mutations += 1

    if Util.randomFlipCoin(p):
        mutate_uniform(genome, 'reproduction_threshold', 0.1)
        mutations += 1

    if Util.randomFlipCoin(p):
        mutate_uniform(genome, 'death_threshold', 0.1)
        mutations += 1

    if Util.randomFlipCoin(p):
        mutate_uniform(genome, 'mutation_probability', 0.1)
        mutations += 1

    if Util.randomFlipCoin(p):
        mutate_uniform(genome, 'elite_threshold', 5, m=1)
        mutations += 1

    if Util.randomFlipCoin(p):
        mutate_int(genome, 'elite_islands', 3, m=1)
        mutations += 1

    if Util.randomFlipCoin(p):
        mutate_int(genome, 'world_size', 3, m=1, M=5)
        mutations += 1

    return mutations


def crossover(genome, **kwargs):
    g1 = kwargs['mom']
    g2 = kwargs['dad']

    return (g1.clone(), g2.clone())


def initializer(genome, **kwargs):
    params = {
        'world_size' : randint(1, 5),
        'population_size': randint(20, 100),
        'elite_islands': randint(1, 5),
        'init_energy': rand_uniform(0.2, 1),
        'fight_transfer': rand_uniform(0, 1),
        'travel_threshold': rand_uniform(0, 1),
        'travel_cost': rand_uniform(0, 1),
        'reproduction_threshold': rand_uniform(0, 1),
        'death_threshold': rand_uniform(0.01, 0.4),
        'mutation_probability': rand_uniform(0.05, 0.5),
        'elite_threshold': rand_uniform(1, 50),
    }
    genome.conf.update(params)


class ConfGenome(GenomeBase.GenomeBase, object):

    def __init__(self):
        object.__init__(self)
        GenomeBase.GenomeBase.__init__(self)
        self.conf = {}
        self.set_rules()

    def set_rules(self):
        self.evaluator.set(eval_func)
        self.initializator.set(initializer)
        self.mutator.set(mutator)
        self.crossover.set(crossover)

    def copy(self, g):
        GenomeBase.GenomeBase.copy(self, g)
        g.conf.update(self.conf)

    def clone(self):
        c = ConfGenome()
        self.copy(c)
        return c

    def __str__(self):
        old = GenomeBase.GenomeBase.__repr__(self)
        param_str = 'Params:\n'
        for k, v in self.conf.iteritems():
            param_str += '  {:30}: {}\n'.format(k, v)
        return old + param_str + '\n{}'.format(self.conf)


def run_main():
    genome = ConfGenome()
    ga = GSimpleGA.GSimpleGA(genome)
    ga.setMinimax(Consts.minimaxType['maximize'])
    ga.selector.set(Selectors.GRouletteWheel)
    ga.setGenerations(generations)
    ga.setPopulationSize(population_size)

    ga.evolve(freq_stats=1)

    # Best individual
    best = ga.bestIndividual()
    print best
    print eval_func(best, steps=steps)


if __name__ == "__main__":
    run_main()

