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

def test_pyawkward_ListArrayU32_min_range_1():
    tomin = [123]
    fromstarts = [2, 0, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1]
    fromstops = [3, 2, 4, 5, 3, 4, 2, 5, 3, 4, 6, 11]
    lenstarts = 3
    funcPy = getattr(kernels, 'awkward_ListArrayU32_min_range')
    funcPy(tomin=tomin, fromstarts=fromstarts, fromstops=fromstops, lenstarts=lenstarts)
    pytest_tomin = [1]
    assert tomin[:len(pytest_tomin)] == pytest.approx(pytest_tomin)

def test_pyawkward_ListArrayU32_min_range_2():
    tomin = [123]
    fromstarts = [1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]
    fromstops = [8, 4, 5, 6, 5, 5, 7]
    lenstarts = 3
    funcPy = getattr(kernels, 'awkward_ListArrayU32_min_range')
    funcPy(tomin=tomin, fromstarts=fromstarts, fromstops=fromstops, lenstarts=lenstarts)
    pytest_tomin = [4]
    assert tomin[:len(pytest_tomin)] == pytest.approx(pytest_tomin)

def test_pyawkward_ListArrayU32_min_range_3():
    tomin = [123]
    fromstarts = [1, 4, 5, 6, 5, 5, 7, 1, 2, 1, 3, 1, 5, 3, 2]
    fromstops = [1, 4, 5, 6, 5, 5, 7, 1, 2, 1, 3, 1, 5, 3, 2]
    lenstarts = 3
    funcPy = getattr(kernels, 'awkward_ListArrayU32_min_range')
    funcPy(tomin=tomin, fromstarts=fromstarts, fromstops=fromstops, lenstarts=lenstarts)
    pytest_tomin = [0]
    assert tomin[:len(pytest_tomin)] == pytest.approx(pytest_tomin)

def test_pyawkward_ListArrayU32_min_range_4():
    tomin = [123]
    fromstarts = [1, 7, 6, 1, 3, 4, 2, 5, 2, 3, 1, 2, 3, 4, 5, 6, 7, 1, 2]
    fromstops = [1, 9, 6, 2, 4, 5, 3, 6, 3, 4, 2, 4, 5, 5, 7, 8, 2, 3]
    lenstarts = 3
    funcPy = getattr(kernels, 'awkward_ListArrayU32_min_range')
    funcPy(tomin=tomin, fromstarts=fromstarts, fromstops=fromstops, lenstarts=lenstarts)
    pytest_tomin = [0]
    assert tomin[:len(pytest_tomin)] == pytest.approx(pytest_tomin)

def test_pyawkward_ListArrayU32_min_range_5():
    tomin = [123]
    fromstarts = [0, 0, 0, 0, 0, 0, 0, 0]
    fromstops = [1, 1, 1, 1, 1, 1, 1, 1]
    lenstarts = 3
    funcPy = getattr(kernels, 'awkward_ListArrayU32_min_range')
    funcPy(tomin=tomin, fromstarts=fromstarts, fromstops=fromstops, lenstarts=lenstarts)
    pytest_tomin = [1]
    assert tomin[:len(pytest_tomin)] == pytest.approx(pytest_tomin)

