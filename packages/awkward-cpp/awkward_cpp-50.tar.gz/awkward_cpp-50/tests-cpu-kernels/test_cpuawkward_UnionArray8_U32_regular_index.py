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

def test_cpuawkward_UnionArray8_U32_regular_index_1():
    toindex = [123, 123, 123]
    toindex = (ctypes.c_uint32*len(toindex))(*toindex)
    current = [123, 123, 123]
    current = (ctypes.c_uint32*len(current))(*current)
    size = 3
    fromtags = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    fromtags = (ctypes.c_int8*len(fromtags))(*fromtags)
    length = 3
    funcC = getattr(lib, 'awkward_UnionArray8_U32_regular_index')
    ret_pass = funcC(toindex, current, size, fromtags, length)
    pytest_toindex = [0, 1, 2]
    pytest_current = [3, 0, 0]
    assert not ret_pass.str

def test_cpuawkward_UnionArray8_U32_regular_index_2():
    toindex = [123, 123, 123]
    toindex = (ctypes.c_uint32*len(toindex))(*toindex)
    current = [123, 123, 123]
    current = (ctypes.c_uint32*len(current))(*current)
    size = 3
    fromtags = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    fromtags = (ctypes.c_int8*len(fromtags))(*fromtags)
    length = 3
    funcC = getattr(lib, 'awkward_UnionArray8_U32_regular_index')
    ret_pass = funcC(toindex, current, size, fromtags, length)
    pytest_toindex = [0, 1, 2]
    pytest_current = [0, 3, 0]
    assert not ret_pass.str

def test_cpuawkward_UnionArray8_U32_regular_index_3():
    toindex = [123, 123, 123]
    toindex = (ctypes.c_uint32*len(toindex))(*toindex)
    current = [123, 123, 123]
    current = (ctypes.c_uint32*len(current))(*current)
    size = 3
    fromtags = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    fromtags = (ctypes.c_int8*len(fromtags))(*fromtags)
    length = 3
    funcC = getattr(lib, 'awkward_UnionArray8_U32_regular_index')
    ret_pass = funcC(toindex, current, size, fromtags, length)
    pytest_toindex = [0, 1, 2]
    pytest_current = [0, 3, 0]
    assert not ret_pass.str

def test_cpuawkward_UnionArray8_U32_regular_index_4():
    toindex = [123, 123, 123]
    toindex = (ctypes.c_uint32*len(toindex))(*toindex)
    current = [123, 123, 123]
    current = (ctypes.c_uint32*len(current))(*current)
    size = 3
    fromtags = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    fromtags = (ctypes.c_int8*len(fromtags))(*fromtags)
    length = 3
    funcC = getattr(lib, 'awkward_UnionArray8_U32_regular_index')
    ret_pass = funcC(toindex, current, size, fromtags, length)
    pytest_toindex = [0, 1, 2]
    pytest_current = [3, 0, 0]
    assert not ret_pass.str

def test_cpuawkward_UnionArray8_U32_regular_index_5():
    toindex = [123, 123, 123]
    toindex = (ctypes.c_uint32*len(toindex))(*toindex)
    current = [123, 123, 123]
    current = (ctypes.c_uint32*len(current))(*current)
    size = 3
    fromtags = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    fromtags = (ctypes.c_int8*len(fromtags))(*fromtags)
    length = 3
    funcC = getattr(lib, 'awkward_UnionArray8_U32_regular_index')
    ret_pass = funcC(toindex, current, size, fromtags, length)
    pytest_toindex = [0, 1, 2]
    pytest_current = [3, 0, 0]
    assert not ret_pass.str

