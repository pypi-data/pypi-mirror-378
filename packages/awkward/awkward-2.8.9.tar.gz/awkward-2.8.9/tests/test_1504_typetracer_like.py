# BSD 3-Clause License; see https://github.com/scikit-hep/awkward/blob/main/LICENSE

from __future__ import annotations

import numpy as np
import pytest

import awkward as ak
from awkward._nplikes.typetracer import TypeTracer

typetracer = TypeTracer.instance()


@pytest.mark.parametrize("dtype", [np.float64, np.int64, np.uint8, None])
@pytest.mark.parametrize("like_dtype", [np.float64, np.int64, np.uint8, None])
def test_ones_like(dtype, like_dtype):
    array = ak.contents.numpyarray.NumpyArray(
        np.array([99, 88, 77, 66, 66], dtype=dtype)
    )
    ones = ak.ones_like(array.to_typetracer(), dtype=like_dtype, highlevel=False)
    assert ones.to_typetracer().shape == array.shape
    assert ones.to_typetracer().dtype == like_dtype or array.dtype


@pytest.mark.parametrize("dtype", [np.float64, np.int64, np.uint8, None])
@pytest.mark.parametrize("like_dtype", [np.float64, np.int64, np.uint8, None])
def test_zeros_like(dtype, like_dtype):
    array = ak.contents.numpyarray.NumpyArray(
        np.array([99, 88, 77, 66, 66], dtype=dtype)
    )

    full = ak.zeros_like(array.to_typetracer(), dtype=like_dtype, highlevel=False)
    assert full.to_typetracer().shape == array.shape
    assert full.to_typetracer().dtype == like_dtype or array.dtype


@pytest.mark.parametrize("dtype", [np.float64, np.int64, np.uint8, None])
@pytest.mark.parametrize("like_dtype", [np.float64, np.int64, np.uint8, None])
@pytest.mark.parametrize("value", [1.0, -20, np.iinfo(np.int64).max])
def test_full_like(dtype, like_dtype, value):
    array = ak.contents.numpyarray.NumpyArray(
        np.array([99, 88, 77, 66, 66], dtype=dtype)
    )
    full = ak.full_like(array.to_typetracer(), value, dtype=like_dtype, highlevel=False)
    assert full.to_typetracer().shape == array.shape
    assert full.to_typetracer().dtype == like_dtype or array.dtype
