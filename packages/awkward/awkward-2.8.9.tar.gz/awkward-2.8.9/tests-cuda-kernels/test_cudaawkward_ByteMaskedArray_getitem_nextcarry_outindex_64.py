# AUTO GENERATED ON 2025-09-20 AT 15:57:04
# DO NOT EDIT BY HAND!
#
# To regenerate file, run
#
#     python dev/generate-tests.py
#

# fmt: off

import cupy
import cupy.testing as cpt
import numpy as np
import pytest

import awkward as ak
import awkward._connect.cuda as ak_cu
from awkward._backends.cupy import CupyBackend

cupy_backend = CupyBackend.instance()

def test_cudaawkward_ByteMaskedArray_getitem_nextcarry_outindex_64_1():
    tocarry = cupy.array([123, 123, 123], dtype=cupy.int64)
    outindex = cupy.array([123, 123, 123], dtype=cupy.int64)
    mask = cupy.array([1, 1, 1, 1, 1], dtype=cupy.int8)
    length = 3
    validwhen = True
    funcC = cupy_backend['awkward_ByteMaskedArray_getitem_nextcarry_outindex', cupy.int64, cupy.int64, cupy.int8]
    funcC(tocarry, outindex, mask, length, validwhen)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [0, 1, 2]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_outindex = [0, 1, 2]
    cpt.assert_allclose(outindex[:len(pytest_outindex)], cupy.array(pytest_outindex))

def test_cudaawkward_ByteMaskedArray_getitem_nextcarry_outindex_64_2():
    tocarry = cupy.array([123, 123, 123], dtype=cupy.int64)
    outindex = cupy.array([123, 123, 123], dtype=cupy.int64)
    mask = cupy.array([0, 0, 0, 0, 0], dtype=cupy.int8)
    length = 3
    validwhen = False
    funcC = cupy_backend['awkward_ByteMaskedArray_getitem_nextcarry_outindex', cupy.int64, cupy.int64, cupy.int8]
    funcC(tocarry, outindex, mask, length, validwhen)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [0, 1, 2]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_outindex = [0, 1, 2]
    cpt.assert_allclose(outindex[:len(pytest_outindex)], cupy.array(pytest_outindex))

def test_cudaawkward_ByteMaskedArray_getitem_nextcarry_outindex_64_3():
    tocarry = cupy.array([123, 123, 123], dtype=cupy.int64)
    outindex = cupy.array([123, 123, 123], dtype=cupy.int64)
    mask = cupy.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], dtype=cupy.int8)
    length = 3
    validwhen = True
    funcC = cupy_backend['awkward_ByteMaskedArray_getitem_nextcarry_outindex', cupy.int64, cupy.int64, cupy.int8]
    funcC(tocarry, outindex, mask, length, validwhen)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [0, 1, 2]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_outindex = [0, 1, 2]
    cpt.assert_allclose(outindex[:len(pytest_outindex)], cupy.array(pytest_outindex))

def test_cudaawkward_ByteMaskedArray_getitem_nextcarry_outindex_64_4():
    tocarry = cupy.array([123, 123, 123], dtype=cupy.int64)
    outindex = cupy.array([123, 123, 123], dtype=cupy.int64)
    mask = cupy.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], dtype=cupy.int8)
    length = 3
    validwhen = True
    funcC = cupy_backend['awkward_ByteMaskedArray_getitem_nextcarry_outindex', cupy.int64, cupy.int64, cupy.int8]
    funcC(tocarry, outindex, mask, length, validwhen)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [0, 1, 2]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_outindex = [0, 1, 2]
    cpt.assert_allclose(outindex[:len(pytest_outindex)], cupy.array(pytest_outindex))

