# BSD 3-Clause License; see https://github.com/scikit-hep/awkward/blob/main/LICENSE

from __future__ import annotations

import pytest  # noqa: F401

import awkward as ak


def test():
    array = ak.Array([[[], [], []], []])
    flattened = ak.flatten(array, axis=None)
    assert isinstance(flattened.layout, ak.contents.EmptyArray)
    assert len(flattened) == 0
