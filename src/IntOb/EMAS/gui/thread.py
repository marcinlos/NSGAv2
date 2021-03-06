
from PyQt4 import QtCore


class ComputationThread(QtCore.QThread):

    def __init__(self, emas, steps, refpoint, callback):
        super(QtCore.QThread, self).__init__()
        self.emas = emas
        self.steps = steps
        self.refpoint = refpoint
        self.callback = callback

    def run(self):
        self.emas.optimize(self.steps, self.callback)

