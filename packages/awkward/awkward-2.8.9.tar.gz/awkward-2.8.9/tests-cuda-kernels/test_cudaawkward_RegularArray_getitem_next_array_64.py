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

def test_cudaawkward_RegularArray_getitem_next_array_64_1():
    tocarry = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    toadvanced = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    fromarray = cupy.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1], dtype=cupy.int64)
    length = 3
    lenarray = 3
    size = 3
    funcC = cupy_backend['awkward_RegularArray_getitem_next_array', cupy.int64, cupy.int64, cupy.int64]
    funcC(tocarry, toadvanced, fromarray, length, lenarray, size)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [1, 1, 1, 4, 4, 4, 7, 7, 7]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_toadvanced = [0, 1, 2, 0, 1, 2, 0, 1, 2]
    cpt.assert_allclose(toadvanced[:len(pytest_toadvanced)], cupy.array(pytest_toadvanced))

def test_cudaawkward_RegularArray_getitem_next_array_64_2():
    tocarry = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    toadvanced = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    fromarray = cupy.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1], dtype=cupy.int64)
    length = 3
    lenarray = 3
    size = 2
    funcC = cupy_backend['awkward_RegularArray_getitem_next_array', cupy.int64, cupy.int64, cupy.int64]
    funcC(tocarry, toadvanced, fromarray, length, lenarray, size)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [1, 1, 1, 3, 3, 3, 5, 5, 5]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_toadvanced = [0, 1, 2, 0, 1, 2, 0, 1, 2]
    cpt.assert_allclose(toadvanced[:len(pytest_toadvanced)], cupy.array(pytest_toadvanced))

def test_cudaawkward_RegularArray_getitem_next_array_64_3():
    tocarry = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    toadvanced = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    fromarray = cupy.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1], dtype=cupy.int64)
    length = 3
    lenarray = 3
    size = 1
    funcC = cupy_backend['awkward_RegularArray_getitem_next_array', cupy.int64, cupy.int64, cupy.int64]
    funcC(tocarry, toadvanced, fromarray, length, lenarray, size)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [1, 1, 1, 2, 2, 2, 3, 3, 3]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_toadvanced = [0, 1, 2, 0, 1, 2, 0, 1, 2]
    cpt.assert_allclose(toadvanced[:len(pytest_toadvanced)], cupy.array(pytest_toadvanced))

def test_cudaawkward_RegularArray_getitem_next_array_64_4():
    tocarry = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    toadvanced = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    fromarray = cupy.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1], dtype=cupy.int64)
    length = 3
    lenarray = 3
    size = 2
    funcC = cupy_backend['awkward_RegularArray_getitem_next_array', cupy.int64, cupy.int64, cupy.int64]
    funcC(tocarry, toadvanced, fromarray, length, lenarray, size)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [1, 1, 1, 3, 3, 3, 5, 5, 5]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_toadvanced = [0, 1, 2, 0, 1, 2, 0, 1, 2]
    cpt.assert_allclose(toadvanced[:len(pytest_toadvanced)], cupy.array(pytest_toadvanced))

def test_cudaawkward_RegularArray_getitem_next_array_64_5():
    tocarry = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    toadvanced = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    fromarray = cupy.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1], dtype=cupy.int64)
    length = 3
    lenarray = 3
    size = 0
    funcC = cupy_backend['awkward_RegularArray_getitem_next_array', cupy.int64, cupy.int64, cupy.int64]
    funcC(tocarry, toadvanced, fromarray, length, lenarray, size)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [1, 1, 1, 1, 1, 1, 1, 1, 1]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_toadvanced = [0, 1, 2, 0, 1, 2, 0, 1, 2]
    cpt.assert_allclose(toadvanced[:len(pytest_toadvanced)], cupy.array(pytest_toadvanced))

