import dataclasses
import os
import pathlib
import struct
import typing

import numpy as np


_BIF6_HEADER = struct.Struct('<6s3H')
_BIF6_MAGIC = b'\x00\x00BIF6'
_MZ_BIN_HEADER = struct.Struct('<I3f')


@dataclasses.dataclass
class BIF6Interval:
    """A single interval in a BIF6 file."""

    id: int
    """A unique identifier for this interval."""

    mz_lower: float
    """The lower bound of the m/z interval for this image."""

    mz_middle: float
    """The middle of the m/z interval for this image."""

    mz_upper: float
    """The upper bound of the m/z interval for this image."""

    image: np.ndarray
    """The image data for this interval, with its shape in [height, width] order."""

    def is_tic_image(self) -> bool:
        """Check if this interval is a TIC (total-ion-count) image.

        The first interval in a BIF6 file should probably be a TIC image."""
        return self.id == 0


class BIF6FileParser:
    path: pathlib.Path
    _file: typing.BinaryIO

    _n_intervals: int
    _n_x_pixels: int
    _n_y_pixels: int

    def __init__(self, file: typing.Union[os.PathLike, str]):
        self.path = pathlib.Path(file)
        self._file = open(file, "rb")
        header = self._file.read(_BIF6_HEADER.size)
        assert len(header) == _BIF6_HEADER.size, 'Invalid BIF6 header. Not a BIF6 file?'
        magic, invernals, x_pixels, y_pixels = _BIF6_HEADER.unpack(header)
        assert magic == _BIF6_MAGIC, 'Invalid BIF6 magic. Not a BIF6 file?'
        self._n_intervals = invernals
        self._n_x_pixels = x_pixels
        self._n_y_pixels = y_pixels

    @property
    def interval_count(self) -> int:
        """The number of intervals in the BIF6 file.

        Each interval contains an image for the m/z in a certain interval.
        See BIF6Interval for more information."""
        return self._n_intervals

    @property
    def image_size(self) -> typing.Tuple[int, int]:
        """The size of the images in the BIF6 file.

        Similar to ndarray.shape, this is in [height, width] order."""
        return self._n_y_pixels, self._n_x_pixels

    def close(self):
        """Close the BIF6 file.

        This will be automatically called when the iterator is exhausted.
        But you can call it manually if you want to free up resources."""
        self._file.close()

    def __iter__(self):
        return self

    def __next__(self) -> BIF6Interval:
        """Get the next interval in the BIF6 file.

        Returns:
            A BIF6Interval object.
        """

        n_pixels = self._n_x_pixels * self._n_y_pixels
        pixel_data_size = n_pixels * 4
        interval_data = self._file.read(_MZ_BIN_HEADER.size + pixel_data_size)

        if len(interval_data) == 0:
            self.close()
            raise StopIteration

        assert len(interval_data) == _MZ_BIN_HEADER.size + pixel_data_size, 'Incomplete BIF6 interval'
        interval_id, mz_lower, mz_middle, mz_upper = _MZ_BIN_HEADER.unpack(
            interval_data[:_MZ_BIN_HEADER.size]
        )
        image = np.frombuffer(
            interval_data[_MZ_BIN_HEADER.size:],
            dtype=np.dtype(np.uint32).newbyteorder('<'),
        ).reshape((self._n_x_pixels, self._n_y_pixels))

        return BIF6Interval(
            id=interval_id,
            mz_lower=mz_lower,
            mz_middle=mz_middle,
            mz_upper=mz_upper,
            image=image,
        )

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc_value, _traceback):
        self.close()
        return False


def parse_bif6(file: typing.Union[os.PathLike, str]) -> BIF6FileParser:
    """Parse a BIF6 file.

    Args:
        file: The BIF6 file to parse.

    Returns:
        A BIF6File object.
    """

    return BIF6FileParser(file)
