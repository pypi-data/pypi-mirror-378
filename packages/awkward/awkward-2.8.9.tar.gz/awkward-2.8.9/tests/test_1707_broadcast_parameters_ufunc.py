# BSD 3-Clause License; see https://github.com/scikit-hep/awkward/blob/main/LICENSE

from __future__ import annotations

import numpy as np
import pytest  # noqa: F401

import awkward as ak


def test_numpy_1d():
    x = ak.Array(
        ak.contents.NumpyArray(
            np.asarray([1, 2, 3]),
            parameters={"attrs": {"not": "hashable"}, "name": "x"},
        )
    )
    y = ak.Array(
        ak.contents.NumpyArray(
            np.asarray([1, 2, 3]),
            parameters={"attrs": {"not": "hashable"}, "name": "y"},
        )
    )
    result = x + y
    assert ak.parameters(result) == {"attrs": {"not": "hashable"}}


def test_numpy_2d():
    x = ak.Array(
        ak.contents.NumpyArray(
            np.asarray([[1, 2, 3]]),
            parameters={"attrs": {"not": "hashable"}, "name": "x"},
        )
    )
    y = ak.Array(
        ak.contents.NumpyArray(
            np.asarray([[1, 2, 3]]),
            parameters={"attrs": {"not": "hashable"}, "name": "y"},
        )
    )
    result = x + y
    assert ak.parameters(result) == {"attrs": {"not": "hashable"}}


def test_regular_array_numpy_1d():
    x = ak.Array(
        ak.contents.RegularArray(
            ak.contents.NumpyArray(
                np.asarray([1, 2, 3, 4, 5, 6]),
                parameters={"attrs": {"not": "hashable"}, "name": "x"},
            ),
            3,
        )
    )
    y = ak.Array(
        ak.contents.RegularArray(
            ak.contents.NumpyArray(
                np.asarray([7, 8, 9, 10, 11, 12]),
                parameters={"attrs": {"not": "hashable"}, "name": "y"},
            ),
            3,
        )
    )
    result = x + y
    assert result.layout.parameters == {}
    assert result.layout.content.parameters == {"attrs": {"not": "hashable"}}
