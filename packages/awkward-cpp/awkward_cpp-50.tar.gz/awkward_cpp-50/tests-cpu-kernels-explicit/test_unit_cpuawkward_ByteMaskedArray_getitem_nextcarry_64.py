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

def test_unit_cpuawkward_ByteMaskedArray_getitem_nextcarry_64_1():
    tocarry = []
    tocarry = (ctypes.c_int64*len(tocarry))(*tocarry)
    length = 0
    mask = []
    mask = (ctypes.c_int8*len(mask))(*mask)
    validwhen = False
    funcC = getattr(lib, 'awkward_ByteMaskedArray_getitem_nextcarry_64')
    ret_pass = funcC(tocarry, mask, length, validwhen)
    pytest_tocarry = []
    assert tocarry[:len(pytest_tocarry)] == pytest.approx(pytest_tocarry)
    assert not ret_pass.str

def test_unit_cpuawkward_ByteMaskedArray_getitem_nextcarry_64_2():
    tocarry = [123, 123]
    tocarry = (ctypes.c_int64*len(tocarry))(*tocarry)
    length = 2
    mask = [0, 0]
    mask = (ctypes.c_int8*len(mask))(*mask)
    validwhen = False
    funcC = getattr(lib, 'awkward_ByteMaskedArray_getitem_nextcarry_64')
    ret_pass = funcC(tocarry, mask, length, validwhen)
    pytest_tocarry = [0, 1]
    assert tocarry[:len(pytest_tocarry)] == pytest.approx(pytest_tocarry)
    assert not ret_pass.str

def test_unit_cpuawkward_ByteMaskedArray_getitem_nextcarry_64_3():
    tocarry = [123, 123, 123]
    tocarry = (ctypes.c_int64*len(tocarry))(*tocarry)
    length = 5
    mask = [0, 0, 1, 1, 0]
    mask = (ctypes.c_int8*len(mask))(*mask)
    validwhen = False
    funcC = getattr(lib, 'awkward_ByteMaskedArray_getitem_nextcarry_64')
    ret_pass = funcC(tocarry, mask, length, validwhen)
    pytest_tocarry = [0, 1, 4]
    assert tocarry[:len(pytest_tocarry)] == pytest.approx(pytest_tocarry)
    assert not ret_pass.str

