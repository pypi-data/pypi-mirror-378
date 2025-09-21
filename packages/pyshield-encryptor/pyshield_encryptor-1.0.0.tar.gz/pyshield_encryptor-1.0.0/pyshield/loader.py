"""
PyShield Runtime Loader
=======================

Custom import hooks and module loader for seamless execution of encrypted Python files.
Handles both direct execution and module imports transparently.
"""

import sys
import os
import importlib.util
import importlib.machinery
from importlib.abc import Loader, MetaPathFinder
from types import ModuleType
from .encryptor import decrypt_string, is_encrypted_file

class PyShieldImporter(MetaPathFinder, Loader):
    """Custom importer for PyShield encrypted files."""
    
    def find_spec(self, fullname, path, target=None):
        """Find module spec for encrypted files."""
        if path is None:
            path = sys.path
        
        for search_path in path:
            if not os.path.isdir(search_path):
                continue
                
            # Look for encrypted .py files
            module_file = os.path.join(search_path, fullname + '.py')
            if os.path.exists(module_file) and is_encrypted_file(module_file):
                return importlib.machinery.ModuleSpec(
                    fullname, 
                    self, 
                    origin=module_file
                )
            
            # Look for encrypted packages
            package_dir = os.path.join(search_path, fullname)
            if os.path.isdir(package_dir):
                init_file = os.path.join(package_dir, '__init__.py')
                if os.path.exists(init_file) and is_encrypted_file(init_file):
                    return importlib.machinery.ModuleSpec(
                        fullname,
                        self,
                        origin=init_file,
                        is_package=True
                    )
        
        return None
    
    def create_module(self, spec):
        """Create module from spec."""
        return None  # Use default module creation
    
    def exec_module(self, module):
        """Execute encrypted module."""
        try:
            # Read encrypted file
            with open(module.__spec__.origin, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract encrypted code from wrapper
            if "ENCRYPTED_CODE = " in content:
                start = content.find("ENCRYPTED_CODE = ") + len("ENCRYPTED_CODE = ")
                end = content.find("\n", start)
                encrypted_repr = content[start:end].strip()
                
                # Safely evaluate the encrypted data
                encrypted_data = eval(encrypted_repr)
                
                # Decrypt and execute
                source_code = decrypt_string(encrypted_data)
                
                # Set module attributes
                module.__file__ = module.__spec__.origin
                module.__loader__ = self
                module.__package__ = module.__spec__.parent
                
                # Execute code in module namespace
                exec(source_code, module.__dict__)
            else:
                raise ImportError(f"Invalid encrypted file format: {module.__spec__.origin}")
                
        except Exception as e:
            raise ImportError(f"Failed to load encrypted module {module.__spec__.name}: {e}")

class PyShieldFileLoader(Loader):
    """File loader for encrypted Python files."""
    
    def __init__(self, fullname, path):
        self.fullname = fullname
        self.path = path
    
    def create_module(self, spec):
        """Create module."""
        return None
    
    def exec_module(self, module):
        """Execute encrypted module."""
        importer = PyShieldImporter()
        importer.exec_module(module)

def install_import_hook():
    """Install PyShield import hook in sys.meta_path."""
    # Check if already installed
    for finder in sys.meta_path:
        if isinstance(finder, PyShieldImporter):
            return
    
    # Install at the beginning of meta_path for priority
    sys.meta_path.insert(0, PyShieldImporter())

def uninstall_import_hook():
    """Remove PyShield import hook from sys.meta_path."""
    sys.meta_path[:] = [
        finder for finder in sys.meta_path 
        if not isinstance(finder, PyShieldImporter)
    ]

def execute_encrypted_file(file_path):
    """
    Execute an encrypted Python file directly.
    
    Args:
        file_path (str): Path to encrypted Python file
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not is_encrypted_file(file_path):
        raise ValueError(f"File is not PyShield encrypted: {file_path}")
    
    try:
        # Read encrypted file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract encrypted code from wrapper
        if "ENCRYPTED_CODE = " in content:
            start = content.find("ENCRYPTED_CODE = ") + len("ENCRYPTED_CODE = ")
            end = content.find("\n", start)
            encrypted_repr = content[start:end].strip()
            
            # Safely evaluate the encrypted data
            encrypted_data = eval(encrypted_repr)
            
            # Decrypt and execute
            source_code = decrypt_string(encrypted_data)
            
            # Create execution environment
            exec_globals = {
                '__file__': os.path.abspath(file_path),
                '__name__': '__main__',
                '__doc__': None,
                '__package__': None,
            }
            
            # Execute decrypted code
            exec(source_code, exec_globals)
        else:
            raise ValueError("Invalid encrypted file format")
            
    except Exception as e:
        raise RuntimeError(f"Failed to execute encrypted file: {e}")

def load_encrypted_module(module_name, file_path):
    """
    Load an encrypted module programmatically.
    
    Args:
        module_name (str): Name of the module
        file_path (str): Path to encrypted Python file
        
    Returns:
        ModuleType: Loaded module
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not is_encrypted_file(file_path):
        raise ValueError(f"File is not PyShield encrypted: {file_path}")
    
    try:
        # Create module spec
        spec = importlib.machinery.ModuleSpec(
            module_name,
            PyShieldImporter(),
            origin=file_path
        )
        
        # Create and execute module
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        return module
        
    except Exception as e:
        # Clean up on failure
        if module_name in sys.modules:
            del sys.modules[module_name]
        raise ImportError(f"Failed to load encrypted module: {e}")

# Auto-install hooks when this module is imported
_hooks_installed = False

def _auto_install():
    """Auto-install import hooks."""
    global _hooks_installed
    if not _hooks_installed:
        install_import_hook()
        _hooks_installed = True

# Install hooks on import
_auto_install()
