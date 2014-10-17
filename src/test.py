
import IntOb.NSGAv2 as nsga
import unittest


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
        fronts, ranks = nsga.nonDominatedSort(f, points)

        for i in xrange(0, len(fronts)):
            for j in xrange(0, i):
                for p in fronts[i]:
                    for q in fronts[j]:
                        fp = f(p)
                        fq = f(q)
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

    def test_crowdingDistance(self):
        points = [1, 2, 3, 4]
        vals   = [(3, 3), (1, 5), (2, 4), (0, 6)]
        expected = {
            1: float('+inf'),
            2: 2.0/3 + 2.0/3, 
            3: 2.0/3 + 2.0/3, 
            4: float('+inf'),
        }

        dist = nsga.crowdingDistance(points, vals, [(0, 3), (3,6)])
        # Works, but probably can fail if the implementation of crowdingDistance
        # changes, since I guess it compares floating point values exactly
        self.assertDictEqual(dist, expected)


if __name__ == '__main__':
    unittest.main()
