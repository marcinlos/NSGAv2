#!/usr/bin/env python
# encoding: utf-8

from PyQt4 import QtGui

import matplotlib.pyplot as plt
from IntOb.gui.lock import RWLock as Lock
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from IntOb.EMAS import Stats
from IntOb.EMAS2 import EMAS
from IntOb.hypervolume import hypervolume
from IntOb.EMAS.param_sets import param_sets
from IntOb.gui import *
from IntOb.problems import *

import os
import errno
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


plot_conf = {
    (EnergyPlot, 'energy'),
    (EnergyDistributionPlot, 'energy_distribution'),
    (SolutionEnergyPlot, 'solution_energy'),
    (SolutionDensityPlot, 'density'),
    (SolutionPrestigePlot, 'prestige'),
    (EnergyPerIslandPlot, 'energy_per_island'),
    (PopulationPlot, 'population'),
    (EliteSolutionPlot, 'elite_solutions'),
    (SolutionPlot, 'solutions'),
    (FrontPlot, 'front'),
    (HVRPlot, 'hvr'),
    (LifeCyclePlot, 'lifecycle'),
    (TravelPlot, 'travel'),
    (EncounterPlot, 'encounters'),
    (AgentEnergyPlot, 'agent_energy'),
}

def ensure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

def create_plots(conf, step, steps, data, alg, prefix):
    plots = []
    for kind, path in conf:
        fig = Figure()
        ax = fig.add_subplot(111)
        plot = kind(fig, ax, steps, data, alg)
        plot.update()
        directory = '{}/{}'.format(prefix, path)
        ensure_path_exists(directory)
        out = '{}/{}.png'.format(directory, step)

        canvas = FigureCanvas(fig)
        canvas.print_figure(out, dpi=200)


def create_windows(conf, steps, data, alg, lock):
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
    parser.add_argument('--prefix', default='.')
    parser.add_argument('--save', action='store_true')
    parser.add_argument('--dim', type=int, default=30)
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

    problem = problem_def(n=args.dim)

    alg = EMAS(problem, **params)
    data = Stats(alg)

    app = QtGui.QApplication(sys.argv)
    lock = Lock()
    windows = create_windows(conf, args.steps, data, alg, lock)

    def update(step, P):
        print 'Step {}'.format(step)
        if step % args.stat_freq == 0:
            with lock.writeLock:
                data.update(step)
            for w in windows:
                w.update(step, P)
            if args.save:
                create_plots(plot_conf, step, args.steps, data, alg, args.prefix)

    computation = ComputationThread(alg, args.steps, update)
    computation.start()

    sys.exit(app.exec_())

