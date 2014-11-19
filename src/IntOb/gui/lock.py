from contextlib import contextmanager
from PyQt4.QtCore import QReadWriteLock


class RWLock(object):

    def __init__(self):
        self.lock = QReadWriteLock()

    @property
    @contextmanager
    def readLock(self):
       self.lock.lockForRead()
       yield
       self.lock.unlock()

    @property
    @contextmanager
    def writeLock(self):
       self.lock.lockForWrite()
       yield
       self.lock.unlock()
