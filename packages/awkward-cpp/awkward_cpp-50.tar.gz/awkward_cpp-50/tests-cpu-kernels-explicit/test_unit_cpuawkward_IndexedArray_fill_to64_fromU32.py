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

def test_unit_cpuawkward_IndexedArray_fill_to64_fromU32_1():
    toindex = []
    toindex = (ctypes.c_int64*len(toindex))(*toindex)
    base = 0
    fromindex = []
    fromindex = (ctypes.c_uint32*len(fromindex))(*fromindex)
    length = 0
    toindexoffset = 0
    funcC = getattr(lib, 'awkward_IndexedArray_fill_to64_fromU32')
    ret_pass = funcC(toindex, toindexoffset, fromindex, length, base)
    pytest_toindex = []
    assert toindex[:len(pytest_toindex)] == pytest.approx(pytest_toindex)
    assert not ret_pass.str

def test_unit_cpuawkward_IndexedArray_fill_to64_fromU32_2():
    toindex = [123, 123, 123]
    toindex = (ctypes.c_int64*len(toindex))(*toindex)
    base = 0
    fromindex = [0, 1, 2]
    fromindex = (ctypes.c_uint32*len(fromindex))(*fromindex)
    length = 3
    toindexoffset = 0
    funcC = getattr(lib, 'awkward_IndexedArray_fill_to64_fromU32')
    ret_pass = funcC(toindex, toindexoffset, fromindex, length, base)
    pytest_toindex = [0, 1, 2]
    assert toindex[:len(pytest_toindex)] == pytest.approx(pytest_toindex)
    assert not ret_pass.str

