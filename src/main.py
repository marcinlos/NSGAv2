#! /usr/bin/env python

import IntOb.NSGAv2 as nsga
from IntOb.hypervolume import hypervolume
from IntOb.problems import *
import sys


def makeCallback(F, ranges, volume):
    pass
    f, g = F
    refpoint = tuple(r[1] for r in ranges)

    def onStep(step, P):
        print 'step', step

        if step % 10 == 0:
            vals = [guy.val for guy in P]
            vol = hypervolume(refpoint, vals)

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


steps = int(sys.argv[2])


def run(F, bounds, ranges, method, volume=None):
    alg = method(F, bounds, ranges)
    return alg.optimize(steps, makeCallback(F, ranges, volume))



if __name__ == '__main__':
    problem = sys.argv[1].upper()
    impl = globals()[problem]
    F, bounds, ranges = impl()
    run(F, bounds, ranges, method=nsga.NSGA)

