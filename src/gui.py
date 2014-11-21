#!/usr/bin/env python
# encoding: utf-8

from PyQt4 import QtGui
from IntOb.gui.lock import RWLock as Lock

from IntOb.EMAS import Stats
from IntOb.EMAS2 import EMAS
from IntOb.hypervolume import hypervolume
from IntOb.EMAS.param_sets import param_sets
from IntOb.gui import *
from IntOb.problems import *

import sys
import argparse


conf = [
{
    'rows': 2, 'cols': 2,
    'plots': [
        SolutionPlot, SolutionDensityPlot,
        SolutionPrestigePlot, SolutionEnergyPlot
    ]
},
{
    'rows': 1, 'cols': 1,
    'plots': [EliteSolutionPlot]
},
{
    'rows': 1, 'cols': 1,
    'plots': [FrontPlot]
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


def create_windows(conf, steps, lock):
    windows = []

    for page in conf:
        rows = page['rows']
        cols = page['cols']
        kinds = page['plots']
        wnd = Window(steps, data, alg, kinds, rows, cols, lock)
        wnd.show()
        windows.append(wnd)

    return windows


def parse_params():
    parser = argparse.ArgumentParser()
    parser.add_argument('problem', help='optimization problem to solve')
    parser.add_argument('steps', help='number of simulation steps', type=int)
    parser.add_argument('param_set', help='predefined parameter set', nargs='?')
    parser.add_argument('--stat-freq', type=int, default=1)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_params()

    try:
        problem_def = globals()[args.problem.upper()]
    except KeyError:
        print 'Unknown problem: {}'.format(problem)
        sys.exit(1)

    if args.param_set is not None:
        try:
            params = param_sets[args.param_set]
        except KeyError:
            print 'Unknown parameter set: {}'.format(set_name)
            sys.exit(1)
    else:
        params = {}

    F, bounds, ranges, volume = problem_def()

    alg = EMAS(F, bounds, ranges, **params)
    data = Stats(alg, volume)

    app = QtGui.QApplication(sys.argv)
    lock = Lock()
    windows = create_windows(conf, args.steps, lock)

    def update(step, P):
        print 'Step {}'.format(step)
        if step % args.stat_freq == 0:
            with lock.writeLock:
                data.update(step)
            for w in windows:
                w.update(step, P)

    computation = ComputationThread(alg, args.steps, update)
    computation.start()

    sys.exit(app.exec_())

