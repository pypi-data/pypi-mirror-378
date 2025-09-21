# AUTO GENERATED ON 2025-09-20 AT 15:57:04
# DO NOT EDIT BY HAND!
#
# To regenerate file, run
#
#     python dev/generate-tests.py
#

# fmt: off

import pytest
import numpy as np
import kernels

def test_pyawkward_UnionArray_fillindex_to64_fromU32_1():
    toindex = [123, 123, 123, 123, 123, 123]
    toindexoffset = 3
    fromindex = [1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1]
    length = 3
    funcPy = getattr(kernels, 'awkward_UnionArray_fillindex_to64_fromU32')
    funcPy(toindex=toindex, toindexoffset=toindexoffset, fromindex=fromindex, length=length)
    pytest_toindex = [123, 123, 123, 1, 0, 0]
    assert toindex[:len(pytest_toindex)] == pytest.approx(pytest_toindex)

def test_pyawkward_UnionArray_fillindex_to64_fromU32_2():
    toindex = [123, 123, 123, 123, 123, 123]
    toindexoffset = 3
    fromindex = [1, 2, 2, 3, 0, 2, 0, 2, 1, 1]
    length = 3
    funcPy = getattr(kernels, 'awkward_UnionArray_fillindex_to64_fromU32')
    funcPy(toindex=toindex, toindexoffset=toindexoffset, fromindex=fromindex, length=length)
    pytest_toindex = [123, 123, 123, 1, 2, 2]
    assert toindex[:len(pytest_toindex)] == pytest.approx(pytest_toindex)

def test_pyawkward_UnionArray_fillindex_to64_fromU32_3():
    toindex = [123, 123, 123, 123, 123, 123]
    toindexoffset = 3
    fromindex = [1, 3, 0, 3, 5, 2, 0, 2, 1, 1]
    length = 3
    funcPy = getattr(kernels, 'awkward_UnionArray_fillindex_to64_fromU32')
    funcPy(toindex=toindex, toindexoffset=toindexoffset, fromindex=fromindex, length=length)
    pytest_toindex = [123, 123, 123, 1, 3, 0]
    assert toindex[:len(pytest_toindex)] == pytest.approx(pytest_toindex)

def test_pyawkward_UnionArray_fillindex_to64_fromU32_4():
    toindex = [123, 123, 123, 123, 123, 123]
    toindexoffset = 3
    fromindex = [1, 4, 2, 3, 1, 2, 3, 1, 4, 3, 2, 1, 3, 2, 4, 5, 1, 2, 3, 4, 5]
    length = 3
    funcPy = getattr(kernels, 'awkward_UnionArray_fillindex_to64_fromU32')
    funcPy(toindex=toindex, toindexoffset=toindexoffset, fromindex=fromindex, length=length)
    pytest_toindex = [123, 123, 123, 1, 4, 2]
    assert toindex[:len(pytest_toindex)] == pytest.approx(pytest_toindex)

def test_pyawkward_UnionArray_fillindex_to64_fromU32_5():
    toindex = [123, 123, 123, 123, 123, 123]
    toindexoffset = 3
    fromindex = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    length = 3
    funcPy = getattr(kernels, 'awkward_UnionArray_fillindex_to64_fromU32')
    funcPy(toindex=toindex, toindexoffset=toindexoffset, fromindex=fromindex, length=length)
    pytest_toindex = [123, 123, 123, 0, 0, 0]
    assert toindex[:len(pytest_toindex)] == pytest.approx(pytest_toindex)

