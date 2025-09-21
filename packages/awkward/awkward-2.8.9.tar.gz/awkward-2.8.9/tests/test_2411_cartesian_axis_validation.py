# BSD 3-Clause License; see https://github.com/scikit-hep/awkward/blob/main/LICENSE

from __future__ import annotations

import pytest

import awkward as ak
from awkward.errors import AxisError


def test_simple():
    left = ak.Array([1, 2, 3])
    right = ak.Array([["lambda", "sigma", "eta", "phi"], ["delta"]])
    pair = ak.cartesian([left, right], axis=0)
    assert pair.ndim == 1
    assert pair.tolist() == [
        (1, ["lambda", "sigma", "eta", "phi"]),
        (1, ["delta"]),
        (2, ["lambda", "sigma", "eta", "phi"]),
        (2, ["delta"]),
        (3, ["lambda", "sigma", "eta", "phi"]),
        (3, ["delta"]),
    ]


def test_out_of_bounds():
    left = ak.Array([1, 2, 3])
    right = ak.Array([["lambda", "sigma", "eta", "phi"], ["delta"]])
    with pytest.raises(AxisError):
        ak.cartesian([left, right], axis=2)
