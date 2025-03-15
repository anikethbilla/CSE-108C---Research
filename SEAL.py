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
        encrypted_field BLOB,
        oram_id INTEGER
    )
    """)
    conn.commit()
    return conn

def compute_oram_id(record_id, alpha):
    # Use SHA-256 as a PRP to map record_id to an ORAM ID
    h = SHA256.new(str(record_id).encode('utf-8'))
    oram_id = int.from_bytes(h.digest(), byteorder='big') % (2 ** alpha)
    return oram_id

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

def insert_record(conn, data, field, alpha):
    encrypted_data = encrypt_data(data)
    encrypted_field = deterministic_encrypt(field)
    cursor = conn.cursor()

    # Get the next record ID
    cursor.execute('SELECT COUNT(*) FROM records')
    record_id = cursor.fetchone()[0] + 1  # Simulate auto-increment

    # Compute ORAM ID
    oram_id = compute_oram_id(record_id, alpha)

    # Insert the record
    cursor.execute('INSERT INTO records (encrypted_data, encrypted_field, oram_id) VALUES (?, ?, ?)',
                  (encrypted_data, encrypted_field, oram_id))
    conn.commit()
    print(f"Record inserted with field: {field} and ORAM ID: {oram_id}")

# Retrieve and decrypt a record from the database
def retrieve_record(conn, record_id):
    cursor = conn.cursor()
    cursor.execute('SELECT encrypted_data FROM records WHERE id = ?', (record_id,))
    result = cursor.fetchone()
    if result:
        return decrypt_data(result[0])
    return None

def pad_results(results, x):
    # Pad the results to the next power-of-x
    target_length = x ** (len(results).bit_length())
    padded_results = results + ['dummy'] * (target_length - len(results))
    return padded_results

def query_by_field(conn, field, alpha, x):
    encrypted_field = deterministic_encrypt(field)
    cursor = conn.cursor()

    # Retrieve all records with the matching field
    cursor.execute('SELECT encrypted_data, oram_id FROM records WHERE encrypted_field = ?', (encrypted_field,))
    results = cursor.fetchall()

    # Group records by ORAM ID
    oram_results = {}
    for encrypted_data, oram_id in results:
        if oram_id not in oram_results:
            oram_results[oram_id] = []
        oram_results[oram_id].append(decrypt_data(encrypted_data))

    # Simulate accessing the appropriate ORAM and pad results
    print(f"Query results for '{field}':")
    for oram_id, records in oram_results.items():
        padded_records = pad_results(records, x)
        print(f"ORAM {oram_id}: {padded_records}")

def interactive_cli(conn, alpha, x):
    while True:
        print("\nOptions:")
        print("1. Insert a record")
        print("2. Retrieve a record by ID")
        print("3. Query records by field")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            data = input("Enter the data to encrypt: ")
            field = input("Enter the field for querying: ")
            insert_record(conn, data, field, alpha)
        elif choice == "2":
            record_id = input("Enter the record ID: ")
            try:
                record_id = int(record_id)
                record = retrieve_record(conn, record_id)
                if record:
                    print(f"Record {record_id}: {record}")
                else:
                    print(f"No record found with ID {record_id}")
            except ValueError:
                print("Invalid record ID. Please enter a number.")
        elif choice == "3":
            field = input("Enter the field to query: ")
            query_by_field(conn, field, alpha, x)
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    alpha = int(input("Enter the value of alpha (bits of leakage): "))
    x = int(input("Enter the value of x (padding factor): "))
    conn = init_db()
    interactive_cli(conn, alpha, x)
    conn.close()
