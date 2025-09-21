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

def test_unit_cpuawkward_UnionArray64_regular_index_getsize_1():
    size = [123]
    size = (ctypes.c_int64*len(size))(*size)
    fromtags = []
    fromtags = (ctypes.c_int64*len(fromtags))(*fromtags)
    length = 0
    funcC = getattr(lib, 'awkward_UnionArray64_regular_index_getsize')
    ret_pass = funcC(size, fromtags, length)
    pytest_size = [1]
    assert size[:len(pytest_size)] == pytest.approx(pytest_size)
    assert not ret_pass.str

def test_unit_cpuawkward_UnionArray64_regular_index_getsize_2():
    size = [123]
    size = (ctypes.c_int64*len(size))(*size)
    fromtags = [0]
    fromtags = (ctypes.c_int64*len(fromtags))(*fromtags)
    length = 1
    funcC = getattr(lib, 'awkward_UnionArray64_regular_index_getsize')
    ret_pass = funcC(size, fromtags, length)
    pytest_size = [1]
    assert size[:len(pytest_size)] == pytest.approx(pytest_size)
    assert not ret_pass.str

def test_unit_cpuawkward_UnionArray64_regular_index_getsize_3():
    size = [123]
    size = (ctypes.c_int64*len(size))(*size)
    fromtags = [-1]
    fromtags = (ctypes.c_int64*len(fromtags))(*fromtags)
    length = 1
    funcC = getattr(lib, 'awkward_UnionArray64_regular_index_getsize')
    ret_pass = funcC(size, fromtags, length)
    pytest_size = [1]
    assert size[:len(pytest_size)] == pytest.approx(pytest_size)
    assert not ret_pass.str

def test_unit_cpuawkward_UnionArray64_regular_index_getsize_4():
    size = [123]
    size = (ctypes.c_int64*len(size))(*size)
    fromtags = [0, 1, 0, 1, 0, 1]
    fromtags = (ctypes.c_int64*len(fromtags))(*fromtags)
    length = 6
    funcC = getattr(lib, 'awkward_UnionArray64_regular_index_getsize')
    ret_pass = funcC(size, fromtags, length)
    pytest_size = [2]
    assert size[:len(pytest_size)] == pytest.approx(pytest_size)
    assert not ret_pass.str

def test_unit_cpuawkward_UnionArray64_regular_index_getsize_5():
    size = [123]
    size = (ctypes.c_int64*len(size))(*size)
    fromtags = [1, 0, 1, 1]
    fromtags = (ctypes.c_int64*len(fromtags))(*fromtags)
    length = 4
    funcC = getattr(lib, 'awkward_UnionArray64_regular_index_getsize')
    ret_pass = funcC(size, fromtags, length)
    pytest_size = [2]
    assert size[:len(pytest_size)] == pytest.approx(pytest_size)
    assert not ret_pass.str

def test_unit_cpuawkward_UnionArray64_regular_index_getsize_6():
    size = [123]
    size = (ctypes.c_int64*len(size))(*size)
    fromtags = [1, 1, 0, 0, 1, 0, 1, 1]
    fromtags = (ctypes.c_int64*len(fromtags))(*fromtags)
    length = 8
    funcC = getattr(lib, 'awkward_UnionArray64_regular_index_getsize')
    ret_pass = funcC(size, fromtags, length)
    pytest_size = [2]
    assert size[:len(pytest_size)] == pytest.approx(pytest_size)
    assert not ret_pass.str

