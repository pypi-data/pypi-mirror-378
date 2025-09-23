from __future__ import annotations

import io
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from kw6 import header, settings, types
from kw6.position import Position, PositionHeader


class Reader(BaseModel):
    """
    Used to iterate over images in a kw6 file.

    Example:

    .. code-block:: python

        from pathlib import Path
        import kw6

        path = Path("...")

        for position in kw6.Reader.from_path(path):
            for camera in position.cameras:
                camera.image.save(
                    f"{position.header.frame_index}_{camera.header.camera_index}.png"
                )
    """

    stream: Any
    cached_byte_positions: Dict[int, int]
    initial_frame_index: int
    n_bytes: int
    file_version: str

    class Config:
        arbitrary_types_allowed = True

    @staticmethod
    def from_file_like(
        file: Any,
        header_file: Optional[Any] = None,
        raise_on_version_mismatch: bool = True,
    ) -> "Reader":
        """
        Create a Reader instance from a file-like object.

        Args:
            file: A file-like object containing the kw6 data.
            header_file: An optional file-like object containing header information.

        Returns:
            A Reader instance.

        Raises:
            ValueError: If the file version is unexpected.
        """
        version = file.read(settings.N_BYTES_VERSION).decode().strip()
        if version != "KW6FileClassVer1.0" and raise_on_version_mismatch:
            raise ValueError(f"Unexpected file version {version}")

        initial_position_header = PositionHeader.from_stream_(file)

        cached_byte_positions = (
            dict() if header_file is None else header.positions(header_file.read())
        )
        cached_byte_positions[initial_position_header.frame_index] = (
            settings.N_BYTES_VERSION
        )

        file.seek(0, io.SEEK_END)
        n_bytes = file.tell()

        return Reader(
            stream=file,
            cached_byte_positions=cached_byte_positions,
            initial_frame_index=initial_position_header.frame_index,
            n_bytes=n_bytes,
            file_version=version,
        )

    @staticmethod
    def from_path(
        path: Union[str, Path],
        header_path: Optional[Union[str, Path]] = None,
        raise_on_version_mismatch: bool = True,
    ) -> "Reader":
        """
        Create a Reader instance from a file path.

        Args:
            path: Path to the kw6 file. Can be a string or Path object.
            header_path: Optional path to the header file. Can be a string or Path object.

        Returns:
            A Reader instance.
        """
        path = Path(path) if isinstance(path, str) else path
        header_path = Path(header_path) if isinstance(header_path, str) else header_path

        return Reader.from_file_like(
            file=path.open("rb"),
            header_file=None if header_path is None else header_path.open("rb"),
            raise_on_version_mismatch=raise_on_version_mismatch,
        )

    def __iter__(self) -> Iterable[Position]:
        """Iterate over all positions and cameras in the file"""
        self.stream.seek(settings.N_BYTES_VERSION)
        while self.stream.peek(1) != b"":
            byte_position = self.stream.tell()
            position = Position.from_stream_(self.stream)
            self.cached_byte_positions[position.header.frame_index] = byte_position
            yield position

    def __len__(self) -> int:
        """
        Calculate the length of the kw6 file.

        Returns:
            The number of frames in the file.

        Raises:
            Exception: If unable to calculate length due to corruption or after too many iterations.
        """
        for iteration in range(1, 10000 + 1):
            assumptuous_length = self.assumptuous_length()
            assumptuous_max_frame_index = (
                self.initial_frame_index + assumptuous_length - 1
            )
            try:
                max_position = self[assumptuous_max_frame_index]
                max_byte_position = self.cached_byte_positions[
                    max_position.header.frame_index
                ]
                if (
                    self.n_bytes
                    == max_byte_position + max_position.header.n_frame_bytes
                ):
                    return assumptuous_length
            except IndexError:
                pass

            if assumptuous_length == self.assumptuous_length():
                raise Exception(
                    "Unable to calculate length, probably due to corruption"
                )

        raise Exception(f"Failed to calculate length after {iteration} iterations")

    def assumptuous_length(self, from_frame_index: Optional[int] = None) -> int:
        """
        Calculate an assumptuous length of the kw6 file.

        Args:
            from_frame_index: The frame index to start calculation from.

        Returns:
            An estimated number of frames in the file.
        """
        if from_frame_index is None:
            from_frame_index = max(self.cached_byte_positions.keys())

        from_position = self[from_frame_index]
        max_byte_position = self.cached_byte_positions[from_frame_index]
        n_frames = (
            self.n_bytes - max_byte_position
        ) / from_position.header.n_frame_bytes

        return int(
            n_frames + from_position.header.frame_index - self.initial_frame_index
        )

    def __getitem__(
        self, indices_or_slice: Union[int, slice, Iterable[int]]
    ) -> Union[Position, List[Position]]:
        """
        Access a position by frame index. Supports slicing and array indexing

        Example:

        .. code-block:: python

            from pathlib import Path
            import kw6

            reader = kw6.Reader.from_path(Path("..."))
            position = reader[10]
            positions = reader[10:20]
            positions = reader[[5, 7, 9]]

        Args:
            indices_or_slice: An integer, slice, or iterable of integers representing frame indices.

        Returns:
            A single Position or a list of Positions.

        Raises:
            ValueError: If slice start or stop is None.
            TypeError: If the input type is not supported for indexing.
        """
        if isinstance(indices_or_slice, int):
            positions = self.position_(indices_or_slice)

        elif isinstance(indices_or_slice, slice):
            if indices_or_slice.start is None or indices_or_slice.stop is None:
                raise ValueError("NoneType not supported for slice start or stop")
            else:
                positions = [
                    self.position_(index)
                    for index in range(
                        indices_or_slice.start,
                        indices_or_slice.stop,
                        (
                            indices_or_slice.step
                            if indices_or_slice.step is not None
                            else 1
                        ),
                    )
                ]

        elif isinstance(indices_or_slice, Iterable):
            positions = [self.position_(index) for index in indices_or_slice]

        else:
            raise TypeError(f"Unindexable type {type(indices_or_slice)}")

        return positions

    def position_(self, frame_index: types.FRAME_INDEX) -> Position:
        """
        Retrieve a Position for a given frame index.

        Args:
            frame_index: The frame index to retrieve.

        Returns:
            A Position object for the given frame index.

        Raises:
            IndexError: If the frame index is negative, smaller than the initial frame index,
                        or if unable to find the requested frame.
        """
        if frame_index < 0:
            raise IndexError("Negative indexing not supported")

        if frame_index < self.initial_frame_index:
            raise IndexError(
                f"Frame index {frame_index} is smaller than the first frame "
                f"index {self.initial_frame_index}"
            )

        step_size_confidence = -1
        for _ in range(10000000):
            from_frame_index = self.closest_stored_frame_index(frame_index)
            if step_size_confidence == -1:
                to_frame_index = frame_index
            else:
                to_frame_index = from_frame_index + step_size_confidence

            try:
                byte_position = self.assumptuous_byte_position(
                    to_frame_index, from_frame_index
                )
                self.stream.seek(byte_position)
                position_header = PositionHeader.from_stream_(self.stream)
                if position_header.frame_index != to_frame_index:
                    if step_size_confidence == 1:
                        raise IndexError(
                            f"Unexpected frame index {position_header.frame_index} "
                            f"when moving a single step from {from_frame_index}"
                        )
                    step_size_confidence = 1
                    continue
                self.cached_byte_positions[position_header.frame_index] = byte_position
                step_size_confidence *= 10

                if position_header.frame_index == frame_index:
                    self.stream.seek(byte_position)
                    return Position.from_stream_(self.stream)
            except Exception:
                if step_size_confidence == 1:
                    raise IndexError(
                        f"Unable to move a single frame index from "
                        f"{from_frame_index} to {to_frame_index}"
                    )
                step_size_confidence = 1

        raise IndexError(f"Unable to find {frame_index}")

    def assumptuous_byte_position(
        self,
        frame_index: types.FRAME_INDEX,
        from_frame_index: types.FRAME_INDEX,
    ) -> int:
        """
        Calculate an assumptuous byte position for a given frame index.

        Args:
            frame_index: The target frame index.
            from_frame_index: The frame index to start calculation from.

        Returns:
            The calculated byte position.

        Raises:
            IndexError: If the calculated byte position is negative or greater than the file size.
        """
        self.stream.seek(self.cached_byte_positions[from_frame_index])
        from_byte_position = self.stream.tell()
        from_position_header = PositionHeader.from_stream_(self.stream)

        byte_position = (
            from_position_header.n_frame_bytes * (frame_index - from_frame_index)
            + from_byte_position
        )
        if byte_position < 0:
            raise IndexError(
                f"Extrapolating to frame index {frame_index} from {from_frame_index}"
                "gave a negative byte position"
            )
        elif byte_position > self.n_bytes:
            raise IndexError(
                f"Extrapolating to frame index {frame_index} from {from_frame_index}"
                f"gave a byte position greater than the size of the file {self.n_bytes}"
            )

        return byte_position

    def closest_stored_frame_index(self, frame_index: types.FRAME_INDEX) -> int:
        """
        Find the closest stored frame index that is less than or equal to the given frame index.

        Args:
            frame_index: The target frame index.

        Returns:
            The closest stored frame index.
        """
        earlier_frame_indices = [
            cached_frame_index
            for cached_frame_index in self.cached_byte_positions.keys()
            if cached_frame_index <= frame_index
        ]
        return max(earlier_frame_indices)

    def __del__(self):
        """Close the stream when the Reader object is deleted."""
        self.stream.close()


