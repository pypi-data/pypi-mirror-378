"""
PyShield - Advanced Python Code Encryptor
==========================================

A powerful Python module for encrypting Python source code while maintaining
full functionality and cross-platform compatibility.

Features:
- Heavy AES-256 encryption with obfuscation
- Seamless execution of encrypted files
- Import hook system for encrypted modules
- Cross-platform support (Windows, Linux, macOS, Android/Termux)
- Memory-only decryption (never writes decrypted code to disk)
- CLI and programmatic API

Usage:
    # Encrypt a file
    from pyshield import encrypt_file
    encrypt_file('script.py', 'encrypted_script.py')
    
    # Run encrypted file
    python encrypted_script.py
    
    # Import encrypted module
    import encrypted_module  # Works seamlessly

Author: PyShield Team
License: MIT
Version: 1.0.0
"""

import sys
import os
from .loader import install_import_hook, PyShieldImporter
from .encryptor import encrypt_file, encrypt_string, decrypt_string
from .utils import is_encrypted_file, get_version

__version__ = "1.0.0"
__author__ = "PyShield Team"
__license__ = "MIT"

# Auto-install import hooks when module is imported
_hooks_installed = False

def _install_hooks():
    """Install PyShield import hooks automatically."""
    global _hooks_installed
    if not _hooks_installed:
        install_import_hook()
        _hooks_installed = True

# Install hooks on import
_install_hooks()

# Public API
__all__ = [
    'encrypt_file',
    'encrypt_string', 
    'decrypt_string',
    'is_encrypted_file',
    'get_version',
    'PyShieldImporter',
    '__version__'
]

def encrypt(source_file, output_file=None):
    """
    Encrypt a Python file.
    
    Args:
        source_file (str): Path to the source Python file
        output_file (str, optional): Path for encrypted output. 
                                   If None, overwrites source file.
    
    Returns:
        str: Path to the encrypted file
    """
    if output_file is None:
        output_file = source_file
    
    return encrypt_file(source_file, output_file)

def info():
    """Display PyShield information."""
    print(f"PyShield v{__version__}")
    print("Advanced Python Code Encryptor")
    print("Cross-platform encryption with seamless execution")
    print(f"Python {sys.version}")
    print(f"Platform: {sys.platform}")
