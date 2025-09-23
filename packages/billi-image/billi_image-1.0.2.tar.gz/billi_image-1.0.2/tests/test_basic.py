"""
Basic tests for image-format-library

To run tests: pytest tests/
"""

import os
import tempfile
import pytest
from PIL import Image
from image_format_library import encode, decode, get_info, ImageFormatLibrary


class TestImageFormatLibrary:
    
    def setup_method(self):
        """Create a temporary test image"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='red')
        self.test_image_path = os.path.join(self.temp_dir, 'test.jpg')
        img.save(self.test_image_path, 'JPEG')
        
    def teardown_method(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_encode_decode_cycle(self):
        """Test encoding and then decoding an image"""
        # Encode
        encoded_path = os.path.join(self.temp_dir, 'test.billi')
        stats = encode('billi', self.test_image_path, encoded_path, quality=85)
        
        assert os.path.exists(encoded_path)
        assert 'compression_ratio' in stats
        assert 'space_saved_percent' in stats
        assert stats['compression_ratio'] > 0
        
        # Decode
        decoded_path = os.path.join(self.temp_dir, 'decoded.jpg')
        info = decode('billi', encoded_path, decoded_path)
        
        assert os.path.exists(decoded_path)
        assert 'width' in info
        assert 'height' in info
        assert info['width'] == 100
        assert info['height'] == 100
    
    def test_get_info(self):
        """Test getting file information"""
        encoded_path = os.path.join(self.temp_dir, 'test.billi')
        encode('billi', self.test_image_path, encoded_path, quality=90)
        
        info = get_info('billi', encoded_path)
        assert info['width'] == 100
        assert info['height'] == 100
        assert info['quality'] == 90
    
    def test_custom_extension(self):
        """Test using custom file extensions"""
        library = ImageFormatLibrary('custom')
        
        output_path = os.path.join(self.temp_dir, 'test.custom')
        stats = library.encode('billi', self.test_image_path, output_path)
        
        assert os.path.exists(output_path)
        assert output_path.endswith('.custom')
        
        # Test decoding
        decoded_path = os.path.join(self.temp_dir, 'decoded.jpg')
        info = library.decode('billi', output_path, decoded_path)
        assert os.path.exists(decoded_path)
    
    def test_invalid_format(self):
        """Test handling of invalid format names"""
        with pytest.raises(ValueError, match="Unsupported format"):
            encode('invalid_format', self.test_image_path, 'output.test')
    
    def test_missing_file(self):
        """Test handling of missing input files"""
        with pytest.raises(FileNotFoundError):
            encode('billi', 'nonexistent.jpg', 'output.billi')


if __name__ == '__main__':
    pytest.main([__file__])