def test_cudaawkward_RegularArray_getitem_next_array_64_6():
    tocarry = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    toadvanced = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    fromarray = cupy.array([2, 3, 3, 4, 5, 5, 5, 5, 5, 6, 7, 8, 10, 11], dtype=cupy.int64)
    length = 3
    lenarray = 3
    size = 3
    funcC = cupy_backend['awkward_RegularArray_getitem_next_array', cupy.int64, cupy.int64, cupy.int64]
    funcC(tocarry, toadvanced, fromarray, length, lenarray, size)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [2, 3, 3, 5, 6, 6, 8, 9, 9]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_toadvanced = [0, 1, 2, 0, 1, 2, 0, 1, 2]
    cpt.assert_allclose(toadvanced[:len(pytest_toadvanced)], cupy.array(pytest_toadvanced))

def test_cudaawkward_RegularArray_getitem_next_array_64_7():
    tocarry = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    toadvanced = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    fromarray = cupy.array([2, 3, 3, 4, 5, 5, 5, 5, 5, 6, 7, 8, 10, 11], dtype=cupy.int64)
    length = 3
    lenarray = 3
    size = 2
    funcC = cupy_backend['awkward_RegularArray_getitem_next_array', cupy.int64, cupy.int64, cupy.int64]
    funcC(tocarry, toadvanced, fromarray, length, lenarray, size)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [2, 3, 3, 4, 5, 5, 6, 7, 7]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_toadvanced = [0, 1, 2, 0, 1, 2, 0, 1, 2]
    cpt.assert_allclose(toadvanced[:len(pytest_toadvanced)], cupy.array(pytest_toadvanced))

def test_cudaawkward_RegularArray_getitem_next_array_64_8():
    tocarry = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    toadvanced = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    fromarray = cupy.array([2, 3, 3, 4, 5, 5, 5, 5, 5, 6, 7, 8, 10, 11], dtype=cupy.int64)
    length = 3
    lenarray = 3
    size = 1
    funcC = cupy_backend['awkward_RegularArray_getitem_next_array', cupy.int64, cupy.int64, cupy.int64]
    funcC(tocarry, toadvanced, fromarray, length, lenarray, size)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [2, 3, 3, 3, 4, 4, 4, 5, 5]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_toadvanced = [0, 1, 2, 0, 1, 2, 0, 1, 2]
    cpt.assert_allclose(toadvanced[:len(pytest_toadvanced)], cupy.array(pytest_toadvanced))

def test_cudaawkward_RegularArray_getitem_next_array_64_9():
    tocarry = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    toadvanced = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    fromarray = cupy.array([2, 3, 3, 4, 5, 5, 5, 5, 5, 6, 7, 8, 10, 11], dtype=cupy.int64)
    length = 3
    lenarray = 3
    size = 2
    funcC = cupy_backend['awkward_RegularArray_getitem_next_array', cupy.int64, cupy.int64, cupy.int64]
    funcC(tocarry, toadvanced, fromarray, length, lenarray, size)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [2, 3, 3, 4, 5, 5, 6, 7, 7]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_toadvanced = [0, 1, 2, 0, 1, 2, 0, 1, 2]
    cpt.assert_allclose(toadvanced[:len(pytest_toadvanced)], cupy.array(pytest_toadvanced))

def test_cudaawkward_RegularArray_getitem_next_array_64_10():
    tocarry = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    toadvanced = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    fromarray = cupy.array([2, 3, 3, 4, 5, 5, 5, 5, 5, 6, 7, 8, 10, 11], dtype=cupy.int64)
    length = 3
    lenarray = 3
    size = 0
    funcC = cupy_backend['awkward_RegularArray_getitem_next_array', cupy.int64, cupy.int64, cupy.int64]
    funcC(tocarry, toadvanced, fromarray, length, lenarray, size)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [2, 3, 3, 2, 3, 3, 2, 3, 3]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_toadvanced = [0, 1, 2, 0, 1, 2, 0, 1, 2]
    cpt.assert_allclose(toadvanced[:len(pytest_toadvanced)], cupy.array(pytest_toadvanced))

