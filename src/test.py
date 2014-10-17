
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
        pass


if __name__ == '__main__':
    unittest.main()
