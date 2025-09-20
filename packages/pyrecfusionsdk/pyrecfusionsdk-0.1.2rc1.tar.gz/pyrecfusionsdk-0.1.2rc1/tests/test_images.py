import numpy as np
import pytest
from numpy.testing import assert_almost_equal, assert_equal

from pyRecFusionSDK import ColorImage, DepthImage


class TestColorImage:
    def test_creation(self):
        # Create from numpy array (height x width x 3)
        arr = np.random.randint(low=0, high=255, size=(10, 15, 3))
        im1 = ColorImage(arr)
        assert (im1.width, im1.height, im1.channels) == (15, 10, 3)
        assert_equal(arr, im1.data)
        with pytest.raises(TypeError, match="incompatible function arguments"):
            ColorImage(np.array([]))
        with pytest.raises(TypeError, match="incompatible function arguments"):
            ColorImage(np.arange(4))
        with pytest.raises(TypeError, match="incompatible function arguments"):
            ColorImage(np.array([[1, 2], [3, 4]]))
        with pytest.raises(TypeError, match="incompatible function arguments"):
            ColorImage(np.arange(16).reshape((2, 2, 2, 2)))
        with pytest.raises(TypeError, match="incompatible function arguments"):
            ColorImage(np.arange(16).reshape((2, 2, 4)))
        # Directly allocate all zeros (width x height x 3)
        im2 = ColorImage.allocate(33, 10)
        assert (im2.width, im2.height, im2.channels) == (33, 10, 3)
        assert np.sum(im2.data) == 0

    def test_modification(self):
        arr = np.random.randint(low=0, high=255, size=(10, 15, 3))
        im1 = ColorImage.allocate(15, 10)
        with pytest.raises(AssertionError):
            assert_equal(im1.data, arr)
        im1.data = arr
        assert_equal(im1.data, arr)

    def test_repr(self):
        im1 = ColorImage(np.random.randint(low=0, high=255, size=(5, 15, 3)))
        assert repr(im1) == "ColorImage(width=15, height=5)"
        im2 = ColorImage.allocate(500, 300)
        assert repr(im2) == "ColorImage(width=500, height=300)"


class TestDepthImage:
    def test_creation(self):
        # Create from numpy array (height x width x 3)
        arr = np.random.random((10, 15))
        im1 = DepthImage(arr)
        assert (im1.width, im1.height) == (15, 10)
        assert_almost_equal(arr, im1.data)
        with pytest.raises(TypeError, match="incompatible function arguments"):
            DepthImage(np.array([]))
        with pytest.raises(TypeError, match="incompatible function arguments"):
            DepthImage(np.arange(4))
        with pytest.raises(TypeError, match="incompatible function arguments"):
            DepthImage(np.arange(16).reshape((2, 2, 2, 2)))
        # Directly allocate all zeros (width x height x 3)
        im2 = DepthImage.allocate(33, 10)
        assert (im2.width, im2.height) == (33, 10)
        assert np.sum(im2.data) == 0

    def test_modification(self):
        arr = np.random.random((10, 15))
        im1 = DepthImage.allocate(15, 10)
        with pytest.raises(AssertionError):
            assert_equal(im1.data, arr)
        im1.data = arr
        assert_almost_equal(im1.data, arr)

    def test_repr(self):
        im1 = DepthImage(np.random.random((5, 15)))
        assert repr(im1) == "DepthImage(width=15, height=5)"
        im2 = DepthImage.allocate(500, 300)
        assert repr(im2) == "DepthImage(width=500, height=300)"
