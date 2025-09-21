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

def test_unit_cpuawkward_IndexedArrayU32_ranges_next_64_1():
    tostarts = []
    tostarts = (ctypes.c_int64*len(tostarts))(*tostarts)
    tostops = []
    tostops = (ctypes.c_int64*len(tostops))(*tostops)
    tolength = [123]
    tolength = (ctypes.c_int64*len(tolength))(*tolength)
    index = []
    index = (ctypes.c_uint32*len(index))(*index)
    fromstarts = []
    fromstarts = (ctypes.c_int64*len(fromstarts))(*fromstarts)
    fromstops = []
    fromstops = (ctypes.c_int64*len(fromstops))(*fromstops)
    length = 0
    funcC = getattr(lib, 'awkward_IndexedArrayU32_ranges_next_64')
    ret_pass = funcC(index, fromstarts, fromstops, length, tostarts, tostops, tolength)
    pytest_tostarts = []
    assert tostarts[:len(pytest_tostarts)] == pytest.approx(pytest_tostarts)
    pytest_tostops = []
    assert tostops[:len(pytest_tostops)] == pytest.approx(pytest_tostops)
    pytest_tolength = [0]
    assert tolength[:len(pytest_tolength)] == pytest.approx(pytest_tolength)
    assert not ret_pass.str

def test_unit_cpuawkward_IndexedArrayU32_ranges_next_64_2():
    tostarts = [123]
    tostarts = (ctypes.c_int64*len(tostarts))(*tostarts)
    tostops = [123]
    tostops = (ctypes.c_int64*len(tostops))(*tostops)
    tolength = [123]
    tolength = (ctypes.c_int64*len(tolength))(*tolength)
    index = [0, 1]
    index = (ctypes.c_uint32*len(index))(*index)
    fromstarts = [0]
    fromstarts = (ctypes.c_int64*len(fromstarts))(*fromstarts)
    fromstops = [2]
    fromstops = (ctypes.c_int64*len(fromstops))(*fromstops)
    length = 1
    funcC = getattr(lib, 'awkward_IndexedArrayU32_ranges_next_64')
    ret_pass = funcC(index, fromstarts, fromstops, length, tostarts, tostops, tolength)
    pytest_tostarts = [0]
    assert tostarts[:len(pytest_tostarts)] == pytest.approx(pytest_tostarts)
    pytest_tostops = [2]
    assert tostops[:len(pytest_tostops)] == pytest.approx(pytest_tostops)
    pytest_tolength = [2]
    assert tolength[:len(pytest_tolength)] == pytest.approx(pytest_tolength)
    assert not ret_pass.str

def test_unit_cpuawkward_IndexedArrayU32_ranges_next_64_3():
    tostarts = [123, 123]
    tostarts = (ctypes.c_int64*len(tostarts))(*tostarts)
    tostops = [123, 123]
    tostops = (ctypes.c_int64*len(tostops))(*tostops)
    tolength = [123]
    tolength = (ctypes.c_int64*len(tolength))(*tolength)
    index = [0, 1, 2]
    index = (ctypes.c_uint32*len(index))(*index)
    fromstarts = [0, 2]
    fromstarts = (ctypes.c_int64*len(fromstarts))(*fromstarts)
    fromstops = [2, 3]
    fromstops = (ctypes.c_int64*len(fromstops))(*fromstops)
    length = 2
    funcC = getattr(lib, 'awkward_IndexedArrayU32_ranges_next_64')
    ret_pass = funcC(index, fromstarts, fromstops, length, tostarts, tostops, tolength)
    pytest_tostarts = [0, 2]
    assert tostarts[:len(pytest_tostarts)] == pytest.approx(pytest_tostarts)
    pytest_tostops = [2, 3]
    assert tostops[:len(pytest_tostops)] == pytest.approx(pytest_tostops)
    pytest_tolength = [3]
    assert tolength[:len(pytest_tolength)] == pytest.approx(pytest_tolength)
    assert not ret_pass.str

