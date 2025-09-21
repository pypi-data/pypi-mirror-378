"""
PyShield Utilities
==================

Utility functions for PyShield encryption module.
Cross-platform helpers and common functionality.
"""

import os
import sys
import hashlib
import platform
from typing import List, Optional

def get_version() -> str:
    """Get PyShield version."""
    return "1.0.0"

def get_platform_info() -> dict:
    """Get detailed platform information."""
    return {
        'system': platform.system(),
        'platform': platform.platform(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'python_implementation': platform.python_implementation(),
        'architecture': platform.architecture(),
        'is_android': is_android_platform(),
        'is_termux': is_termux_environment()
    }

def is_android_platform() -> bool:
    """Check if running on Android platform."""
    try:
        # Check for Android-specific paths and properties
        android_indicators = [
            '/system/bin/sh',
            '/system/build.prop',
            '/data/data',
            '/android_root'
        ]
        
        for indicator in android_indicators:
            if os.path.exists(indicator):
                return True
        
        # Check environment variables
        if 'ANDROID_ROOT' in os.environ or 'ANDROID_DATA' in os.environ:
            return True
            
        return False
    except:
        return False

def is_termux_environment() -> bool:
    """Check if running in Termux environment."""
    try:
        # Check for Termux-specific paths
        termux_indicators = [
            '/data/data/com.termux',
            os.path.expanduser('~/../../usr/bin/termux-info')
        ]
        
        for indicator in termux_indicators:
            if os.path.exists(indicator):
                return True
        
        # Check PREFIX environment variable (Termux-specific)
        if os.environ.get('PREFIX', '').endswith('/com.termux/files/usr'):
            return True
            
        return False
    except:
        return False

def is_encrypted_file(file_path: str) -> bool:
    """
    Check if a file is PyShield encrypted.
    
    Args:
        file_path (str): Path to the file to check
        
    Returns:
        bool: True if file is encrypted, False otherwise
    """
    try:
        if not os.path.exists(file_path):
            return False
            
        with open(file_path, 'r', encoding='utf-8') as f:
            # Read first few lines to check for PyShield signature
            content = f.read(500)
            return "PyShield Encrypted Python File" in content
    except:
        return False

def get_file_hash(file_path: str) -> str:
    """
    Get SHA256 hash of a file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: SHA256 hash in hexadecimal
    """
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        return hashlib.sha256(content).hexdigest()
    except:
        return ""

def find_python_files(directory: str, recursive: bool = True) -> List[str]:
    """
    Find all Python files in a directory.
    
    Args:
        directory (str): Directory to search
        recursive (bool): Whether to search recursively
        
    Returns:
        List[str]: List of Python file paths
    """
    python_files = []
    
    try:
        if recursive:
            for root, dirs, files in os.walk(directory):
                # Skip hidden directories and __pycache__
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
                
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(os.path.join(root, file))
        else:
            for file in os.listdir(directory):
                if file.endswith('.py') and os.path.isfile(os.path.join(directory, file)):
                    python_files.append(os.path.join(directory, file))
    except:
        pass
    
    return python_files

def backup_file(file_path: str, backup_suffix: str = '.backup') -> str:
    """
    Create a backup of a file.
    
    Args:
        file_path (str): Path to the file to backup
        backup_suffix (str): Suffix for backup file
        
    Returns:
        str: Path to backup file
    """
    backup_path = file_path + backup_suffix
    
    try:
        with open(file_path, 'rb') as src:
            with open(backup_path, 'wb') as dst:
                dst.write(src.read())
        return backup_path
    except Exception as e:
        raise IOError(f"Failed to create backup: {e}")

def ensure_directory(directory: str) -> None:
    """
    Ensure a directory exists, create if it doesn't.
    
    Args:
        directory (str): Directory path to ensure
    """
    try:
        os.makedirs(directory, exist_ok=True)
    except Exception as e:
        raise IOError(f"Failed to create directory '{directory}': {e}")

def safe_remove_file(file_path: str) -> bool:
    """
    Safely remove a file.
    
    Args:
        file_path (str): Path to file to remove
        
    Returns:
        bool: True if removed successfully, False otherwise
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        return True
    except:
        return False

def get_temp_directory() -> str:
    """
    Get appropriate temporary directory for current platform.
    
    Returns:
        str: Path to temporary directory
    """
    import tempfile
    
    # Use platform-appropriate temp directory
    temp_dir = tempfile.gettempdir()
    
    # Ensure it's writable
    try:
        test_file = os.path.join(temp_dir, 'pyshield_test')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        return temp_dir
    except:
        # Fallback to current directory
        return os.getcwd()

def validate_python_syntax(code: str):
    """
    Validate Python syntax.
    
    Args:
        code (str): Python code to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        compile(code, '<string>', 'exec')
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Validation error: {e}"

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def get_file_info(file_path: str) -> dict:
    """
    Get detailed file information.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        dict: File information
    """
    try:
        stat = os.stat(file_path)
        return {
            'path': file_path,
            'size': stat.st_size,
            'size_formatted': format_file_size(stat.st_size),
            'modified': stat.st_mtime,
            'is_encrypted': is_encrypted_file(file_path),
            'hash': get_file_hash(file_path),
            'exists': True
        }
    except:
        return {
            'path': file_path,
            'exists': False
        }

def print_banner():
    """Print PyShield banner."""
    banner = """
╔═══════════════════════════════════════╗
║            PyShield v1.0.0            ║
║     Advanced Python Code Encryptor   ║
║                                       ║
║  Cross-platform • Secure • Seamless  ║
╚═══════════════════════════════════════╝
"""
    print(banner)

def print_platform_info():
    """Print platform information."""
    info = get_platform_info()
    print(f"Platform: {info['system']} ({info['machine']})")
    print(f"Python: {info['python_version']} ({info['python_implementation']})")
    if info['is_android']:
        print("Android platform detected")
    if info['is_termux']:
        print("Termux environment detected")