def test_file_not_found():
    import pytest

    with pytest.raises(FileNotFoundError):
        Reader.from_path("fail").version


def test_iter():
    import pytest

    max_position = 0
    with pytest.raises(ValueError):
        for position in Reader.from_path("tests/constant_corrupt.kw6"):
            max_position = position.header.frame_index

    assert max_position >= 50


def test_indexing():
    reader = Reader.from_path("tests/constant_corrupt.kw6")
    assert reader[10].header.frame_index == 10
    assert reader[10:21][-1].header.frame_index == 20
    assert reader[[11, 5, 9]][1].header.frame_index == 5


def test_indexing_dynamic():
    reader = Reader.from_path("tests/dynamic.kw6")
    assert reader[2090].header.frame_index == 2090
    assert reader[2070].header.frame_index == 2070
    assert reader[2100].header.frame_index == 2100


def test_indexing_dynamic_header():
    reader = Reader.from_path("tests/dynamic.kw6", "tests/dynamic.hdr")
    assert reader[2090].header.frame_index == 2090
    assert reader[2070].header.frame_index == 2070
    assert reader[2100].header.frame_index == 2100


def test_length():
    reader = Reader.from_path("tests/constant.kw6")

    max_frame_index = 0
    for position in reader:
        max_frame_index = position.header.frame_index

    assert (
        max_frame_index == reader.assumptuous_length() + reader.initial_frame_index - 1
    )
    assert max_frame_index == len(reader) + reader.initial_frame_index - 1


