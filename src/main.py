#! /usr/bin/env python

import IntOb.NSGAv2 as nsga
from IntOb.EMAS import EMAS, Stats
from IntOb.hypervolume import hypervolume
from IntOb.problems import *
import sys


def makeCallback(F, ranges, volume):
    f, g = F
    refpoint = tuple(r[1] for r in ranges)

    def onStep(step, P):
        total_energy = 0
        for agent in P:
            total_energy += agent.energy

        print 'step {}, population: {}, energy: {}'.format(step, len(P), total_energy)

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
    #run(F, bounds, ranges, method=nsga.NSGA)
    run(F, bounds, ranges, method=EMAS)

