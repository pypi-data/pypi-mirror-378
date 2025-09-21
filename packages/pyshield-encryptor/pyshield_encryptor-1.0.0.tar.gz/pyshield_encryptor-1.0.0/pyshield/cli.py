"""
PyShield Command Line Interface
===============================

Command-line tools for encrypting and managing Python files.
Provides easy-to-use commands for encryption operations.
"""

import os
import sys
import argparse
import glob
from typing import List
from .encryptor import encrypt_file, is_encrypted_file
from .utils import (
    print_banner, print_platform_info, get_platform_info,
    find_python_files, backup_file, get_file_info, format_file_size
)

class PyShieldCLI:
    """Command-line interface for PyShield."""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self):
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            prog='pyshield',
            description='PyShield - Advanced Python Code Encryptor',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  pyshield encrypt script.py                    # Encrypt single file
  pyshield encrypt script.py -o encrypted.py   # Encrypt with custom output
  pyshield encrypt-dir ./src                    # Encrypt entire directory
  pyshield info script.py                       # Show file information
  pyshield version                              # Show version info
  pyshield platform                             # Show platform info

For more information, visit: https://github.com/pyshield/pyshield
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Encrypt command
        encrypt_parser = subparsers.add_parser(
            'encrypt', 
            help='Encrypt a Python file'
        )
        encrypt_parser.add_argument(
            'file', 
            help='Python file to encrypt'
        )
        encrypt_parser.add_argument(
            '-o', '--output',
            help='Output file path (default: overwrite original)'
        )
        encrypt_parser.add_argument(
            '-b', '--backup',
            action='store_true',
            help='Create backup of original file'
        )
        encrypt_parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help='Verbose output'
        )
        
        # Encrypt directory command
        encrypt_dir_parser = subparsers.add_parser(
            'encrypt-dir',
            help='Encrypt all Python files in a directory'
        )
        encrypt_dir_parser.add_argument(
            'directory',
            help='Directory containing Python files'
        )
        encrypt_dir_parser.add_argument(
            '-r', '--recursive',
            action='store_true',
            default=True,
            help='Encrypt files recursively (default: True)'
        )
        encrypt_dir_parser.add_argument(
            '-b', '--backup',
            action='store_true',
            help='Create backups of original files'
        )
        encrypt_dir_parser.add_argument(
            '-e', '--exclude',
            action='append',
            help='Exclude files matching pattern'
        )
        encrypt_dir_parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help='Verbose output'
        )
        
        # Info command
        info_parser = subparsers.add_parser(
            'info',
            help='Show information about a file'
        )
        info_parser.add_argument(
            'file',
            help='File to analyze'
        )
        
        # Version command
        subparsers.add_parser(
            'version',
            help='Show version information'
        )
        
        # Platform command
        subparsers.add_parser(
            'platform',
            help='Show platform information'
        )
        
        # Test command
        test_parser = subparsers.add_parser(
            'test',
            help='Test encryption/decryption'
        )
        test_parser.add_argument(
            'file',
            nargs='?',
            help='Test file (optional)'
        )
        
        return parser
    
    def run(self, args=None):
        """Run CLI with given arguments."""
        if args is None:
            args = sys.argv[1:]
        
        parsed_args = self.parser.parse_args(args)
        
        if not parsed_args.command:
            print_banner()
            self.parser.print_help()
            return 0
        
        try:
            if parsed_args.command == 'encrypt':
                return self._encrypt_file(parsed_args)
            elif parsed_args.command == 'encrypt-dir':
                return self._encrypt_directory(parsed_args)
            elif parsed_args.command == 'info':
                return self._show_info(parsed_args)
            elif parsed_args.command == 'version':
                return self._show_version()
            elif parsed_args.command == 'platform':
                return self._show_platform()
            elif parsed_args.command == 'test':
                return self._test_encryption(parsed_args)
            else:
                print(f"Unknown command: {parsed_args.command}")
                return 1
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return 1
        except Exception as e:
            print(f"Error: {e}")
            return 1
    
    def _encrypt_file(self, args):
        """Encrypt a single file."""
        if not os.path.exists(args.file):
            print(f"Error: File '{args.file}' not found.")
            return 1
        
        if not args.file.endswith('.py'):
            print(f"Error: File '{args.file}' is not a Python file.")
            return 1
        
        if is_encrypted_file(args.file):
            print(f"Warning: File '{args.file}' is already encrypted.")
            return 0
        
        output_file = args.output or args.file
        
        if args.verbose:
            print(f"Encrypting: {args.file}")
            if args.output:
                print(f"Output: {output_file}")
        
        # Create backup if requested
        if args.backup and args.file == output_file:
            try:
                backup_path = backup_file(args.file)
                if args.verbose:
                    print(f"Backup created: {backup_path}")
            except Exception as e:
                print(f"Warning: Failed to create backup: {e}")
        
        # Encrypt file
        try:
            result_file = encrypt_file(args.file, output_file)
            
            # Show results
            original_info = get_file_info(args.file)
            encrypted_info = get_file_info(result_file)
            
            print(f"✓ Successfully encrypted: {args.file}")
            if args.verbose:
                print(f"  Original size: {original_info['size_formatted']}")
                print(f"  Encrypted size: {encrypted_info['size_formatted']}")
                print(f"  Output file: {result_file}")
            
            return 0
            
        except Exception as e:
            print(f"Error encrypting file: {e}")
            return 1
    
    def _encrypt_directory(self, args):
        """Encrypt all Python files in a directory."""
        if not os.path.exists(args.directory):
            print(f"Error: Directory '{args.directory}' not found.")
            return 1
        
        if not os.path.isdir(args.directory):
            print(f"Error: '{args.directory}' is not a directory.")
            return 1
        
        # Find Python files
        python_files = find_python_files(args.directory, args.recursive)
        
        if not python_files:
            print(f"No Python files found in '{args.directory}'.")
            return 0
        
        # Filter out excluded files
        if args.exclude:
            filtered_files = []
            for file_path in python_files:
                excluded = False
                for pattern in args.exclude:
                    if glob.fnmatch.fnmatch(os.path.basename(file_path), pattern):
                        excluded = True
                        break
                if not excluded:
                    filtered_files.append(file_path)
            python_files = filtered_files
        
        # Filter out already encrypted files
        unencrypted_files = [f for f in python_files if not is_encrypted_file(f)]
        
        if not unencrypted_files:
            print("All Python files are already encrypted.")
            return 0
        
        print(f"Found {len(unencrypted_files)} Python files to encrypt.")
        
        # Encrypt files
        success_count = 0
        error_count = 0
        
        for file_path in unencrypted_files:
            try:
                if args.verbose:
                    print(f"Encrypting: {file_path}")
                
                # Create backup if requested
                if args.backup:
                    try:
                        backup_file(file_path)
                    except Exception as e:
                        print(f"Warning: Failed to backup {file_path}: {e}")
                
                # Encrypt file
                encrypt_file(file_path, file_path)
                success_count += 1
                
                if not args.verbose:
                    print(f"✓ {file_path}")
                
            except Exception as e:
                print(f"✗ Error encrypting {file_path}: {e}")
                error_count += 1
        
        # Summary
        print(f"\nEncryption complete:")
        print(f"  Successfully encrypted: {success_count} files")
        if error_count > 0:
            print(f"  Errors: {error_count} files")
        
        return 0 if error_count == 0 else 1
    
    def _show_info(self, args):
        """Show file information."""
        if not os.path.exists(args.file):
            print(f"Error: File '{args.file}' not found.")
            return 1
        
        info = get_file_info(args.file)
        
        print(f"File Information:")
        print(f"  Path: {info['path']}")
        print(f"  Size: {info['size_formatted']} ({info['size']} bytes)")
        print(f"  Encrypted: {'Yes' if info['is_encrypted'] else 'No'}")
        print(f"  Hash: {info['hash'][:16]}...")
        
        return 0
    
    def _show_version(self):
        """Show version information."""
        from . import __version__, __author__, __license__
        
        print_banner()
        print(f"Version: {__version__}")
        print(f"Author: {__author__}")
        print(f"License: {__license__}")
        print(f"Python: {sys.version}")
        
        return 0
    
    def _show_platform(self):
        """Show platform information."""
        print_banner()
        print_platform_info()
        
        return 0
    
    def _test_encryption(self, args):
        """Test encryption functionality."""
        print("Testing PyShield encryption...")
        
        # Test code
        test_code = '''
def hello_world():
    """Test function for PyShield encryption."""
    print("Hello from encrypted Python code!")
    return "PyShield works perfectly!"

if __name__ == "__main__":
    result = hello_world()
    print(f"Result: {result}")
'''
        
        try:
            from .encryptor import encrypt_string, decrypt_string
            
            print("1. Testing string encryption...")
            encrypted = encrypt_string(test_code)
            print(f"   ✓ Code encrypted ({len(encrypted)} bytes)")
            
            print("2. Testing string decryption...")
            decrypted = decrypt_string(encrypted)
            print("   ✓ Code decrypted successfully")
            
            print("3. Testing code integrity...")
            if decrypted.strip() == test_code.strip():
                print("   ✓ Code integrity verified")
            else:
                print("   ✗ Code integrity check failed")
                return 1
            
            print("4. Testing code execution...")
            exec_globals = {'__name__': '__main__'}
            exec(decrypted, exec_globals)
            print("   ✓ Encrypted code executed successfully")
            
            # Test file encryption if file provided
            if args.file:
                if os.path.exists(args.file):
                    print(f"5. Testing file encryption: {args.file}")
                    test_output = args.file + '.test_encrypted'
                    encrypt_file(args.file, test_output)
                    print(f"   ✓ File encrypted: {test_output}")
                    
                    # Clean up
                    os.remove(test_output)
                    print("   ✓ Test file cleaned up")
            
            print("\n✓ All tests passed! PyShield is working correctly.")
            return 0
            
        except Exception as e:
            print(f"✗ Test failed: {e}")
            return 1

def main():
    """Main CLI entry point."""
    cli = PyShieldCLI()
    return cli.run()

if __name__ == '__main__':
    sys.exit(main())
