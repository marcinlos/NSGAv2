#!/usr/bin/env python
# encoding: utf-8

from PyQt4 import QtGui

from IntOb.EMAS import EMAS, Stats
from IntOb.hypervolume import hypervolume
from IntOb.EMAS.gui import *
from IntOb.problems import *

import sys


conf = [{
    'rows': 1, 'cols': 1,
    'plots': [SolutionPlot]
}, {
    'rows': 3, 'cols': 1,
    'plots': [EnergyPlot, EnergyPerIslandPlot, PopulationPlot]
}]


def create_windows(conf):
    windows = []

    for page in conf:
        rows = page['rows']
        cols = page['cols']
        kinds = page['plots']
        wnd = Window(steps, data, alg, kinds, rows, cols)
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
    F, bounds, ranges = problem_def()
    refpoint = (1., 1.)

    alg = EMAS(F, bounds, ranges)
    data = Stats(alg)

    app = QtGui.QApplication(sys.argv)
    windows = create_windows(conf)

    def update(step, P):
        print 'Step {}'.format(step)
        data.update(step)
        for w in windows:
            w.update(step, P)

    computation = ComputationThread(alg, steps, refpoint, update)
    computation.start()

    sys.exit(app.exec_())

