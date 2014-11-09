#!/usr/bin/env python
# encoding: utf-8

from PyQt4 import QtGui, QtCore

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import matplotlib.pyplot as plt

from IntOb.EMAS import EMAS, Stats
from IntOb.hypervolume import hypervolume
from IntOb.problems import *
import sys
import random
import time


class Plot(object):

    def __init__(self, plot, steps, update_every, data, emas):
        self.emas = emas
        self.steps = steps
        self.update_every = update_every
        self.data = data
        self.plot = plot
        self.set_metadata()

    def set_metadata(self):
        pass

    def set_style(self):
        pass

    @property
    def step_axis(self):
        return [0, self.steps / self.update_every]


class EnergyPlot(Plot):
    def __init__(self, *args, **kwargs):
        super(EnergyPlot, self).__init__(*args, **kwargs)

    def set_metadata(self):
        self.plot.set_title('Total energy in the system')
        self.plot.set_xlim(self.step_axis)
        self.plot.set_ylim(self.energy_axis)

    def redraw(self):
        self.plot.hold(False)
        self.plot.plot(self.data.energy, '-')
        self.plot.hold(True)
        self.plot.plot(self.data.free_energy, '-')
        self.set_metadata()

    @property
    def energy_axis(self):
        return [0, self.data.max_energy * 1.2]


class EnergyPerIslandPlot(Plot):
    def __init__(self, *args, **kwargs):
        super(EnergyPerIslandPlot, self).__init__(*args, **kwargs)

    def set_metadata(self):
        self.plot.set_title('Energy per island')
        self.plot.set_xlim(self.step_axis)
        self.plot.set_ylim(self.energy_axis)

    def redraw(self):
        self.plot.hold(False)
        for island, history in self.data.energy_per_island.iteritems():
            self.plot.plot(history, '-')
            self.plot.hold(True)
        self.set_metadata()

    @property
    def energy_axis(self):
        n = self.emas.params['world_size']
        return [0, self.data.max_energy / n * 1.2]


class Window(QtGui.QDialog):

    step_signal = QtCore.pyqtSignal()

    def __init__(self, emas, computation, parent=None):
        super(Window, self).__init__(parent)

        self.emas = emas
        self.data = Stats(emas)
        self.computation = computation
        self.steps = computation.steps

        self.update_every = 10
        computation.callback = self.update

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        # self.toolbar = NavigationToolbar(self.canvas, self)

        plot = self.figure.add_subplot(1, 1, 1)
        self.energy_plot = EnergyPerIslandPlot(plot, steps, self.update_every,
                self.data, emas)

        self.solution_figure = plt.figure()
        self.solution_canvas = FigureCanvas(self.solution_figure)
        self.solution_plot = self.solution_figure.add_subplot(1, 1, 1)

        self.solution_plot.set_title('Solutions')

        layout = QtGui.QVBoxLayout()
        # layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.solution_canvas)
        self.setLayout(layout)

        self.schedule_computation()

    def schedule_computation(self):
        self.step_signal.connect(self.redraw)
        timer = QtCore.QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(self.start_thread)
        timer.start(1000)

    def start_thread(self):
        self.computation.start()

    def update(self, step, P):
        if step % self.update_every == 0:
            print 'Step {}'.format(step)
            self.data.update(step)
            self.step_signal.emit()
            time.sleep(1)

    def redraw(self):
        self.energy_plot.redraw()
        self.canvas.draw()

        self.redraw_solutions()
        self.solution_canvas.draw()


    def redraw_energy(self):
        self.energy_plot.hold(False)
        self.energy_plot.plot(self.data.energy, '-')

        self.energy_plot.set_title('Total energy in the system')
        self.energy_plot.set_xlim(self.step_axis)
        self.energy_plot.set_ylim(self.energy_axis)

    def redraw_solutions(self):
        self.solution_plot.hold(False)
        sx = []
        sy = []
        for island in self.emas.world:
            for agent in island.inhabitants:
                x, y = agent.val
                sx.append(x)
                sy.append(y)
        self.solution_plot.plot(sx, sy, 'ro', ms=5)

        self.solution_plot.set_title('Solutions')
        self.solution_plot.set_xlim([0, 1])
        self.solution_plot.set_ylim(bottom=0)


    @property
    def step_axis(self):
        return [0, self.steps / self.update_every]

    @property
    def energy_axis(self):
        return [0, self.data.max_energy * 1.2]


class ComputationThread(QtCore.QThread):

    def __init__(self, emas, steps, refpoint):
        super(QtCore.QThread, self).__init__()

        self.emas = emas
        self.steps = steps
        self.refpoint = refpoint

    def run(self):
        self.emas.optimize(self.steps, self.callback)


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

    alg = EMAS(F, bounds, ranges)
    refpoint = (1., 1.)
    thread = ComputationThread(alg, steps, refpoint)

    app = QtGui.QApplication(sys.argv)
    main = Window(alg, thread)
    main.show()

    sys.exit(app.exec_())

