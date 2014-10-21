#! /usr/bin/env python

import IntOb.NSGAv2 as nsga
from itertools import repeat
from math import sqrt, sin, pi
import sys


def makeCallback(F, ranges, volume):
    pass
    f, g = F
    refpoint = tuple(r[1] for r in ranges)

    def onStep(step, P):
        print 'step', step

        if step % 10 == 0:
            vals = [guy.val for guy in P]
            vol = nsga.hypervolume(refpoint, vals)

            if volume:
                print 'HVR = {:.2%}'.format(vol / volume)
            else:
                print 'HV = {}'.format(vol)

            with open('step_{:04}.dat'.format(step), 'w') as out:
                for guy in P:
                    x, y = guy.val
                    line = '{:20} {:20}\n'.format(x, y)
                    out.write(line)

    return onStep


steps = int(sys.argv[1])


def run(F, bounds, ranges, volume=None):
    alg = nsga.NSGA(F, bounds, ranges) 
    return alg.optimize(steps, makeCallback(F, ranges, volume))


def simple():
    f = lambda (x, y): x
    g = lambda (x, y): 1 - x * y
    F = (f, g)

    bounds = [(0, 1), (0, 1)] 
    ranges = [(0, 1), (0, 1)] 

    run(F, bounds, ranges)


g = lambda x: 1 + 9 * sum(x[1:]) / float(len(x) - 1)


def ZDT1():
    F = (
        lambda x: x[0],
        lambda x: g(x) * (1 - sqrt(x[0] / g(x)))
    )
    n = 3
    bounds = tuple(repeat((0, 1), n))
    ranges = [(0, 1), (0, 1)] 

    run(F, bounds, ranges)


def ZDT2():
    F = (
        lambda x: x[0],
        lambda x: g(x) * (1 - (x[0] / g(x))**2)
    )
    n = 3
    bounds = tuple(repeat((0, 1), n))
    ranges = [(0, 1), (0, 1)] 

    run(F, bounds, ranges)


def ZDT3():
    F = (
        lambda x: x[0],
        lambda x: 0.5 * (1 + g(x) * (1 - sqrt(x[0]/g(x)) - x[0]/g(x) * sin(10*pi*x[0])))
    )
    n = 30
    bounds = tuple(repeat((0, 1), n))
    ranges = [(0, 1), (0, 1)] 

    run(F, bounds, ranges)


if __name__ == '__main__':
    problem = sys.argv[1].upper()
    impl = globals()[problem]

