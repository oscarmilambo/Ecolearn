import os
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import json
from django.conf import settings

class DataEncryption:
    """Handle data encryption and decryption"""
    
    def __init__(self):
        self.key = self._get_encryption_key()
        self.cipher = Fernet(self.key)
    
    def _get_encryption_key(self):
        """Get or generate encryption key"""
        # Try to get from Django settings first (which handles .env via python-decouple)
        if hasattr(settings, 'ENCRYPTION_KEY') and settings.ENCRYPTION_KEY:
            # Key is already base64 encoded, return as bytes
            return settings.ENCRYPTION_KEY.encode()
        
        # Fallback: Generate key from SECRET_KEY if ENCRYPTION_KEY not set
        password = settings.SECRET_KEY.encode()
        salt = b'ecolearn_salt'  # In production, use a random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt_string(self, data):
        """Encrypt a string"""
        if isinstance(data, str):
            data = data.encode()
        return self.cipher.encrypt(data)
    
    def decrypt_string(self, encrypted_data):
        """Decrypt to string"""
        decrypted = self.cipher.decrypt(encrypted_data)
        return decrypted.decode()
    
    def encrypt_json(self, data):
        """Encrypt JSON data"""
        json_string = json.dumps(data)
        return self.encrypt_string(json_string)
    
    def decrypt_json(self, encrypted_data):
        """Decrypt JSON data"""
        json_string = self.decrypt_string(encrypted_data)
        return json.loads(json_string)
    
    def hash_password(self, password, salt=None):
        """Hash password with salt"""
        if salt is None:
            salt = os.urandom(32)
        
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return salt + pwdhash
    
    def verify_password(self, stored_password, provided_password):
        """Verify password against stored hash"""
        salt = stored_password[:32]
        stored_hash = stored_password[32:]
        pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
        return pwdhash == stored_hash

class SecureFileHandler:
    """Handle secure file operations"""
    
    def __init__(self):
        self.encryption = DataEncryption()
    
    def calculate_checksum(self, file_path):
        """Calculate SHA-256 checksum of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def encrypt_file(self, input_path, output_path):
        """Encrypt a file"""
        with open(input_path, 'rb') as infile:
            data = infile.read()
        
        encrypted_data = self.encryption.cipher.encrypt(data)
        
        with open(output_path, 'wb') as outfile:
            outfile.write(encrypted_data)
        
        return self.calculate_checksum(output_path)
    
    def decrypt_file(self, input_path, output_path):
        """Decrypt a file"""
        with open(input_path, 'rb') as infile:
            encrypted_data = infile.read()
        
        decrypted_data = self.encryption.cipher.decrypt(encrypted_data)
        
        with open(output_path, 'wb') as outfile:
            outfile.write(decrypted_data)
        
        return self.calculate_checksum(output_path)

def generate_encryption_key():
    """Generate a new encryption key"""
    return Fernet.generate_key().decode()

def encrypt_sensitive_data(data):
    """Utility function to encrypt sensitive data"""
    encryption = DataEncryption()
    if isinstance(data, dict):
        return encryption.encrypt_json(data)
    else:
        return encryption.encrypt_string(str(data))

def decrypt_sensitive_data(encrypted_data, is_json=False):
    """Utility function to decrypt sensitive data"""
    encryption = DataEncryption()
    if is_json:
        return encryption.decrypt_json(encrypted_data)
    else:
        return encryption.decrypt_string(encrypted_data)