"""
Command Line Interface for django-dart-sass
"""

import argparse
import sys
from pathlib import Path

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Django Dart Sass CLI'
    )
    parser.add_argument(
        'input_file',
        help='Input Sass/SCSS file'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output CSS file'
    )
    
    args = parser.parse_args()
    
    # Basic compilation
    from .registry import compile_file
    
    try:
        result = compile_file(args.input_file)
        
        if args.output:
            Path(args.output).write_text(result.css)
            print(f"Compiled {args.input_file} -> {args.output}")
        else:
            print(result.css)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
