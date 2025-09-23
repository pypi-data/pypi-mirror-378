import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import gc

try:
	import cupy as cp
	CUPY_AVAILABLE = True
except ImportError:
	import numpy as cp
	CUPY_AVAILABLE = False

from mermake.deconvolver import (
	laplacian_3d, 
	batch_laplacian_fft, 
	repeat_last, 
	Deconvolver, 
	full_deconv
)


class TestDeconvolverProcessing:
	"""Test actual deconvolution processing."""
	
	@pytest.fixture
	def simple_test_data(self):
		"""Create simple test data."""
		# Create a simple test image with a point source
		image = cp.zeros((10, 50, 50))
		image[5, 25, 25] = 100  # Point source in center
		
		# Create a simple PSF
		psf = np.zeros((10, 10, 10))
		psf[5, 5, 5] = 1.0
		
		return image, psf
	
	def test_apply_basic(self, simple_test_data):
		"""Test basic apply functionality."""
		image, psf = simple_test_data
		image_shape = (None, *image.shape)
		
		deconv = Deconvolver(
			psfs=psf,
			image_shape=image_shape,
			tile_size=30,
			overlap=5,
			zpad=2,
			beta=0.001
		)
		result = deconv.apply(image)
		
		assert result.shape == image.shape, 1
		assert result.dtype == np.float32, 2
		# Result should be finite (no NaN or inf)
		assert np.all(np.isfinite(result)), 3
	
	@pytest.mark.parametrize("blur_radius", [None, 2, 5])
	def test_apply_with_blur_subtraction(self, simple_test_data, blur_radius):
		"""Test apply with different blur subtraction settings."""
		image, psf = simple_test_data
		image_shape = (None, *image.shape)
		
		deconv = Deconvolver(
			psfs=psf,
			image_shape=image_shape,
			tile_size=30,
			overlap=5,
			zpad=2
		)
		
		result = deconv.apply(image, blur_radius=blur_radius)
		
		assert result.shape == image.shape
		assert np.all(np.isfinite(result))
	
	def test_apply_with_flat_field(self, simple_test_data):
		"""Test apply with flat field correction."""
		image, psf = simple_test_data
		# Create a simple flat field (slight gradient)
		flat_field = cp.ones(( 50, 50))
		flat_field[:, :] *= cp.linspace(0.8, 1.2, 50)[:, None]
		
		image_shape = (None, *image.shape)
		
		deconv = Deconvolver(
			psfs=psf,
			image_shape=image_shape,
			tile_size=30,
			overlap=5,
			zpad=2
		)
		
		result = deconv.apply(image, flat_field=flat_field)
		
		assert result.shape == image.shape
		assert np.all(np.isfinite(result))



'''
# Mock tests for dependencies that might not be available
class TestMockDependencies:
	"""Test with mocked dependencies."""
	
	@patch('mermake.deconvolver.cp', new=np)
	def test_fallback_to_numpy(self):
		"""Test that code works when CuPy is mocked to NumPy."""
		image = np.random.random((5, 20, 20))
		psf = np.zeros((3, 3, 3))
		psf[1, 1, 1] = 1.0
		
		# This should work even with mocked CuPy
		result = full_deconv(image=image, psfs=psf, tile_size=15)
		assert result.shape == image.shape
	
	@patch('mermake.blur.box_1d')
	def test_with_mocked_blur(self, mock_blur):
		"""Test with mocked blur function."""
		mock_blur.return_value = None  # blur modifies in-place
		
		image = cp.random.random((5, 20, 20))
		psf = np.zeros((3, 3, 3))
		psf[1, 1, 1] = 1.0
		
		result = full_deconv(
			image=image, 
			psfs=psf, 
			tile_size=15,
			blur_radius=2  # This should trigger the blur calls
		)
		
		# Blur should have been called
		assert mock_blur.called
		assert result.shape == image.shape
'''

if __name__ == "__main__":
	pytest.main([__file__, "-v"])
