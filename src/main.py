#! /usr/bin/env python

from IntOb.NSGAv2 import NSGA
from IntOb.EMAS2 import EMAS
from IntOb.EMAS import Stats
from IntOb.hypervolume import hypervolume
from IntOb.problems import *
import sys

class Callback(object):

    def __init__(self, ranges, volume):
        self.ranes = ranges
        self.refpoint = tuple(r[1] for r in ranges)
        self.volume = volume
        self.gap = 10

    def dump_to_file(self, step, guys):
        with open('step_{:04}.dat'.format(step), 'w') as out:
            for guy in guys:
                x, y = guy.val
                line = '{:20} {:20}\n'.format(x, y)
                out.write(line)

    def print_hypervolume(self, guys):
        vals = [guy.val for guy in guys]
        V = hypervolume(self.refpoint, vals)

        if self.volume:
            print 'HVR = {:.2%}'.format(V / volume)
        else:
            print 'HV = {}'.format(V)

    def step_nsga(self, step, guys):
        print 'step {}'.format(step)
        if step % self.gap == 0:
            self.print_hypervolume(guys)
            self.dump_to_file(step, guys)

    def step_emas(self, step, guys):

        if step % self.gap == 0:
            print 'step {}'.format(step)
            total_energy = 0
            for agent in guys:
                total_energy += agent.energy

            print 'population: {}'.format(len(guys))
            print 'energy: {}'.format(total_energy)
            self.print_hypervolume(guys)
            self.dump_to_file(step, guys)

    def for_method(self, method):
        return {
            NSGA: self.step_nsga,
            EMAS: self.step_emas,
        }[method]

    def at_end(self, guys):
        self.print_hypervolume(guys)


def run(F, bounds, ranges, method, volume):
    alg = method(F, bounds, ranges)
    cb = Callback(ranges, volume)
    guys = alg.optimize(steps, cb.for_method(method))
    cb.at_end(guys)


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print 'Usage: ./gui.py <method> <problem> <steps>'
        sys.exit(1)

    method_name = sys.argv[1].upper()
    problem_name = sys.argv[2].upper()
    steps = int(sys.argv[3])

    problem = globals()[problem_name]
    method = globals()[method_name]

    F, bounds, ranges, volume = problem()
    run(F, bounds, ranges, method, volume)

