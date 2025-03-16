import sqlite3
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from PathORAM import PathORAM
from EncryptionUtils import EncryptionUtils

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('encrypted_db.sqlite')
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        encrypted_field BLOB,
        oram_id INTEGER
    )
    """)
    conn.commit()
    return conn

# Initialize Path ORAM
def init_path_oram(N, Z, num_orams):
    return PathORAM(N=N, Z=Z, num_orams=num_orams)

# Deterministic encryption for queryable fields
def deterministic_encrypt(data, key):
    """Encrypt data deterministically for queryable fields."""
    h = SHA256.new(data.encode('utf-8'))
    cipher = AES.new(h.digest()[:16], AES.MODE_ECB)
    return cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))

def compute_oram_id(record_id, num_orams):
    """Compute the ORAM ID for a given record ID using a PRP."""
    h = SHA256.new(str(record_id).encode('utf-8'))
    oram_id = int.from_bytes(h.digest(), byteorder='big') % num_orams
    return oram_id

def insert_record(conn, path_oram, encryption, data, field, alpha):
    """Insert a record into the database and Path ORAM."""
    encrypted_data = encryption.encrypt_data(data)  # Encrypt data
    encrypted_field = deterministic_encrypt(field, encryption.key)
    cursor = conn.cursor()

    # Get the next record ID
    cursor.execute('SELECT COUNT(*) FROM records')
    record_id = cursor.fetchone()[0] + 1  # Simulate auto-increment

    # Compute ORAM ID using a PRP
    num_orams = 2 ** alpha
    oram_id = compute_oram_id(record_id, num_orams)

    # Insert the record into Path ORAM
    path_oram.access(oram_id, op='write', a=record_id, data=encrypted_data)

    # Insert metadata into SQLite database
    cursor.execute('INSERT INTO records (id, encrypted_field, oram_id) VALUES (?, ?, ?)',
                  (record_id, encrypted_field, oram_id))
    conn.commit()
    print(f"Record inserted with field: {field} and ID: {record_id} (ORAM {oram_id})")

def retrieve_record(conn, path_oram, encryption, record_id):
    """Retrieve and decrypt a record by ID."""
    cursor = conn.cursor()
    cursor.execute('SELECT oram_id FROM records WHERE id = ?', (record_id,))
    result = cursor.fetchone()
    if result:
        oram_id = result[0]
        encrypted_data = path_oram.access(oram_id, op='read', a=record_id)
        return encryption.decrypt_data(encrypted_data)
    return None

def query_by_field(conn, path_oram, encryption, field, alpha, x):
    """Query records by field and return padded results."""
    encrypted_field = deterministic_encrypt(field, encryption.key)
    cursor = conn.cursor()

    # Retrieve all records with the matching field
    cursor.execute('SELECT id, oram_id FROM records WHERE encrypted_field = ?', (encrypted_field,))
    results = cursor.fetchall()

    # Collect all matching records
    all_records = []
    for record_id, oram_id in results:
        encrypted_data = path_oram.access(oram_id, op='read', a=record_id)
        all_records.append(encryption.decrypt_data(encrypted_data))

    # Pad the total number of results
    padded_records = pad_results(all_records, x)
    print(f"Query results for '{field}': {padded_records}")

def pad_results(results, x):
    """Pad the results to the next power-of-x."""
    current_length = len(results)
    if current_length == 0:
        return ['dummy'] * x  # Handle empty results

    # Find the next power of x
    target_length = 1
    while target_length < current_length:
        target_length *= x

    # Pad only if the current length is not already a power of x
    if target_length > current_length:
        return results + ['dummy'] * (target_length - current_length)
    else:
        return results  # No padding needed

def interactive_cli(conn, path_oram, encryption, alpha, x):
    """Interactive command-line interface for the SEAL program."""
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
            insert_record(conn, path_oram, encryption, data, field, alpha)
        elif choice == "2":
            record_id = input("Enter the record ID: ")
            try:
                record_id = int(record_id)
                record = retrieve_record(conn, path_oram, encryption, record_id)
                if record:
                    print(f"Record {record_id}: {record}")
                else:
                    print(f"No record found with ID {record_id}")
            except ValueError:
                print("Invalid record ID. Please enter a number.")
        elif choice == "3":
            field = input("Enter the field to query: ")
            query_by_field(conn, path_oram, encryption, field, alpha, x)
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

def test_seal_program():
    # Initialize the database, Path ORAM, and encryption
    conn = init_db()
    N = 10  # Maximum number of blocks per ORAM
    Z = 4   # Bucket capacity
    alpha = 2  # Number of bits of leakage (2^alpha ORAMs)
    num_orams = 2 ** alpha  # Number of ORAMs
    path_oram = init_path_oram(N=N, Z=Z, num_orams=num_orams)
    encryption = EncryptionUtils()
    x = 2  # Padding factor

    # Test data
    test_data = [
        ("data1", "field1"),
        ("data2", "field2"),
        ("data3", "field1"),
    ]

    # Insert records
    print("Inserting records...")
    for data, field in test_data:
        insert_record(conn, path_oram, encryption, data, field, alpha)

    # Retrieve records by ID
    print("\nRetrieving records by ID...")
    for record_id in range(1, len(test_data) + 1):
        record = retrieve_record(conn, path_oram, encryption, record_id)
        print(f"Record {record_id}: {record}")

    # Query records by field
    print("\nQuerying records by field...")
    query_by_field(conn, path_oram, encryption, "field1", alpha, x)

    # Close the database connection
    conn.close()

if __name__ == "__main__":
    test_seal_program()
