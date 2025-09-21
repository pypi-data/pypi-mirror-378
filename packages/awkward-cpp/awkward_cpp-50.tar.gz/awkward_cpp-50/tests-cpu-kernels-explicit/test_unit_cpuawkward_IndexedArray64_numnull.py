# AUTO GENERATED ON 2025-09-20 AT 15:57:04
# DO NOT EDIT BY HAND!
#
# To regenerate file, run
#
#     python dev/generate-tests.py
#

# fmt: off

import ctypes
import numpy as np
import pytest

from awkward_cpp.cpu_kernels import lib

def test_unit_cpuawkward_IndexedArray64_numnull_1():
    numnull = [123]
    numnull = (ctypes.c_int64*len(numnull))(*numnull)
    fromindex = []
    fromindex = (ctypes.c_int64*len(fromindex))(*fromindex)
    lenindex = 0
    funcC = getattr(lib, 'awkward_IndexedArray64_numnull')
    ret_pass = funcC(numnull, fromindex, lenindex)
    pytest_numnull = [0]
    assert numnull[:len(pytest_numnull)] == pytest.approx(pytest_numnull)
    assert not ret_pass.str

def test_unit_cpuawkward_IndexedArray64_numnull_2():
    numnull = [123]
    numnull = (ctypes.c_int64*len(numnull))(*numnull)
    fromindex = [1]
    fromindex = (ctypes.c_int64*len(fromindex))(*fromindex)
    lenindex = 1
    funcC = getattr(lib, 'awkward_IndexedArray64_numnull')
    ret_pass = funcC(numnull, fromindex, lenindex)
    pytest_numnull = [0]
    assert numnull[:len(pytest_numnull)] == pytest.approx(pytest_numnull)
    assert not ret_pass.str

def test_unit_cpuawkward_IndexedArray64_numnull_3():
    numnull = [123]
    numnull = (ctypes.c_int64*len(numnull))(*numnull)
    fromindex = [-1]
    fromindex = (ctypes.c_int64*len(fromindex))(*fromindex)
    lenindex = 1
    funcC = getattr(lib, 'awkward_IndexedArray64_numnull')
    ret_pass = funcC(numnull, fromindex, lenindex)
    pytest_numnull = [1]
    assert numnull[:len(pytest_numnull)] == pytest.approx(pytest_numnull)
    assert not ret_pass.str

def test_unit_cpuawkward_IndexedArray64_numnull_4():
    numnull = [123]
    numnull = (ctypes.c_int64*len(numnull))(*numnull)
    fromindex = [-1, -1, -1, -1]
    fromindex = (ctypes.c_int64*len(fromindex))(*fromindex)
    lenindex = 4
    funcC = getattr(lib, 'awkward_IndexedArray64_numnull')
    ret_pass = funcC(numnull, fromindex, lenindex)
    pytest_numnull = [4]
    assert numnull[:len(pytest_numnull)] == pytest.approx(pytest_numnull)
    assert not ret_pass.str

def test_unit_cpuawkward_IndexedArray64_numnull_5():
    numnull = [123]
    numnull = (ctypes.c_int64*len(numnull))(*numnull)
    fromindex = [0, -1, 2, -1, -1, -1, -1]
    fromindex = (ctypes.c_int64*len(fromindex))(*fromindex)
    lenindex = 7
    funcC = getattr(lib, 'awkward_IndexedArray64_numnull')
    ret_pass = funcC(numnull, fromindex, lenindex)
    pytest_numnull = [5]
    assert numnull[:len(pytest_numnull)] == pytest.approx(pytest_numnull)
    assert not ret_pass.str

def test_unit_cpuawkward_IndexedArray64_numnull_6():
    numnull = [123]
    numnull = (ctypes.c_int64*len(numnull))(*numnull)
    fromindex = [0, 1]
    fromindex = (ctypes.c_int64*len(fromindex))(*fromindex)
    lenindex = 2
    funcC = getattr(lib, 'awkward_IndexedArray64_numnull')
    ret_pass = funcC(numnull, fromindex, lenindex)
    pytest_numnull = [0]
    assert numnull[:len(pytest_numnull)] == pytest.approx(pytest_numnull)
    assert not ret_pass.str

def test_unit_cpuawkward_IndexedArray64_numnull_7():
    numnull = [123]
    numnull = (ctypes.c_int64*len(numnull))(*numnull)
    fromindex = [0, 1, 2, 3]
    fromindex = (ctypes.c_int64*len(fromindex))(*fromindex)
    lenindex = 4
    funcC = getattr(lib, 'awkward_IndexedArray64_numnull')
    ret_pass = funcC(numnull, fromindex, lenindex)
    pytest_numnull = [0]
    assert numnull[:len(pytest_numnull)] == pytest.approx(pytest_numnull)
    assert not ret_pass.str

def test_unit_cpuawkward_IndexedArray64_numnull_8():
    numnull = [123]
    numnull = (ctypes.c_int64*len(numnull))(*numnull)
    fromindex = [0, 1, 2, 3, 4, 5, 6]
    fromindex = (ctypes.c_int64*len(fromindex))(*fromindex)
    lenindex = 7
    funcC = getattr(lib, 'awkward_IndexedArray64_numnull')
    ret_pass = funcC(numnull, fromindex, lenindex)
    pytest_numnull = [0]
    assert numnull[:len(pytest_numnull)] == pytest.approx(pytest_numnull)
    assert not ret_pass.str

def test_unit_cpuawkward_IndexedArray64_numnull_9():
    numnull = [123]
    numnull = (ctypes.c_int64*len(numnull))(*numnull)
    fromindex = [1, 2]
    fromindex = (ctypes.c_int64*len(fromindex))(*fromindex)
    lenindex = 2
    funcC = getattr(lib, 'awkward_IndexedArray64_numnull')
    ret_pass = funcC(numnull, fromindex, lenindex)
    pytest_numnull = [0]
    assert numnull[:len(pytest_numnull)] == pytest.approx(pytest_numnull)
    assert not ret_pass.str