def test_length_constant_corrupt():
    import pytest

    reader = Reader.from_path("tests/constant_corrupt.kw6")

    with pytest.raises(Exception):
        len(reader)


def test_length_dynamic():
    reader = Reader.from_path("tests/dynamic.kw6")

    max_frame_index = None
    for position in reader:
        assert (
            max_frame_index is None
            or position.header.frame_index == max_frame_index + 1
        )
        max_frame_index = position.header.frame_index

    assert max_frame_index == len(reader) + reader.initial_frame_index - 1


def test_read_2121():
    reader = Reader.from_path("tests/dynamic.kw6")

    position2121 = reader[2121]

    for position in reader:
        if position.header.frame_index == 2121:
            break

    assert position2121 == position


def test_stream_already_ended():
    reader = Reader.from_path("tests/dynamic.kw6")
    len(reader)

    position2121 = reader[2121]
    assert position2121.header.frame_index == 2121


def test_stream_already_ended2():
    reader = Reader.from_path("tests/dynamic.kw6")
    reader[2163]

    position2121 = reader[2121]
    assert position2121.header.frame_index == 2121


def test_last_twice():
    reader = Reader.from_path("tests/dynamic.kw6")
    reader[2163]
    reader[2163]


def test_read_too_far_dynamic():
    import pytest

    reader = Reader.from_path("tests/dynamic.kw6")

    with pytest.raises(IndexError):
        reader[10000]


def test_read_too_far_constant():
    import pytest

    reader = Reader.from_path("tests/constant.kw6")

    with pytest.raises(IndexError):
        reader[10000]