def test_cudaawkward_RegularArray_getitem_next_array_64_11():
    tocarry = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    toadvanced = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    fromarray = cupy.array([2, 1, 0, 1, 2, 0, 1, 2, 2, 2, 1, 2, 1, 0, 0, 0, 0], dtype=cupy.int64)
    length = 3
    lenarray = 3
    size = 3
    funcC = cupy_backend['awkward_RegularArray_getitem_next_array', cupy.int64, cupy.int64, cupy.int64]
    funcC(tocarry, toadvanced, fromarray, length, lenarray, size)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [2, 1, 0, 5, 4, 3, 8, 7, 6]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_toadvanced = [0, 1, 2, 0, 1, 2, 0, 1, 2]
    cpt.assert_allclose(toadvanced[:len(pytest_toadvanced)], cupy.array(pytest_toadvanced))

def test_cudaawkward_RegularArray_getitem_next_array_64_12():
    tocarry = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    toadvanced = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    fromarray = cupy.array([2, 1, 0, 1, 2, 0, 1, 2, 2, 2, 1, 2, 1, 0, 0, 0, 0], dtype=cupy.int64)
    length = 3
    lenarray = 3
    size = 2
    funcC = cupy_backend['awkward_RegularArray_getitem_next_array', cupy.int64, cupy.int64, cupy.int64]
    funcC(tocarry, toadvanced, fromarray, length, lenarray, size)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [2, 1, 0, 4, 3, 2, 6, 5, 4]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_toadvanced = [0, 1, 2, 0, 1, 2, 0, 1, 2]
    cpt.assert_allclose(toadvanced[:len(pytest_toadvanced)], cupy.array(pytest_toadvanced))

def test_cudaawkward_RegularArray_getitem_next_array_64_13():
    tocarry = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    toadvanced = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    fromarray = cupy.array([2, 1, 0, 1, 2, 0, 1, 2, 2, 2, 1, 2, 1, 0, 0, 0, 0], dtype=cupy.int64)
    length = 3
    lenarray = 3
    size = 1
    funcC = cupy_backend['awkward_RegularArray_getitem_next_array', cupy.int64, cupy.int64, cupy.int64]
    funcC(tocarry, toadvanced, fromarray, length, lenarray, size)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [2, 1, 0, 3, 2, 1, 4, 3, 2]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_toadvanced = [0, 1, 2, 0, 1, 2, 0, 1, 2]
    cpt.assert_allclose(toadvanced[:len(pytest_toadvanced)], cupy.array(pytest_toadvanced))

def test_cudaawkward_RegularArray_getitem_next_array_64_14():
    tocarry = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    toadvanced = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    fromarray = cupy.array([2, 1, 0, 1, 2, 0, 1, 2, 2, 2, 1, 2, 1, 0, 0, 0, 0], dtype=cupy.int64)
    length = 3
    lenarray = 3
    size = 2
    funcC = cupy_backend['awkward_RegularArray_getitem_next_array', cupy.int64, cupy.int64, cupy.int64]
    funcC(tocarry, toadvanced, fromarray, length, lenarray, size)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [2, 1, 0, 4, 3, 2, 6, 5, 4]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_toadvanced = [0, 1, 2, 0, 1, 2, 0, 1, 2]
    cpt.assert_allclose(toadvanced[:len(pytest_toadvanced)], cupy.array(pytest_toadvanced))

def test_cudaawkward_RegularArray_getitem_next_array_64_15():
    tocarry = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    toadvanced = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    fromarray = cupy.array([2, 1, 0, 1, 2, 0, 1, 2, 2, 2, 1, 2, 1, 0, 0, 0, 0], dtype=cupy.int64)
    length = 3
    lenarray = 3
    size = 0
    funcC = cupy_backend['awkward_RegularArray_getitem_next_array', cupy.int64, cupy.int64, cupy.int64]
    funcC(tocarry, toadvanced, fromarray, length, lenarray, size)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [2, 1, 0, 2, 1, 0, 2, 1, 0]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_toadvanced = [0, 1, 2, 0, 1, 2, 0, 1, 2]
    cpt.assert_allclose(toadvanced[:len(pytest_toadvanced)], cupy.array(pytest_toadvanced))

