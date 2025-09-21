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

def test_unit_cpuawkward_reduce_min_int16_int16_64_1():
    toptr = [123, 123, 123, 123]
    toptr = (ctypes.c_int16*len(toptr))(*toptr)
    fromptr = [1, 3, 6, 4, 2, 2, 3, 1, 6]
    fromptr = (ctypes.c_int16*len(fromptr))(*fromptr)
    identity = 4
    lenparents = 9
    outlength = 4
    parents = [0, 0, 0, 0, 0, 2, 2, 2, 3]
    parents = (ctypes.c_int64*len(parents))(*parents)
    funcC = getattr(lib, 'awkward_reduce_min_int16_int16_64')
    ret_pass = funcC(toptr, fromptr, parents, lenparents, outlength, identity)
    pytest_toptr = [1, 4, 1, 4]
    assert toptr[:len(pytest_toptr)] == pytest.approx(pytest_toptr)
    assert not ret_pass.str

def test_unit_cpuawkward_reduce_min_int16_int16_64_2():
    toptr = [123, 123, 123, 123]
    toptr = (ctypes.c_int16*len(toptr))(*toptr)
    fromptr = [1, 3, 5, 4, 2, 2, 3, 1, 5]
    fromptr = (ctypes.c_int16*len(fromptr))(*fromptr)
    identity = 4
    lenparents = 9
    outlength = 4
    parents = [0, 0, 0, 0, 0, 2, 2, 2, 3]
    parents = (ctypes.c_int64*len(parents))(*parents)
    funcC = getattr(lib, 'awkward_reduce_min_int16_int16_64')
    ret_pass = funcC(toptr, fromptr, parents, lenparents, outlength, identity)
    pytest_toptr = [1, 4, 1, 4]
    assert toptr[:len(pytest_toptr)] == pytest.approx(pytest_toptr)
    assert not ret_pass.str

