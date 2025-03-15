import sqlite3
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256

# AES encryption key (must be 16, 24, or 32 bytes long)
KEY = get_random_bytes(32)  # 256-bit key

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('encrypted_db.sqlite')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            encrypted_data BLOB,
            encrypted_field BLOB
        )
    """)
    conn.commit()
    return conn

# Encrypt data using AES (CBC mode)
def encrypt_data(data):
    cipher = AES.new(KEY, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
    return cipher.iv + ct_bytes  # Return IV + ciphertext

# Decrypt data using AES (CBC mode)
def decrypt_data(encrypted_data):
    iv = encrypted_data[:AES.block_size]  # Extract IV
    ct = encrypted_data[AES.block_size:]  # Extract ciphertext
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode('utf-8')

# Deterministic encryption for queryable fields
def deterministic_encrypt(data):
    # Use a hash of the data as the encryption key for deterministic encryption
    h = SHA256.new(data.encode('utf-8'))
    cipher = AES.new(h.digest()[:16], AES.MODE_ECB)  # Use first 16 bytes of hash as key
    return cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))

# Insert a record into the database
def insert_record(conn, data, field):
    encrypted_data = encrypt_data(data)
    encrypted_field = deterministic_encrypt(field)  # Encrypt the queryable field
    cursor = conn.cursor()
    cursor.execute('INSERT INTO records (encrypted_data, encrypted_field) VALUES (?, ?)',
                  (encrypted_data, encrypted_field))
    conn.commit()

# Retrieve and decrypt a record from the database
def retrieve_record(conn, record_id):
    cursor = conn.cursor()
    cursor.execute('SELECT encrypted_data FROM records WHERE id = ?', (record_id,))
    result = cursor.fetchone()
    if result:
        return decrypt_data(result[0])
    return None

# Query records by exact match on the encrypted field
def query_by_field(conn, field):
    encrypted_field = deterministic_encrypt(field)  # Encrypt the query term
    cursor = conn.cursor()
    cursor.execute('SELECT encrypted_data FROM records WHERE encrypted_field = ?', (encrypted_field,))
    results = cursor.fetchall()
    return [decrypt_data(result[0]) for result in results]

if __name__ == "__main__":
    conn = init_db()

    # Insert some data
    insert_record(conn, "Hello, this is a secret message!", "message")
    insert_record(conn, "Another secret record.", "record")

    # Retrieve and decrypt data
    print("Record 1:", retrieve_record(conn, 1))
    print("Record 2:", retrieve_record(conn, 2))

    # Query by field
    print("Query results for 'message':", query_by_field(conn, "message"))
    print("Query results for 'record':", query_by_field(conn, "record"))

    conn.close()


