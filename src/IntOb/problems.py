
from itertools import repeat
from math import sqrt, sin, pi


g = lambda x: 1 + 9 * sum(x[1:]) / float(len(x) - 1)


def ZDT1():
    F = (
        lambda x: x[0],
        lambda x: g(x) * (1 - sqrt(x[0] / g(x)))
    )
    n = 30
    bounds = tuple(repeat((0, 1), n))
    volume = 2./3 + 9
    ranges = [(0, 1), (0, 10)]
    return (F, bounds, ranges, volume)


def ZDT2():
    F = (
        lambda x: x[0],
        lambda x: g(x) * (1 - (x[0] / g(x))**2)
    )
    n = 30
    bounds = tuple(repeat((0, 1), n))
    volume = 1./3 + 9
    ranges = [(0, 1), (0, 10)]
    return (F, bounds, ranges, volume)


def ZDT3():
    F = (
        lambda x: x[0],
        lambda x: 0.5 * (1 + g(x) * (1 - sqrt(x[0]/g(x)) - x[0]/g(x) * sin(10*pi*x[0])))
    )
    n = 30
    bounds = tuple(repeat((0, 1), n))
    ranges = [(0, 1), (0, 10)]
    return (F, bounds, ranges, 1)


def ZDT1_3D():
    F = (
        lambda x: x[0],
        lambda x: g(x) * (1 - sqrt(x[0] / g(x)))
    )
    n = 3
    bounds = tuple(repeat((0, 1), n))
    volume = 2./3 + 9
    ranges = [(0, 1), (0, 10)]
    return (F, bounds, ranges, volume)


def ZDT2_3D():
    F = (
        lambda x: x[0],
        lambda x: g(x) * (1 - (x[0] / g(x))**2)
    )
    n = 3
    bounds = tuple(repeat((0, 1), n))
    volume = 1./3 + 9
    ranges = [(0, 1), (0, 10)]
    return (F, bounds, ranges, volume)


def ZDT3_3D():
    F = (
        lambda x: x[0],
        lambda x: 0.5 * (1 + g(x) * (1 - sqrt(x[0]/g(x)) - x[0]/g(x) * sin(10*pi*x[0])))
    )
    n = 3
    bounds = tuple(repeat((0, 1), n))
    ranges = [(0, 1), (0, 10)]
    return (F, bounds, ranges, 1)
