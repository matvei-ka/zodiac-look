from collections import Counter

from django.test import SimpleTestCase

from forecasts.stats import build_gradient, top_tied


class TopTiedTests(SimpleTestCase):
    def test_single_leader(self):
        self.assertEqual(top_tied(Counter({1: 3, 2: 1})), ([1], 3))

    def test_tie_returns_all_leaders(self):
        self.assertEqual(top_tied(Counter({2: 2, 1: 2, 3: 1})), ([1, 2], 2))

    def test_empty_counter(self):
        self.assertEqual(top_tied(Counter()), ([], 0))


class BuildGradientTests(SimpleTestCase):
    def test_empty(self):
        self.assertEqual(build_gradient([]), '#eeeeee')

    def test_single_color_is_plain(self):
        self.assertEqual(build_gradient(['#E0B04A']), '#E0B04A')

    def test_several_colors_make_gradient(self):
        self.assertEqual(
            build_gradient(['#E0B04A', '#A8E6CF']),
            'linear-gradient(90deg, #E0B04A, #A8E6CF)',
        )
