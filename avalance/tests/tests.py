from django.test import TestCase

from tests.services import unique_result_points_validation


# Create your tests here.

class UniqueResultPointsTesting(TestCase): # unique_result_points_validation
    def test_with_full_identical_numbers(self):
        start = [[0, 0], [0, 0], [0, 0], [0, 0]]
        final = [[0, 0], [1, 1], [2, 2], [3, 32767]]
        self.assertEqual(unique_result_points_validation(start, len(start)), final)

    def test_with_equalities_2(self):
        start = [[0, 0], [14, 14], [13, 13], [75, 75]]
        final = [[0, 0], [1, 13], [14, 14], [15, 32767]]
        self.assertEqual(unique_result_points_validation(start, len(start)), final)

    def test_with_equalities(self):
        start = [[0, 0], [23, 23], [13, 13], [75, 76]]
        final = [[0, 0], [1, 13], [14, 14], [15, 32767]]
        self.assertEqual(unique_result_points_validation(start, len(start)), final)

    def test_without_zero(self):
        start = [[41, 63], [55, 23], [65, 13], [75, 105]]
        final = [[0, 23], [24, 41], [42, 55], [56, 32767]]
        self.assertEqual(unique_result_points_validation(start, len(start)), final)

    def test_with_zero(self):
        start = [[0, 63], [55, 23], [65, 13], [75, 105]]
        final = [[0, 13], [14, 23], [24, 55], [56, 32767]]
        self.assertEqual(unique_result_points_validation(start, len(start)), final)

    def test_with_identical_numbers(self):
        start = [[0, 1], [1, 1], [1, 1], [1, 1]]
        final = [[0, 1], [2, 2], [3, 4], [5, 32767]]
        self.assertEqual(unique_result_points_validation(start, len(start)), final)

