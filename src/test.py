
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


if __name__ == '__main__':
    unittest.main()
