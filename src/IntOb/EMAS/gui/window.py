
import time
from PyQt4 import QtGui, QtCore
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar

class Window(QtGui.QDialog):

    step_signal = QtCore.pyqtSignal()
    start_delay = 1000
    update_delay = 0.5
    redraw_period = 10

    def __init__(self, steps, data, alg, plot_types, rows=1, cols=1, parent=None):
        super(Window, self).__init__(parent)

        fig = plt.figure()
        self.canvas = FigureCanvas(fig)
        # self.toolbar = NavigationToolbar(self.canvas, self)

        self.plots = []

        i = 1
        for pt in plot_types:
            p = fig.add_subplot(rows, cols, i)
            plot = pt(p, steps, data, alg)
            self.plots.append(plot)
            i += 1

        self.step_signal.connect(self.redraw)

        layout = QtGui.QVBoxLayout()
        # layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update(self, step, P):
        if step % self.redraw_period == 0:
            self.step_signal.emit()
            time.sleep(self.update_delay)

    def redraw(self):
        for plot in self.plots:
            plot.redraw()
        self.canvas.draw()

