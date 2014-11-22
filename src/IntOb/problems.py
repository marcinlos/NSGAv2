
from itertools import repeat
import numpy as np
from math import sqrt, sin, pi


g = lambda x: 1 + 9 * sum(x[1:]) / float(len(x) - 1)

class Problem(object):

    @property
    def refpoint(self):
        return tuple(r[1] for r in self.ranges)


class ZDT1(Problem):

    def __init__(self, n=30):
        self.bounds = tuple(repeat((0, 1), n))
        self.volume = 9 + 2.0 / 3
        self.ranges = [(0, 1), (0, 10)]

        self.front = self.__generate_front(100)

    def __generate_front(self, count):
        x = np.linspace(0, 1, count)
        y = 1 - x ** 0.5
        return [(x, y)]

    def evaluate(self, x):
        k = g(x)
        y = k * (1 - sqrt(x[0] / k))
        return (x[0], y)


class ZDT2(Problem):

    def __init__(self, n=30):
        self.bounds = tuple(repeat((0, 1), n))
        self.volume = 9 + 1.0 / 3
        self.ranges = [(0, 1), (0, 10)]

        self.front = self.__generate_front(100)

    def __generate_front(self, count):
        x = np.linspace(0, 1, count)
        y = 1 - x ** 2
        return [(x, y)]

    def evaluate(self, x):
        k = g(x)
        y = k * (1 - (x[0] / k) ** 2)
        return (x[0], y)


class ZDT3(Problem):

    def __init__(self, n=30):
        self.bounds = tuple(repeat((0, 1), n))
        self.volume = 9 + 0.52170099153
        self.ranges = [(0, 1), (0, 10)]

        self.front = self.__generate_front(20)

    def __generate_front(self, count):
        ranges = [
            (0, 0.0830015439),
            (0.1822287280, 0.2577623634),
            (0.4093136748, 0.4538821041),
            (0.6183967944, 0.6525117038),
            (0.8233317983, 0.8518328654),
        ]
        parts = []
        for a, b in ranges:
            xs = np.linspace(a, b, count)
            ys = [0.5 * (2 - sqrt(x) - x * sin(10 * pi * x)) for x in xs]
            parts.append((xs, ys))

        return parts

    def evaluate(self, x):
        k = g(x)
        y = 0.5 * (1 + k * (1 - sqrt(x[0]/k)) - x[0]/k * sin(10*pi*x[0]))
        return (x[0], y)

