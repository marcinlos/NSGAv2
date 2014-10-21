
import IntOb.NSGAv2 as nsga
import unittest
from itertools import repeat


class Test(unittest.TestCase):


    def test_dominates_donminatesWhenGreaterAtOnePosition(self):
        a = [1, 2, 3]
        b = [1, 3, 3]
        self.assertTrue(nsga.dominates(a, b))


    def test_dominates_dominatesWhenGreaterAtAllPositions(self):
        a = [1, 2, 3]
        b = [7, 3, 4]
        self.assertTrue(nsga.dominates(a, b))


    def test_dominates_notDominatesWhenLessAtOnePosition(self):
        a = [1, 2, 3]
        b = [7, 1, 9]
        self.assertFalse(nsga.dominates(a, b))


    def test_nonDominatedSort(self):
        n = 10
        points = nsga.randomPopulation(n, [(0,1), (2,3)])
        f = lambda (a, b) : (a + b, a * b)
        vals = map(f, points)
        fronts, ranks = nsga.nonDominatedSort(points, vals)
        valueMap = dict(zip(points, vals))

        for i in xrange(0, len(fronts)):
            for j in xrange(0, i):
                for p in fronts[i]:
                    for q in fronts[j]:
                        fp = valueMap[p]
                        fq = valueMap[q]
                        self.assertFalse(nsga.dominates(fp, fq))
        for p in points:
            rank = ranks[p]
            self.assertIn(p, fronts[rank])


    def test_sortByValue(self):
        points = [10, 20, 30, 40, 50]
        vals   = [3, 5, 1, 2, 4]
        expected = [(30, 1), (40, 2), (10, 3), (50, 4), (20, 5)]

        ps = nsga.sortByValue(points, vals)
        self.assertSequenceEqual(ps, expected)


    def test_volBetween(self):
        a = (1, 5, 2)
        b = (3, 2, 1)
        self.assertEqual(nsga.volBetween(a, b), nsga.volBetween(b, a))
        self.assertEqual(nsga.volBetween(a, b), 6)


    #def test_crowdingDistance(self):
    #    points = [1, 2, 3, 4]
    #    vals   = [(3, 3), (1, 5), (2, 4), (0, 6)]
    #    expected = {
    #        1: float('+inf'),
    #        2: 2.0/3 + 2.0/3, 
    #        3: 2.0/3 + 2.0/3, 
    #        4: float('+inf'),
    #    }

    #    dist = nsga.crowdingDistance(points, vals, [(0, 3), (3,6)])
    #    # Works, but probably can fail if the implementation of crowdingDistance
    #    # changes, since I guess it compares floating point values exactly
    #    self.assertDictEqual(dist, expected)


    def test_mutation(self):
        a = (0.3, 0.7)
        bounds = [(0, 1), (0.6, 0.8)]
        max_changes = (0.5, 0.2)

        for _ in xrange(100):
            b = nsga.mutation(a, 1, bounds, max_changes)
            for i, (x, y) in enumerate(zip(a, b)):
                self.assertLessEqual(abs(x - y), max_changes[i])
                m, M = bounds[i]
                self.assertGreaterEqual(y, m)
                self.assertLessEqual(y, M)


    def test_findSmallestGreater(self):
        x = (0.3, 1)
        xs = [0.2, 2, 1.4, 4, 0, 1.1, 1, 0.3, 1.2]
        xs = zip(repeat(1), xs)
        self.assertEqual(nsga.findSmallestGreater(x, xs, 1), 1.1)


    def test_hypervolume_simple(self):
        p = (1, 1)
        xs = [(0.5, 0.5)]
        self.assertEqual(nsga.hypervolume(p, xs), 0.25)


    def test_hypervolume(self):
        p = (1, 1)
        xs = [(0.5, 0.5), (0, 0.75), (0.75, 0)]
        self.assertEqual(nsga.hypervolume(p, xs), 0.5)


    def test_hypervolume_withOverlap(self):
        p = (1, 1)
        xs = [(0.5, 0.5), (0.75, 0.75)]
        self.assertEqual(nsga.hypervolume(p, xs), 0.25)


    def test_hypervolume_edges(self):
        p = (1, 1)
        xs = [(0.5, 0.5), (0.5, 0.0), (0.0, 0.5), (0.25, 0.5)]
        self.assertEqual(nsga.hypervolume(p, xs), 0.75)


if __name__ == '__main__':
    unittest.main()

