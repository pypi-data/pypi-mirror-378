from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
from builtins import super

from nectar.asciichart import AsciiChart


class Testcases(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.curve = [1.2, 4.3, 2.0, -1.3, 6.4, 0.0]

    def test_plot(self):
        ac = AsciiChart(height=3, width=3)
        self.assertEqual(len(ac.canvas), 0)
        ret = ac.plot(self.curve, return_str=True)
        ac.plot(self.curve, return_str=False)
        self.assertTrue(len(ret) > 0)
        ac.clear_data()
        self.assertEqual(len(ac.canvas), 0)

    def test_plot2(self):
        ac = AsciiChart(height=3, width=3)
        ac.clear_data()
        ac.adapt_on_series(self.curve)
        self.assertEqual(ac.maximum, max(self.curve))
        self.assertEqual(ac.minimum, min(self.curve))
        self.assertEqual(ac.n, len(self.curve))
        ac.new_chart()
        ac.add_axis()
        ac.add_curve(self.curve)
