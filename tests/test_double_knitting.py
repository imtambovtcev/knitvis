import unittest
import numpy as np
import matplotlib.pyplot as plt
from knitvis.double_knitting import DoubleKnittingCanvas
from knitvis.chart import KnittingChart


class TestDoubleKnittingCanvas(unittest.TestCase):
    def setUp(self):
        """Set up test patterns for use in multiple test cases."""
        # Create simple test patterns
        self.small_pattern = np.array([
            [True, False, True],
            [False, True, False],
            [True, False, True]
        ], dtype=bool)

        # Create a more complex pattern for comprehensive testing
        self.complex_pattern = np.zeros((10, 10), dtype=bool)
        self.complex_pattern[2:8, 2:8] = True  # Create a square
        self.complex_pattern[4:6, 4:6] = False  # Create a hole in the middle

        # Define custom colors for testing
        self.front_color = (255, 0, 0)  # Red
        self.back_color = (0, 0, 255)   # Blue

    def test_init_basic(self):
        """Test basic initialization with default parameters."""
        canvas = DoubleKnittingCanvas(self.small_pattern)

        # Check shape and pattern properties
        self.assertEqual(canvas.shape, self.small_pattern.shape)
        np.testing.assert_array_equal(canvas.front, self.small_pattern)
        np.testing.assert_array_equal(canvas.back, ~self.small_pattern)

        # Check default colors
        np.testing.assert_array_equal(
            canvas.front_color, np.array([255, 255, 255]))
        np.testing.assert_array_equal(canvas.back_color, np.array([0, 0, 0]))

        # Verify charts were created
        self.assertIsInstance(canvas.front_chart, KnittingChart)
        self.assertIsInstance(canvas.back_chart, KnittingChart)

    def test_init_custom_colors(self):
        """Test initialization with custom colors."""
        canvas = DoubleKnittingCanvas(
            self.small_pattern,
            front_color=self.front_color,
            back_color=self.back_color
        )

        np.testing.assert_array_equal(
            canvas.front_color, np.array(self.front_color))
        np.testing.assert_array_equal(
            canvas.back_color, np.array(self.back_color))

    def test_init_custom_back_pattern(self):
        """Test initialization with a custom back pattern."""
        back_pattern = np.array([
            [False, True, False],
            [True, False, True],
            [False, True, False]
        ], dtype=bool)

        canvas = DoubleKnittingCanvas(self.small_pattern, back_pattern)

        np.testing.assert_array_equal(canvas.front, self.small_pattern)
        np.testing.assert_array_equal(canvas.back, back_pattern)

    def test_from_pattern_no_resize(self):
        """Test from_pattern class method without resizing."""
        canvas = DoubleKnittingCanvas.from_pattern(self.small_pattern)

        np.testing.assert_array_equal(canvas.front, self.small_pattern)
        self.assertEqual(canvas.shape, self.small_pattern.shape)

    def test_from_pattern_with_resize(self):
        """Test from_pattern class method with resizing."""
        target_size = (6, 6)
        canvas = DoubleKnittingCanvas.from_pattern(
            self.small_pattern, target_size)

        self.assertEqual(canvas.shape, target_size)

        # Check that the pattern was properly interpolated
        # The center point should still be True
        self.assertTrue(canvas.front[3, 3])

    def test_from_pattern_with_custom_colors(self):
        """Test from_pattern with custom colors."""
        canvas = DoubleKnittingCanvas.from_pattern(
            self.small_pattern,
            front_color=self.front_color,
            back_color=self.back_color
        )

        np.testing.assert_array_equal(
            canvas.front_color, np.array(self.front_color))
        np.testing.assert_array_equal(
            canvas.back_color, np.array(self.back_color))

    def test_create_knitting_pattern(self):
        """Test the creation of the interleaved knitting pattern."""
        canvas = DoubleKnittingCanvas(self.small_pattern)
        pattern = canvas.create_knitting_pattern()

        # Check that the pattern has the correct shape (width doubled)
        self.assertEqual(
            pattern.shape, (self.small_pattern.shape[0], self.small_pattern.shape[1] * 2))

        # Check that the pattern has alternating front and back stitches
        for row in range(pattern.shape[0]):
            for col in range(0, pattern.shape[1], 2):
                self.assertEqual(
                    pattern[row, col], canvas.front_chart.pattern[row, col // 2])
                self.assertEqual(
                    pattern[row, col + 1], canvas.back_chart.pattern[row, col // 2])

    def test_get_knitting_chart(self):
        """Test getting a complete knitting chart for the double-sided pattern."""
        canvas = DoubleKnittingCanvas(self.small_pattern)
        chart = canvas.get_knitting_chart()

        self.assertIsInstance(chart, KnittingChart)
        self.assertEqual(
            chart.pattern.shape, (self.small_pattern.shape[0], self.small_pattern.shape[1] * 2))

    def test_display_methods(self):
        """Test that display methods return valid matplotlib figures."""
        canvas = DoubleKnittingCanvas(self.small_pattern)

        # Test display() method
        fig1, fig2 = canvas.display()
        self.assertIsInstance(fig1, plt.Figure)
        self.assertIsInstance(fig2, plt.Figure)

        # Test display_knitting_pattern() method
        fig = canvas.display_knitting_pattern()
        self.assertIsInstance(fig, plt.Figure)

        # Test plot_full_pattern() method
        figs = canvas.plot_full_pattern()
        self.assertIsInstance(figs, list)
        for fig in figs:
            self.assertIsInstance(fig, plt.Figure)

    def test_complex_pattern(self):
        """Test with a more complex pattern to ensure proper handling."""
        canvas = DoubleKnittingCanvas(self.complex_pattern)

        # Verify shapes
        self.assertEqual(canvas.shape, self.complex_pattern.shape)

        # Test display methods with complex pattern
        fig1, fig2 = canvas.display()
        self.assertIsInstance(fig1, plt.Figure)
        self.assertIsInstance(fig2, plt.Figure)

        # Check that the knitting pattern has the expected shape
        pattern = canvas.create_knitting_pattern()
        self.assertEqual(
            pattern.shape, (self.complex_pattern.shape[0], self.complex_pattern.shape[1] * 2))

        # Close all figures to prevent memory issues
        plt.close('all')


if __name__ == '__main__':
    unittest.main()
