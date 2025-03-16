from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

class EncryptionUtils:
    def __init__(self):
        self.key = get_random_bytes(32)  # 256-bit key

    def encrypt_data(self, data):
        """Encrypt data using AES in CBC mode."""
        cipher = AES.new(self.key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
        return cipher.iv + ct_bytes  # Return IV + ciphertext

    def decrypt_data(self, encrypted_data):
        """Decrypt data using AES in CBC mode."""
        iv = encrypted_data[:AES.block_size]
        ct = encrypted_data[AES.block_size:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode('utf-8')
