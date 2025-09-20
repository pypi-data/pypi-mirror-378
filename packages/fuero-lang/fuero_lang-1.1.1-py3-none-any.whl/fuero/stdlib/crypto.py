"""
cryptography utilities for fuero
provides encryption, hashing, and security functions
"""

import hashlib
import hmac
import secrets
import base64
from typing import Union, Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os


class Crypto:
    """cryptography and security utilities"""
    
    def __init__(self):
        pass
    
    # Hashing functions
    def md5(self, data: Union[str, bytes]) -> str:
        """Calculate MD5 hash"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.md5(data).hexdigest()
    
    def sha1(self, data: Union[str, bytes]) -> str:
        """Calculate SHA-1 hash"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha1(data).hexdigest()
    
    def sha256(self, data: Union[str, bytes]) -> str:
        """Calculate SHA-256 hash"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha256(data).hexdigest()
    
    def sha512(self, data: Union[str, bytes]) -> str:
        """Calculate SHA-512 hash"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha512(data).hexdigest()
    
    def blake2b(self, data: Union[str, bytes], digest_size: int = 64) -> str:
        """Calculate BLAKE2b hash"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.blake2b(data, digest_size=digest_size).hexdigest()
    
    def blake2s(self, data: Union[str, bytes], digest_size: int = 32) -> str:
        """Calculate BLAKE2s hash"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.blake2s(data, digest_size=digest_size).hexdigest()
    
    # HMAC functions
    def hmac_sha256(self, key: Union[str, bytes], message: Union[str, bytes]) -> str:
        """Calculate HMAC-SHA256"""
        if isinstance(key, str):
            key = key.encode('utf-8')
        if isinstance(message, str):
            message = message.encode('utf-8')
        return hmac.new(key, message, hashlib.sha256).hexdigest()
    
    def hmac_sha512(self, key: Union[str, bytes], message: Union[str, bytes]) -> str:
        """Calculate HMAC-SHA512"""
        if isinstance(key, str):
            key = key.encode('utf-8')
        if isinstance(message, str):
            message = message.encode('utf-8')
        return hmac.new(key, message, hashlib.sha512).hexdigest()
    
    def verify_hmac(self, key: Union[str, bytes], message: Union[str, bytes], 
                    signature: str, algorithm: str = 'sha256') -> bool:
        """Verify HMAC signature"""
        if algorithm == 'sha256':
            expected = self.hmac_sha256(key, message)
        elif algorithm == 'sha512':
            expected = self.hmac_sha512(key, message)
        else:
            raise ValueError(f"Unsupported HMAC algorithm: {algorithm}")
        
        return hmac.compare_digest(expected, signature)
    
    # Password hashing
    def hash_password(self, password: str, salt: Optional[bytes] = None) -> Dict[str, str]:
        """Hash password with PBKDF2"""
        if salt is None:
            salt = os.urandom(32)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(password.encode('utf-8'))
        
        return {
            'hash': base64.b64encode(key).decode('utf-8'),
            'salt': base64.b64encode(salt).decode('utf-8')
        }
    
    def verify_password(self, password: str, hash_data: Dict[str, str]) -> bool:
        """Verify password against hash"""
        try:
            salt = base64.b64decode(hash_data['salt'])
            stored_hash = base64.b64decode(hash_data['hash'])
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            kdf.verify(password.encode('utf-8'), stored_hash)
            return True
        except Exception:
            return False
    
    # Random generation
    def random_bytes(self, length: int) -> bytes:
        """Generate cryptographically secure random bytes"""
        return secrets.token_bytes(length)
    
    def random_string(self, length: int, alphabet: str = None) -> str:
        """Generate cryptographically secure random string"""
        if alphabet is None:
            alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def random_hex(self, length: int) -> str:
        """Generate random hex string"""
        return secrets.token_hex(length)
    
    def random_urlsafe(self, length: int) -> str:
        """Generate random URL-safe string"""
        return secrets.token_urlsafe(length)
    
    def random_int(self, min_val: int, max_val: int) -> int:
        """Generate cryptographically secure random integer"""
        return secrets.randbelow(max_val - min_val + 1) + min_val
    
    # Symmetric encryption (Fernet)
    def generate_key(self) -> str:
        """Generate Fernet encryption key"""
        return Fernet.generate_key().decode('utf-8')
    
    def encrypt(self, data: Union[str, bytes], key: str) -> str:
        """Encrypt data with Fernet"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        f = Fernet(key.encode('utf-8'))
        encrypted = f.encrypt(data)
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt(self, encrypted_data: str, key: str) -> str:
        """Decrypt data with Fernet"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            f = Fernet(key.encode('utf-8'))
            decrypted = f.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")
    
    # AES encryption
    def aes_encrypt(self, data: Union[str, bytes], key: bytes, iv: Optional[bytes] = None) -> Dict[str, str]:
        """Encrypt data with AES-256-CBC"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if len(key) != 32:
            raise ValueError("AES key must be 32 bytes (256 bits)")
        
        if iv is None:
            iv = os.urandom(16)
        elif len(iv) != 16:
            raise ValueError("AES IV must be 16 bytes")
        
        # Pad data to multiple of 16 bytes
        padding_length = 16 - (len(data) % 16)
        padded_data = data + bytes([padding_length] * padding_length)
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        
        return {
            'encrypted': base64.b64encode(encrypted).decode('utf-8'),
            'iv': base64.b64encode(iv).decode('utf-8')
        }
    
    def aes_decrypt(self, encrypted_data: str, key: bytes, iv: str) -> str:
        """Decrypt AES-256-CBC encrypted data"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data)
            iv_bytes = base64.b64decode(iv)
            
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv_bytes))
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(encrypted_bytes) + decryptor.finalize()
            
            # Remove padding
            padding_length = padded_data[-1]
            data = padded_data[:-padding_length]
            
            return data.decode('utf-8')
        except Exception as e:
            raise ValueError(f"AES decryption failed: {e}")
    
    # RSA asymmetric encryption
    def generate_rsa_keypair(self, key_size: int = 2048) -> Dict[str, str]:
        """Generate RSA key pair"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
        )
        public_key = private_key.public_key()
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return {
            'private_key': private_pem.decode('utf-8'),
            'public_key': public_pem.decode('utf-8')
        }
    
    def rsa_encrypt(self, data: Union[str, bytes], public_key_pem: str) -> str:
        """Encrypt data with RSA public key"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        public_key = serialization.load_pem_public_key(public_key_pem.encode('utf-8'))
        encrypted = public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(encrypted).decode('utf-8')
    
    def rsa_decrypt(self, encrypted_data: str, private_key_pem: str) -> str:
        """Decrypt data with RSA private key"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data)
            private_key = serialization.load_pem_private_key(
                private_key_pem.encode('utf-8'),
                password=None
            )
            
            decrypted = private_key.decrypt(
                encrypted_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return decrypted.decode('utf-8')
        except Exception as e:
            raise ValueError(f"RSA decryption failed: {e}")
    
    def rsa_sign(self, data: Union[str, bytes], private_key_pem: str) -> str:
        """Sign data with RSA private key"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode('utf-8'),
            password=None
        )
        
        signature = private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')
    
    def rsa_verify(self, data: Union[str, bytes], signature: str, public_key_pem: str) -> bool:
        """Verify RSA signature"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            signature_bytes = base64.b64decode(signature)
            public_key = serialization.load_pem_public_key(public_key_pem.encode('utf-8'))
            
            public_key.verify(
                signature_bytes,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    # Base64 encoding/decoding
    def base64_encode(self, data: Union[str, bytes]) -> str:
        """Encode data to base64"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return base64.b64encode(data).decode('utf-8')
    
    def base64_decode(self, encoded_data: str) -> str:
        """Decode base64 data"""
        try:
            decoded = base64.b64decode(encoded_data)
            return decoded.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Base64 decoding failed: {e}")
    
    def base64_urlsafe_encode(self, data: Union[str, bytes]) -> str:
        """Encode data to URL-safe base64"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return base64.urlsafe_b64encode(data).decode('utf-8')
    
    def base64_urlsafe_decode(self, encoded_data: str) -> str:
        """Decode URL-safe base64 data"""
        try:
            decoded = base64.urlsafe_b64decode(encoded_data)
            return decoded.decode('utf-8')
        except Exception as e:
            raise ValueError(f"URL-safe base64 decoding failed: {e}")
    
    # Utility functions
    def constant_time_compare(self, a: str, b: str) -> bool:
        """Compare two strings in constant time"""
        return hmac.compare_digest(a, b)
    
    def secure_filename(self, filename: str) -> str:
        """Generate secure filename"""
        import re
        # Remove path separators and dangerous characters
        filename = re.sub(r'[^\w\s-.]', '', filename)
        # Replace spaces with underscores
        filename = re.sub(r'[-\s]+', '_', filename)
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        return filename
    
    def generate_uuid(self) -> str:
        """Generate UUID4"""
        import uuid
        return str(uuid.uuid4())
    
    def generate_csrf_token(self) -> str:
        """Generate CSRF token"""
        return self.random_urlsafe(32)
    
    def hash_file(self, filepath: str, algorithm: str = 'sha256') -> str:
        """Calculate hash of file"""
        hash_func = getattr(hashlib, algorithm)()
        
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    def verify_file_integrity(self, filepath: str, expected_hash: str, 
                             algorithm: str = 'sha256') -> bool:
        """Verify file integrity against expected hash"""
        try:
            actual_hash = self.hash_file(filepath, algorithm)
            return self.constant_time_compare(actual_hash, expected_hash)
        except Exception:
            return False
