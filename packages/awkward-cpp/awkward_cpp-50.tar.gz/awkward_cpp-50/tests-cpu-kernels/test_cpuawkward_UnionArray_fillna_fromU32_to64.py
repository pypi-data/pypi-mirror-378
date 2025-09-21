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

def test_cpuawkward_UnionArray_fillna_fromU32_to64_1():
    toindex = [123, 123, 123]
    toindex = (ctypes.c_int64*len(toindex))(*toindex)
    fromindex = [1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1]
    fromindex = (ctypes.c_uint32*len(fromindex))(*fromindex)
    length = 3
    funcC = getattr(lib, 'awkward_UnionArray_fillna_fromU32_to64')
    ret_pass = funcC(toindex, fromindex, length)
    pytest_toindex = [1, 0, 0]
    assert not ret_pass.str

def test_cpuawkward_UnionArray_fillna_fromU32_to64_2():
    toindex = [123, 123, 123]
    toindex = (ctypes.c_int64*len(toindex))(*toindex)
    fromindex = [1, 2, 2, 3, 0, 2, 0, 2, 1, 1]
    fromindex = (ctypes.c_uint32*len(fromindex))(*fromindex)
    length = 3
    funcC = getattr(lib, 'awkward_UnionArray_fillna_fromU32_to64')
    ret_pass = funcC(toindex, fromindex, length)
    pytest_toindex = [1, 2, 2]
    assert not ret_pass.str

def test_cpuawkward_UnionArray_fillna_fromU32_to64_3():
    toindex = [123, 123, 123]
    toindex = (ctypes.c_int64*len(toindex))(*toindex)
    fromindex = [1, 3, 0, 3, 5, 2, 0, 2, 1, 1]
    fromindex = (ctypes.c_uint32*len(fromindex))(*fromindex)
    length = 3
    funcC = getattr(lib, 'awkward_UnionArray_fillna_fromU32_to64')
    ret_pass = funcC(toindex, fromindex, length)
    pytest_toindex = [1, 3, 0]
    assert not ret_pass.str

def test_cpuawkward_UnionArray_fillna_fromU32_to64_4():
    toindex = [123, 123, 123]
    toindex = (ctypes.c_int64*len(toindex))(*toindex)
    fromindex = [1, 4, 2, 3, 1, 2, 3, 1, 4, 3, 2, 1, 3, 2, 4, 5, 1, 2, 3, 4, 5]
    fromindex = (ctypes.c_uint32*len(fromindex))(*fromindex)
    length = 3
    funcC = getattr(lib, 'awkward_UnionArray_fillna_fromU32_to64')
    ret_pass = funcC(toindex, fromindex, length)
    pytest_toindex = [1, 4, 2]
    assert not ret_pass.str

def test_cpuawkward_UnionArray_fillna_fromU32_to64_5():
    toindex = [123, 123, 123]
    toindex = (ctypes.c_int64*len(toindex))(*toindex)
    fromindex = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    fromindex = (ctypes.c_uint32*len(fromindex))(*fromindex)
    length = 3
    funcC = getattr(lib, 'awkward_UnionArray_fillna_fromU32_to64')
    ret_pass = funcC(toindex, fromindex, length)
    pytest_toindex = [0, 0, 0]
    assert not ret_pass.str

