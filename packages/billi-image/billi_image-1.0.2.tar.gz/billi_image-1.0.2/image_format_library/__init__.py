"""
Image Format Library - A Python library for custom image format encoding and decoding

This library provides a flexible framework for creating and handling custom image formats.
Currently supports the BILLI format with customizable file extensions.
"""

from .core import (
    ImageFormatLibrary,
    BILLIHandler,
    FormatHandler,
    encode,
    decode,
    get_info,
    get_supported_formats,
    batch_encode
)

__version__ = "1.0.0"
__author__ = "Ansh Sharma"
__email__ = "anshsxa@gmail.com"
__description__ = "A flexible library for custom image format encoding and decoding"

__all__ = [
    "ImageFormatLibrary",
    "BILLIHandler", 
    "FormatHandler",
    "encode",
    "decode",
    "get_info",
    "get_supported_formats",
    "batch_encode"
]