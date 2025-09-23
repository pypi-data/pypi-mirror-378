import os
import struct
from PIL import Image, ExifTags
import io
from abc import ABC, abstractmethod

class FormatHandler(ABC):
    """Abstract base class for format handlers"""
    
    @abstractmethod
    def encode(self, input_path, output_path, quality=85):
        """Encode an image to the specific format"""
        pass
    
    @abstractmethod
    def decode(self, input_path, output_path):
        """Decode the specific format back to a regular image"""
        pass
    
    @abstractmethod
    def get_info(self, file_path):
        """Get information about the file"""
        pass

class BILLIHandler(FormatHandler):
    """Handler for BILLI format"""
    
    def __init__(self, extension='billi'):
        self.signature = b'BILLI'
        self.version = 1
        self.extension = extension
    
    def encode(self, input_path, output_path, quality=85):
        """
        Encode an image to .billi format
        
        Args:
            input_path (str): Path to input image
            output_path (str): Path for output .billi file
            quality (int): JPEG quality 1-100, default 85
        
        Returns:
            dict: Encoding statistics
        """
        print(f"Encoding: {input_path}")
        
        # Open and process image
        with Image.open(input_path) as img:
            # Remove ALL metadata by creating new image
            img_clean = Image.new(img.mode, img.size)
            img_clean.putdata(list(img.getdata()))
            
            # Convert to RGB if necessary
            if img_clean.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparent images
                background = Image.new('RGB', img_clean.size, (255, 255, 255))
                if img_clean.mode == 'P':
                    img_clean = img_clean.convert('RGBA')
                if 'A' in img_clean.mode:
                    background.paste(img_clean, mask=img_clean.split()[-1])
                    img_clean = background
                else:
                    img_clean = img_clean.convert('RGB')
            
            width, height = img_clean.size
            
            # Compress to JPEG in memory
            jpeg_buffer = io.BytesIO()
            img_clean.save(jpeg_buffer, format='JPEG', quality=quality, optimize=True)
            jpeg_data = jpeg_buffer.getvalue()
        
        # Create header
        header = self._create_header(width, height, quality, len(jpeg_data))
        
        # Write .billi file
        with open(output_path, 'wb') as f:
            f.write(header + jpeg_data)
        
        # Calculate stats
        original_size = os.path.getsize(input_path)
        compressed_size = os.path.getsize(output_path)
        
        stats = {
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': original_size / compressed_size,
            'space_saved_percent': ((original_size - compressed_size) / original_size) * 100,
            'output_file': output_path
        }
        
        print(f"Original size: {self._format_bytes(original_size)}")
        print(f"Compressed size: {self._format_bytes(compressed_size)}")
        print(f"Compression ratio: {stats['compression_ratio']:.2f}:1")
        print(f"Space saved: {stats['space_saved_percent']:.1f}%")
        print(f"Output: {output_path}\n")
        
        return stats
    
    def decode(self, input_path, output_path):
        """
        Decode a .billi file back to regular image
        
        Args:
            input_path (str): Path to .billi file
            output_path (str): Path for output image
        
        Returns:
            dict: Decoding information
        """
        print(f"Decoding: {input_path}")
        
        with open(input_path, 'rb') as f:
            # Read and parse header
            header_data = f.read(18)
            header_info = self._parse_header(header_data)
            
            # Read image data
            jpeg_data = f.read(header_info['data_size'])
        
        # Save decoded image
        with open(output_path, 'wb') as f:
            f.write(jpeg_data)
        
        print(f"Decoded image: {header_info['width']}x{header_info['height']}")
        print(f"Quality: {header_info['quality']}%")
        print(f"Output: {output_path}\n")
        
        return {
            'width': header_info['width'],
            'height': header_info['height'],
            'quality': header_info['quality'],
            'output_file': output_path
        }
    
    def _create_header(self, width, height, quality, data_size):
        """Create 18-byte header for .billi format"""
        header = struct.pack(
            '<4sBIIBI',  # little-endian: 4s=signature, B=version, I=width, I=height, B=quality, I=data_size
            self.signature,
            self.version,
            width,
            height,
            quality,
            data_size
        )
        return header
    
    def _parse_header(self, header_data):
        """Parse .billi header"""
        if len(header_data) < 18:
            raise ValueError("Invalid .billi file: header too small")
        
        signature, version, width, height, quality, data_size = struct.unpack('<4sBIIBI', header_data)
        
        if signature != self.signature:
            raise ValueError(f"Invalid .billi file: wrong signature {signature}")
        
        if version != self.version:
            raise ValueError(f"Unsupported .billi version: {version}")
        
        return {
            'width': width,
            'height': height,
            'quality': quality,
            'data_size': data_size
        }
    
    def _format_bytes(self, bytes_val):
        """Format bytes to human readable string"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_val < 1024:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f} TB"
    
    def get_info(self, file_path):
        """Get information about a .billi file without decoding"""
        with open(file_path, 'rb') as f:
            header_data = f.read(18)
            header_info = self._parse_header(header_data)
        
        file_size = os.path.getsize(file_path)
        
        print(f"File: {file_path}")
        print(f"Dimensions: {header_info['width']}x{header_info['height']}")
        print(f"Quality: {header_info['quality']}%")
        print(f"File size: {self._format_bytes(file_size)}")
        print(f"Image data size: {self._format_bytes(header_info['data_size'])}")
        print()
        
        return header_info


class ImageFormatLibrary:
    """Main library class for encoding and decoding various image formats"""
    
    def __init__(self, custom_extension='billi'):
        self.custom_extension = custom_extension
        self.handlers = {
            'billi': BILLIHandler(custom_extension)
        }
    
    def encode(self, format_name, input_path, output_path, quality=85, extension=None):
        """
        Encode an image to the specified format
        
        Args:
            format_name (str): Name of the format (e.g., 'billi')
            input_path (str): Path to input image
            output_path (str): Path for output file
            quality (int): Quality setting (1-100), default 85
            extension (str): Custom file extension (optional, uses default if not provided)
        
        Returns:
            dict: Encoding statistics
        """
        format_name = format_name.lower()
        if format_name not in self.handlers:
            raise ValueError(f"Unsupported format: {format_name}. Supported formats: {list(self.handlers.keys())}")
        
        # If no extension provided and output_path doesn't have the right extension, add it
        if extension is None:
            extension = self.custom_extension
        
        # Check if output_path already has the correct extension
        if not output_path.lower().endswith(f'.{extension.lower()}'):
            name, _ = os.path.splitext(output_path)
            output_path = f"{name}.{extension}"
        
        handler = self.handlers[format_name]
        return handler.encode(input_path, output_path, quality)
    
    def decode(self, format_name, input_path, output_path, extension=None):
        """
        Decode a file from the specified format
        
        Args:
            format_name (str): Name of the format (e.g., 'billi')
            input_path (str): Path to input file
            output_path (str): Path for output image
            extension (str): Expected input file extension (optional, uses default if not provided)
        
        Returns:
            dict: Decoding information
        """
        format_name = format_name.lower()
        if format_name not in self.handlers:
            raise ValueError(f"Unsupported format: {format_name}. Supported formats: {list(self.handlers.keys())}")
        
        handler = self.handlers[format_name]
        return handler.decode(input_path, output_path)
    
    def get_info(self, format_name, file_path):
        """
        Get information about a file in the specified format
        
        Args:
            format_name (str): Name of the format (e.g., 'billi')
            file_path (str): Path to the file
        
        Returns:
            dict: File information
        """
        format_name = format_name.lower()
        if format_name not in self.handlers:
            raise ValueError(f"Unsupported format: {format_name}. Supported formats: {list(self.handlers.keys())}")
        
        handler = self.handlers[format_name]
        return handler.get_info(file_path)
    
    def get_supported_formats(self):
        """Get list of supported formats"""
        return list(self.handlers.keys())
    
    def set_extension(self, extension):
        """Set a new default extension for the library"""
        self.custom_extension = extension
        # Update all handlers with the new extension
        for handler in self.handlers.values():
            if hasattr(handler, 'extension'):
                handler.extension = extension


# Convenience functions for direct use
def encode(format_name, input_path, output_path, quality=85, extension='billi'):
    """
    Encode an image to the specified format
    
    Args:
        format_name (str): Name of the format (e.g., 'billi')
        input_path (str): Path to input image
        output_path (str): Path for output file
        quality (int): Quality setting (1-100), default 85
        extension (str): Custom file extension, default 'billi'
    
    Returns:
        dict: Encoding statistics
    """
    library = ImageFormatLibrary(extension)
    return library.encode(format_name, input_path, output_path, quality, extension)


def decode(format_name, input_path, output_path, extension='billi'):
    """
    Decode a file from the specified format
    
    Args:
        format_name (str): Name of the format (e.g., 'billi')
        input_path (str): Path to input file
        output_path (str): Path for output image
        extension (str): Expected input file extension, default 'billi'
    
    Returns:
        dict: Decoding information
    """
    library = ImageFormatLibrary(extension)
    return library.decode(format_name, input_path, output_path, extension)


def get_info(format_name, file_path, extension='billi'):
    """
    Get information about a file in the specified format
    
    Args:
        format_name (str): Name of the format (e.g., 'billi')
        file_path (str): Path to the file
        extension (str): Expected file extension, default 'billi'
    
    Returns:
        dict: File information
    """
    library = ImageFormatLibrary(extension)
    return library.get_info(format_name, file_path)


def get_supported_formats():
    """Get list of supported formats"""
    library = ImageFormatLibrary()
    return library.get_supported_formats()


def batch_encode(folder_path, format_name='billi', quality=85, extension='billi'):
    """Encode all images in a folder to the specified format with custom extension"""
    library = ImageFormatLibrary(extension)
    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp')
    
    total_original = 0
    total_compressed = 0
    processed = 0
    
    print(f"Batch encoding images to .{extension} format...")
    
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(supported_formats):
            input_path = os.path.join(folder_path, filename)
            name, _ = os.path.splitext(filename)
            output_path = os.path.join(folder_path, f"{name}.{extension}")
            
            try:
                stats = library.encode(format_name, input_path, output_path, quality=quality)
                total_original += stats['original_size']
                total_compressed += stats['compressed_size']
                processed += 1
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    if processed > 0:
        overall_ratio = total_original / total_compressed
        overall_savings = ((total_original - total_compressed) / total_original) * 100
        
        print(f"\n=== BATCH PROCESSING COMPLETE ===")
        print(f"Files processed: {processed}")
        print(f"Extension used: .{extension}")
        print(f"Total original size: {library.handlers[format_name]._format_bytes(total_original)}")
        print(f"Total compressed size: {library.handlers[format_name]._format_bytes(total_compressed)}")
        print(f"Overall compression ratio: {overall_ratio:.2f}:1")
        print(f"Overall space saved: {overall_savings:.1f}%")