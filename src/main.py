
import IntOb.NSGAv2 as nsga

vals = {
    (0.5, 0.5),
    (0.3, 0.7),
    (0.5, 0.6)
}

fronts, ranks = nsga.nonDominatedSort(lambda x: x, vals)


for f in fronts:
    print f
