import unittest

import numpy as np
from pybif6 import (
    parse_bif6,
    BIF6FileParser,
    BIF6Interval
)

class TestBIF6(unittest.TestCase):
    def test_bif6(self):
        """Test BIF6 parsing"""
        with parse_bif6(
            '/path/to/my/local/test/file.bif6',
        ) as parser:
            self.assertIsInstance(parser, BIF6FileParser)
            height, width = parser.image_size
            interval: BIF6Interval = next(parser)
            self.assertIsInstance(interval, BIF6Interval)
            self.assertEqual(interval.image.shape, (height, width))
            self.assertEqual(interval.image.dtype, np.uint32)
            self.assertTrue(interval.is_tic_image())

            interval = next(parser)
            self.assertIsInstance(interval, BIF6Interval)
            self.assertEqual(interval.image.shape, (height, width))
            self.assertEqual(interval.image.dtype, np.uint32)
            self.assertFalse(interval.is_tic_image())


if __name__ == '__main__':
    unittest.main()