def test_cudaawkward_RegularArray_getitem_next_array_64_16():
    tocarry = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    toadvanced = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    fromarray = cupy.array([1, 0, 2, 3, 1, 2, 0, 0, 1, 1, 2, 3, 1, 2, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], dtype=cupy.int64)
    length = 3
    lenarray = 3
    size = 3
    funcC = cupy_backend['awkward_RegularArray_getitem_next_array', cupy.int64, cupy.int64, cupy.int64]
    funcC(tocarry, toadvanced, fromarray, length, lenarray, size)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [1, 0, 2, 4, 3, 5, 7, 6, 8]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_toadvanced = [0, 1, 2, 0, 1, 2, 0, 1, 2]
    cpt.assert_allclose(toadvanced[:len(pytest_toadvanced)], cupy.array(pytest_toadvanced))

def test_cudaawkward_RegularArray_getitem_next_array_64_17():
    tocarry = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    toadvanced = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    fromarray = cupy.array([1, 0, 2, 3, 1, 2, 0, 0, 1, 1, 2, 3, 1, 2, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], dtype=cupy.int64)
    length = 3
    lenarray = 3
    size = 2
    funcC = cupy_backend['awkward_RegularArray_getitem_next_array', cupy.int64, cupy.int64, cupy.int64]
    funcC(tocarry, toadvanced, fromarray, length, lenarray, size)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [1, 0, 2, 3, 2, 4, 5, 4, 6]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_toadvanced = [0, 1, 2, 0, 1, 2, 0, 1, 2]
    cpt.assert_allclose(toadvanced[:len(pytest_toadvanced)], cupy.array(pytest_toadvanced))

def test_cudaawkward_RegularArray_getitem_next_array_64_18():
    tocarry = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    toadvanced = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    fromarray = cupy.array([1, 0, 2, 3, 1, 2, 0, 0, 1, 1, 2, 3, 1, 2, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], dtype=cupy.int64)
    length = 3
    lenarray = 3
    size = 1
    funcC = cupy_backend['awkward_RegularArray_getitem_next_array', cupy.int64, cupy.int64, cupy.int64]
    funcC(tocarry, toadvanced, fromarray, length, lenarray, size)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [1, 0, 2, 2, 1, 3, 3, 2, 4]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_toadvanced = [0, 1, 2, 0, 1, 2, 0, 1, 2]
    cpt.assert_allclose(toadvanced[:len(pytest_toadvanced)], cupy.array(pytest_toadvanced))

def test_cudaawkward_RegularArray_getitem_next_array_64_19():
    tocarry = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    toadvanced = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    fromarray = cupy.array([1, 0, 2, 3, 1, 2, 0, 0, 1, 1, 2, 3, 1, 2, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], dtype=cupy.int64)
    length = 3
    lenarray = 3
    size = 2
    funcC = cupy_backend['awkward_RegularArray_getitem_next_array', cupy.int64, cupy.int64, cupy.int64]
    funcC(tocarry, toadvanced, fromarray, length, lenarray, size)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [1, 0, 2, 3, 2, 4, 5, 4, 6]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_toadvanced = [0, 1, 2, 0, 1, 2, 0, 1, 2]
    cpt.assert_allclose(toadvanced[:len(pytest_toadvanced)], cupy.array(pytest_toadvanced))

def test_cudaawkward_RegularArray_getitem_next_array_64_20():
    tocarry = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    toadvanced = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    fromarray = cupy.array([1, 0, 2, 3, 1, 2, 0, 0, 1, 1, 2, 3, 1, 2, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], dtype=cupy.int64)
    length = 3
    lenarray = 3
    size = 0
    funcC = cupy_backend['awkward_RegularArray_getitem_next_array', cupy.int64, cupy.int64, cupy.int64]
    funcC(tocarry, toadvanced, fromarray, length, lenarray, size)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [1, 0, 2, 1, 0, 2, 1, 0, 2]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_toadvanced = [0, 1, 2, 0, 1, 2, 0, 1, 2]
    cpt.assert_allclose(toadvanced[:len(pytest_toadvanced)], cupy.array(pytest_toadvanced))