def test_unit_cpuawkward_IndexedArray64_numnull_10():
    numnull = [123]
    numnull = (ctypes.c_int64*len(numnull))(*numnull)
    fromindex = [1, 2, 3]
    fromindex = (ctypes.c_int64*len(fromindex))(*fromindex)
    lenindex = 3
    funcC = getattr(lib, 'awkward_IndexedArray64_numnull')
    ret_pass = funcC(numnull, fromindex, lenindex)
    pytest_numnull = [0]
    assert numnull[:len(pytest_numnull)] == pytest.approx(pytest_numnull)
    assert not ret_pass.str

def test_unit_cpuawkward_IndexedArray64_numnull_11():
    numnull = [123]
    numnull = (ctypes.c_int64*len(numnull))(*numnull)
    fromindex = [1, 2, 3, 4]
    fromindex = (ctypes.c_int64*len(fromindex))(*fromindex)
    lenindex = 4
    funcC = getattr(lib, 'awkward_IndexedArray64_numnull')
    ret_pass = funcC(numnull, fromindex, lenindex)
    pytest_numnull = [0]
    assert numnull[:len(pytest_numnull)] == pytest.approx(pytest_numnull)
    assert not ret_pass.str

def test_unit_cpuawkward_IndexedArray64_numnull_12():
    numnull = [123]
    numnull = (ctypes.c_int64*len(numnull))(*numnull)
    fromindex = [2, 3]
    fromindex = (ctypes.c_int64*len(fromindex))(*fromindex)
    lenindex = 2
    funcC = getattr(lib, 'awkward_IndexedArray64_numnull')
    ret_pass = funcC(numnull, fromindex, lenindex)
    pytest_numnull = [0]
    assert numnull[:len(pytest_numnull)] == pytest.approx(pytest_numnull)
    assert not ret_pass.str

def test_unit_cpuawkward_IndexedArray64_numnull_13():
    numnull = [123]
    numnull = (ctypes.c_int64*len(numnull))(*numnull)
    fromindex = [2, 3, 4]
    fromindex = (ctypes.c_int64*len(fromindex))(*fromindex)
    lenindex = 3
    funcC = getattr(lib, 'awkward_IndexedArray64_numnull')
    ret_pass = funcC(numnull, fromindex, lenindex)
    pytest_numnull = [0]
    assert numnull[:len(pytest_numnull)] == pytest.approx(pytest_numnull)
    assert not ret_pass.str

def test_unit_cpuawkward_IndexedArray64_numnull_14():
    numnull = [123]
    numnull = (ctypes.c_int64*len(numnull))(*numnull)
    fromindex = [3, 2, 1, 0]
    fromindex = (ctypes.c_int64*len(fromindex))(*fromindex)
    lenindex = 4
    funcC = getattr(lib, 'awkward_IndexedArray64_numnull')
    ret_pass = funcC(numnull, fromindex, lenindex)
    pytest_numnull = [0]
    assert numnull[:len(pytest_numnull)] == pytest.approx(pytest_numnull)
    assert not ret_pass.str

def test_unit_cpuawkward_IndexedArray64_numnull_15():
    numnull = [123]
    numnull = (ctypes.c_int64*len(numnull))(*numnull)
    fromindex = [3, 4]
    fromindex = (ctypes.c_int64*len(fromindex))(*fromindex)
    lenindex = 2
    funcC = getattr(lib, 'awkward_IndexedArray64_numnull')
    ret_pass = funcC(numnull, fromindex, lenindex)
    pytest_numnull = [0]
    assert numnull[:len(pytest_numnull)] == pytest.approx(pytest_numnull)
    assert not ret_pass.str

def test_unit_cpuawkward_IndexedArray64_numnull_16():
    numnull = [123]
    numnull = (ctypes.c_int64*len(numnull))(*numnull)
    fromindex = [4, 3, 2, 1, 0]
    fromindex = (ctypes.c_int64*len(fromindex))(*fromindex)
    lenindex = 5
    funcC = getattr(lib, 'awkward_IndexedArray64_numnull')
    ret_pass = funcC(numnull, fromindex, lenindex)
    pytest_numnull = [0]
    assert numnull[:len(pytest_numnull)] == pytest.approx(pytest_numnull)
    assert not ret_pass.str

def test_unit_cpuawkward_IndexedArray64_numnull_17():
    numnull = [123]
    numnull = (ctypes.c_int64*len(numnull))(*numnull)
    fromindex = [5, 2, 4, 1, 3, 0]
    fromindex = (ctypes.c_int64*len(fromindex))(*fromindex)
    lenindex = 6
    funcC = getattr(lib, 'awkward_IndexedArray64_numnull')
    ret_pass = funcC(numnull, fromindex, lenindex)
    pytest_numnull = [0]
    assert numnull[:len(pytest_numnull)] == pytest.approx(pytest_numnull)
    assert not ret_pass.str

def test_unit_cpuawkward_IndexedArray64_numnull_18():
    numnull = [123]
    numnull = (ctypes.c_int64*len(numnull))(*numnull)
    fromindex = [5, 4, 3, 2, 1, 0]
    fromindex = (ctypes.c_int64*len(fromindex))(*fromindex)
    lenindex = 6
    funcC = getattr(lib, 'awkward_IndexedArray64_numnull')
    ret_pass = funcC(numnull, fromindex, lenindex)
    pytest_numnull = [0]
    assert numnull[:len(pytest_numnull)] == pytest.approx(pytest_numnull)
    assert not ret_pass.str

