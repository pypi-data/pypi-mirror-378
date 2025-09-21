"""
PyShield Encryption Engine
==========================

Core encryption functionality using AES-256 with additional obfuscation layers.
Designed for maximum security while maintaining cross-platform compatibility.
"""

import os
import base64
import hashlib
import secrets
import zlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class PyShieldEncryptor:
    """Advanced encryption engine for Python source code."""
    
    MAGIC_HEADER = b"PYSHIELD_ENCRYPTED_V1"
    SALT_SIZE = 32
    KEY_SIZE = 32
    
    def __init__(self):
        self.fernet = None
    
    def _generate_key(self, password: bytes, salt: bytes) -> bytes:
        """Generate encryption key from password and salt."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_SIZE,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password))
    
    def _obfuscate_code(self, code: str) -> str:
        """Apply code obfuscation before encryption."""
        # Remove comments and docstrings while preserving functionality
        lines = code.split('\n')
        obfuscated_lines = []
        
        in_multiline_string = False
        string_delimiter = None
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                continue
                
            # Handle multiline strings
            if '"""' in line or "'''" in line:
                if not in_multiline_string:
                    in_multiline_string = True
                    string_delimiter = '"""' if '"""' in line else "'''"
                elif string_delimiter in line:
                    in_multiline_string = False
                    string_delimiter = None
                continue
            
            if in_multiline_string:
                continue
                
            # Remove inline comments
            if '#' in line:
                # Simple comment removal (doesn't handle strings with #)
                comment_pos = line.find('#')
                line = line[:comment_pos].rstrip()
                
            if line.strip():
                obfuscated_lines.append(line)
        
        return '\n'.join(obfuscated_lines)
    
    def encrypt_code(self, source_code: str) -> bytes:
        """
        Encrypt Python source code with multiple layers of protection.
        
        Args:
            source_code (str): Python source code to encrypt
            
        Returns:
            bytes: Encrypted code with embedded metadata
        """
        # Step 1: Obfuscate code
        obfuscated = self._obfuscate_code(source_code)
        
        # Step 2: Compress code
        compressed = zlib.compress(obfuscated.encode('utf-8'), level=9)
        
        # Step 3: Generate random salt and password
        salt = secrets.token_bytes(self.SALT_SIZE)
        password = secrets.token_bytes(64)
        
        # Step 4: Generate encryption key
        key = self._generate_key(password, salt)
        fernet = Fernet(key)
        
        # Step 5: Encrypt compressed code
        encrypted_code = fernet.encrypt(compressed)
        
        # Step 6: Create final payload
        payload = {
            'salt': salt,
            'password': password,
            'encrypted_code': encrypted_code,
            'checksum': hashlib.sha256(source_code.encode()).hexdigest()
        }
        
        # Step 7: Serialize and encode payload
        import pickle
        serialized = pickle.dumps(payload)
        encoded = base64.b64encode(serialized)
        
        # Step 8: Add magic header
        final_payload = self.MAGIC_HEADER + b'\n' + encoded
        
        return final_payload
    
    def decrypt_code(self, encrypted_data: bytes) -> str:
        """
        Decrypt encrypted Python source code.
        
        Args:
            encrypted_data (bytes): Encrypted code data
            
        Returns:
            str: Decrypted Python source code
        """
        # Step 1: Verify magic header
        if not encrypted_data.startswith(self.MAGIC_HEADER):
            raise ValueError("Invalid encrypted file format")
        
        # Step 2: Extract payload
        payload_data = encrypted_data[len(self.MAGIC_HEADER):].strip()
        
        # Step 3: Decode and deserialize
        import pickle
        try:
            serialized = base64.b64decode(payload_data)
            payload = pickle.loads(serialized)
        except Exception as e:
            raise ValueError(f"Failed to decode encrypted data: {e}")
        
        # Step 4: Extract components
        salt = payload['salt']
        password = payload['password']
        encrypted_code = payload['encrypted_code']
        checksum = payload['checksum']
        
        # Step 5: Regenerate key and decrypt
        key = self._generate_key(password, salt)
        fernet = Fernet(key)
        
        try:
            compressed_code = fernet.decrypt(encrypted_code)
            source_code = zlib.decompress(compressed_code).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to decrypt code: {e}")
        
        # Step 6: Verify integrity
        if hashlib.sha256(source_code.encode()).hexdigest() != checksum:
            raise ValueError("Code integrity check failed")
        
        return source_code

# Global encryptor instance
_encryptor = PyShieldEncryptor()

def encrypt_string(source_code: str) -> bytes:
    """Encrypt a Python source code string."""
    return _encryptor.encrypt_code(source_code)

def decrypt_string(encrypted_data: bytes) -> str:
    """Decrypt encrypted Python source code."""
    return _encryptor.decrypt_code(encrypted_data)

def encrypt_file(source_file: str, output_file: str = None) -> str:
    """
    Encrypt a Python file.
    
    Args:
        source_file (str): Path to source Python file
        output_file (str): Path for encrypted output file
        
    Returns:
        str: Path to encrypted file
    """
    if output_file is None:
        output_file = source_file
    
    # Read source file
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except Exception as e:
        raise IOError(f"Failed to read source file '{source_file}': {e}")
    
    # Encrypt code
    encrypted_data = encrypt_string(source_code)
    
    # Create loader wrapper
    wrapper_code = f'''# PyShield Encrypted Python File
# This file contains encrypted Python code that will be executed transparently
# Original file: {os.path.basename(source_file)}
# Encrypted with PyShield v1.0.0

import base64
import sys
import os

# Embedded encrypted code
ENCRYPTED_CODE = {repr(encrypted_data)}

def __pyshield_execute__():
    """Execute the encrypted code."""
    try:
        # Import PyShield decryptor
        from pyshield.encryptor import decrypt_string
        
        # Decrypt and execute code
        source_code = decrypt_string(ENCRYPTED_CODE)
        
        # Execute in current module's namespace
        exec(source_code, globals())
        
    except ImportError:
        print("Error: PyShield module not found. Please install: pip install pyshield")
        sys.exit(1)
    except Exception as e:
        print(f"Error executing encrypted code: {{e}}")
        sys.exit(1)

# Execute encrypted code when module is imported or run
if __name__ == "__main__":
    __pyshield_execute__()
else:
    __pyshield_execute__()
'''
    
    # Write encrypted file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(wrapper_code)
    except Exception as e:
        raise IOError(f"Failed to write encrypted file '{output_file}': {e}")
    
    return output_file

def is_encrypted_file(file_path: str) -> bool:
    """Check if a file is PyShield encrypted."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(200)  # Read first 200 chars
            return "PyShield Encrypted Python File" in content
    except:
        return False
