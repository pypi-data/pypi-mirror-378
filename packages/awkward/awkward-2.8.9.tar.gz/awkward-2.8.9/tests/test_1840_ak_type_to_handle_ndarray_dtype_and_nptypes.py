# BSD 3-Clause License; see https://github.com/scikit-hep/awkward/blob/main/LICENSE

from __future__ import annotations

import numpy as np
import pytest  # noqa: F401

import awkward as ak


def test_array():
    array = np.random.random(size=512).astype(dtype=np.float64)
    assert ak.type(array) == ak.types.ArrayType(ak.types.NumpyType("float64"), 512)


def test_dtype():
    assert ak.type(np.dtype(np.float64)) == ak.types.ScalarType(
        ak.types.NumpyType("float64")
    )


def test_type_instance():
    assert ak.type(np.float64(10.0)) == ak.types.ScalarType(
        ak.types.NumpyType("float64")
    )
