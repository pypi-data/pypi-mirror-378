"""
Command line interface for image-format-library
"""

import argparse
import sys
import os
from .core import encode, decode, get_info, batch_encode, get_supported_formats


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Image Format Library - Custom image format encoding/decoding",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Encode a single image
  image-format-cli encode billi input.jpg output.billi --quality 90

  # Decode an image
  image-format-cli decode billi input.billi output.jpg

  # Get file info
  image-format-cli info billi myfile.billi

  # Batch process a folder
  image-format-cli batch /path/to/images --format billi --quality 85

  # Use custom extension
  image-format-cli encode billi input.jpg output --extension myformat
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Encode command
    encode_parser = subparsers.add_parser('encode', help='Encode an image')
    encode_parser.add_argument('format', help='Format to use (e.g., billi)')
    encode_parser.add_argument('input', help='Input image path')
    encode_parser.add_argument('output', help='Output file path')
    encode_parser.add_argument('--quality', '-q', type=int, default=85,
                              help='Quality setting (1-100, default: 85)')
    encode_parser.add_argument('--extension', '-e', default='billi',
                              help='File extension (default: billi)')
    
    # Decode command
    decode_parser = subparsers.add_parser('decode', help='Decode a file')
    decode_parser.add_argument('format', help='Format to decode (e.g., billi)')
    decode_parser.add_argument('input', help='Input file path')
    decode_parser.add_argument('output', help='Output image path')
    decode_parser.add_argument('--extension', '-e', default='billi',
                              help='Expected file extension (default: billi)')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Get file information')
    info_parser.add_argument('format', help='Format of the file (e.g., billi)')
    info_parser.add_argument('file', help='File path')
    info_parser.add_argument('--extension', '-e', default='billi',
                            help='Expected file extension (default: billi)')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Batch process a folder')
    batch_parser.add_argument('folder', help='Folder containing images')
    batch_parser.add_argument('--format', '-f', default='billi',
                             help='Format to use (default: billi)')
    batch_parser.add_argument('--quality', '-q', type=int, default=85,
                             help='Quality setting (1-100, default: 85)')
    batch_parser.add_argument('--extension', '-e', default='billi',
                             help='File extension (default: billi)')
    
    # Formats command
    formats_parser = subparsers.add_parser('formats', help='List supported formats')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'encode':
            if not os.path.exists(args.input):
                print(f"Error: Input file '{args.input}' not found")
                sys.exit(1)
            
            stats = encode(args.format, args.input, args.output, 
                          quality=args.quality, extension=args.extension)
            print(f"✓ Encoded successfully")
            print(f"  Compression ratio: {stats['compression_ratio']:.2f}:1")
            print(f"  Space saved: {stats['space_saved_percent']:.1f}%")
            
        elif args.command == 'decode':
            if not os.path.exists(args.input):
                print(f"Error: Input file '{args.input}' not found")
                sys.exit(1)
            
            info = decode(args.format, args.input, args.output, extension=args.extension)
            print(f"✓ Decoded successfully")
            print(f"  Dimensions: {info['width']}x{info['height']}")
            print(f"  Quality: {info['quality']}%")
            
        elif args.command == 'info':
            if not os.path.exists(args.file):
                print(f"Error: File '{args.file}' not found")
                sys.exit(1)
            
            info = get_info(args.format, args.file, extension=args.extension)
            # Info is already printed by the function
            
        elif args.command == 'batch':
            if not os.path.isdir(args.folder):
                print(f"Error: Folder '{args.folder}' not found")
                sys.exit(1)
            
            batch_encode(args.folder, format_name=args.format, 
                        quality=args.quality, extension=args.extension)
            
        elif args.command == 'formats':
            formats = get_supported_formats()
            print("Supported formats:")
            for fmt in formats:
                print(f"  - {fmt}")
                
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()