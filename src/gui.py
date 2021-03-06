#!/usr/bin/env python
# encoding: utf-8

from PyQt4 import QtGui
from IntOb.EMAS.gui.lock import RWLock as Lock

from IntOb.EMAS import EMAS, Stats
from IntOb.hypervolume import hypervolume
from IntOb.EMAS.gui import *
from IntOb.problems import *

import sys


conf = [
{
    'rows': 1, 'cols': 1,
    'plots': [SolutionPlot]
},
{
    'rows': 1, 'cols': 1,
    'plots': [EnergyDistributionPlot]
},
{
    'rows': 2, 'cols': 2,
    'plots': [
        EncounterPlot, LifeCyclePlot,
        RNIPlot, PopulationPlot
    ]
},
{
    'rows': 2, 'cols': 2,
    'plots': [
        AgentEnergyPlot, HVRPlot,
        EnergyPlot, TravelPlot
    ]
}
]


def create_windows(conf, lock):
    windows = []

    for page in conf:
        rows = page['rows']
        cols = page['cols']
        kinds = page['plots']
        wnd = Window(steps, data, alg, kinds, rows, cols, lock)
        wnd.show()
        windows.append(wnd)

    return windows


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage: ./gui.py <problem> <steps>'
        sys.exit(1)

    problem = sys.argv[1].upper()
    steps = int(sys.argv[2])

    if problem not in globals():
        print 'Unknown problem: {}'.format(problem)
        sys.exit(1)

    problem_def = globals()[problem]
    F, bounds, ranges, volume = problem_def()
    refpoint = (1., 1.)

    alg = EMAS(F, bounds, ranges)
    data = Stats(alg, volume)

    app = QtGui.QApplication(sys.argv)
    lock = Lock()
    windows = create_windows(conf, lock)

    def update(step, P):
        print 'Step {}'.format(step)
        if step % 1 == 0:
            with lock.writeLock:
                data.update(step)
            for w in windows:
                w.update(step, P)

    computation = ComputationThread(alg, steps, refpoint, update)
    computation.start()

    sys.exit(app.exec_())