def test_cudaawkward_RegularArray_getitem_next_array_64_21():
    tocarry = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    toadvanced = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    fromarray = cupy.array([0, 0, 0, 0, 0, 0, 0, 0], dtype=cupy.int64)
    length = 3
    lenarray = 3
    size = 3
    funcC = cupy_backend['awkward_RegularArray_getitem_next_array', cupy.int64, cupy.int64, cupy.int64]
    funcC(tocarry, toadvanced, fromarray, length, lenarray, size)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [0, 0, 0, 3, 3, 3, 6, 6, 6]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_toadvanced = [0, 1, 2, 0, 1, 2, 0, 1, 2]
    cpt.assert_allclose(toadvanced[:len(pytest_toadvanced)], cupy.array(pytest_toadvanced))

def test_cudaawkward_RegularArray_getitem_next_array_64_22():
    tocarry = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    toadvanced = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    fromarray = cupy.array([0, 0, 0, 0, 0, 0, 0, 0], dtype=cupy.int64)
    length = 3
    lenarray = 3
    size = 2
    funcC = cupy_backend['awkward_RegularArray_getitem_next_array', cupy.int64, cupy.int64, cupy.int64]
    funcC(tocarry, toadvanced, fromarray, length, lenarray, size)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [0, 0, 0, 2, 2, 2, 4, 4, 4]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_toadvanced = [0, 1, 2, 0, 1, 2, 0, 1, 2]
    cpt.assert_allclose(toadvanced[:len(pytest_toadvanced)], cupy.array(pytest_toadvanced))

def test_cudaawkward_RegularArray_getitem_next_array_64_23():
    tocarry = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    toadvanced = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    fromarray = cupy.array([0, 0, 0, 0, 0, 0, 0, 0], dtype=cupy.int64)
    length = 3
    lenarray = 3
    size = 1
    funcC = cupy_backend['awkward_RegularArray_getitem_next_array', cupy.int64, cupy.int64, cupy.int64]
    funcC(tocarry, toadvanced, fromarray, length, lenarray, size)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [0, 0, 0, 1, 1, 1, 2, 2, 2]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_toadvanced = [0, 1, 2, 0, 1, 2, 0, 1, 2]
    cpt.assert_allclose(toadvanced[:len(pytest_toadvanced)], cupy.array(pytest_toadvanced))

def test_cudaawkward_RegularArray_getitem_next_array_64_24():
    tocarry = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    toadvanced = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    fromarray = cupy.array([0, 0, 0, 0, 0, 0, 0, 0], dtype=cupy.int64)
    length = 3
    lenarray = 3
    size = 2
    funcC = cupy_backend['awkward_RegularArray_getitem_next_array', cupy.int64, cupy.int64, cupy.int64]
    funcC(tocarry, toadvanced, fromarray, length, lenarray, size)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [0, 0, 0, 2, 2, 2, 4, 4, 4]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_toadvanced = [0, 1, 2, 0, 1, 2, 0, 1, 2]
    cpt.assert_allclose(toadvanced[:len(pytest_toadvanced)], cupy.array(pytest_toadvanced))

def test_cudaawkward_RegularArray_getitem_next_array_64_25():
    tocarry = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    toadvanced = cupy.array([123, 123, 123, 123, 123, 123, 123, 123, 123], dtype=cupy.int64)
    fromarray = cupy.array([0, 0, 0, 0, 0, 0, 0, 0], dtype=cupy.int64)
    length = 3
    lenarray = 3
    size = 0
    funcC = cupy_backend['awkward_RegularArray_getitem_next_array', cupy.int64, cupy.int64, cupy.int64]
    funcC(tocarry, toadvanced, fromarray, length, lenarray, size)

    try:
        ak_cu.synchronize_cuda()
    except:
        pytest.fail("This test case shouldn't have raised an error")
    pytest_tocarry = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    cpt.assert_allclose(tocarry[:len(pytest_tocarry)], cupy.array(pytest_tocarry))
    pytest_toadvanced = [0, 1, 2, 0, 1, 2, 0, 1, 2]
    cpt.assert_allclose(toadvanced[:len(pytest_toadvanced)], cupy.array(pytest_toadvanced))

