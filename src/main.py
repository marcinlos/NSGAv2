#! /usr/bin/env python

import IntOb.NSGAv2 as nsga
from itertools import repeat
from math import sqrt, sin, pi


def makeCallback(F):
    f, g = F

    def onStep(step, P):
        print 'step', step
        with open('step_{:04}.dat'.format(step), 'w') as out:
            for p in P:
                x = f(p)
                y = g(p)
                line = '{:20} {:20}\n'.format(x, y)
                out.write(line)
    return onStep


steps = 100


def run(F, bounds, ranges):
    alg = nsga.NSGA(F, bounds, ranges) 
    return alg.optimize(steps, makeCallback(F))


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
    #ZDT1()
    #ZDT2()
    ZDT3()

