from cryptography.fernet import Fernet

class EncryptionUtils:
    def __init__(self):
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt data as a string."""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data back to string."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
