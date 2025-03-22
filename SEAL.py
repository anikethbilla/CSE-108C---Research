import os
import sqlite3
import random
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from PathORAM import PathORAM
from EncryptionUtils import EncryptionUtils

class SEAL:
    def __init__(self, N=10, Z=4, alpha=2, x=2):
        """
        Initialize the SEAL framework.
        :param N: Maximum number of blocks per ORAM.
        :param Z: Bucket capacity (number of blocks per bucket).
        :param alpha: Number of bits of leakage (2^alpha ORAMs).
        :param x: Padding factor (results are padded to the next power of x).
        """
        self.N = N
        self.Z = Z
        self.alpha = alpha
        self.x = x
        self.num_orams = 2 ** alpha
        self.orams = [PathORAM(N=N, Z=Z) for _ in range(self.num_orams)]  # Create multiple PathORAM objects
        self.encryption = EncryptionUtils()
        self.conn = self.init_db()

    def init_db(self):
        """Initialize the SQLite database."""
        db_file = 'encrypted_db.sqlite'
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"Deleted existing database file: {db_file}")

        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cb_no BLOB,
            case_number BLOB,
            arrest_date BLOB,
            race BLOB,
            charge_1_statute BLOB,
            charge_1_description BLOB,
            charge_1_type BLOB,
            charge_1_class BLOB,
            charge_2_statute BLOB,
            charge_2_description BLOB,
            charge_2_type BLOB,
            charge_2_class BLOB,
            charge_3_statute BLOB,
            charge_3_description BLOB,
            charge_3_type BLOB,
            charge_3_class BLOB,
            charge_4_statute BLOB,
            charge_4_description BLOB,
            charge_4_type BLOB,
            charge_4_class BLOB,
            charges_statute BLOB,
            charges_description BLOB,
            charges_type BLOB,
            charges_class BLOB,
            oram_id INTEGER
        )
        """)
        conn.commit()
        return conn

    def deterministic_token(self, data):
        """Encrypt data deterministically for queryable fields."""
        h = SHA256.new(data.encode('utf-8'))
        cipher = AES.new(h.digest()[:16], AES.MODE_ECB)
        return cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))

    def compute_oram_id(self, record_id):
        """Compute the ORAM ID for a given record ID using a PRP."""
        h = SHA256.new(str(record_id).encode('utf-8'))
        return int.from_bytes(h.digest(), byteorder='big') % self.num_orams

    def insert_record(self, record):
        """Insert a record into the database and the appropriate Path ORAM."""
        # Encrypt each field
        encrypted_fields = {}
        for field, value in record.items():
            if not isinstance(value, str):
                value = str(value)

            if field == "RACE":
                encrypted_fields[field] = self.deterministic_token(value)
            else:
                encrypted_fields[field] = self.encryption.encrypt_data(value)

        # Encrypt the data (combine all fields into a single string)
        data = ",".join(str(value) for value in record.values())
        encrypted_data = self.encryption.encrypt_data(data)

        cursor = self.conn.cursor()

        # Get the next record ID
        cursor.execute('SELECT COUNT(*) FROM records')
        record_id = cursor.fetchone()[0] + 1  # Simulate auto-increment

        # Compute ORAM ID using a PRP
        oram_id = self.compute_oram_id(record_id)

        # Insert the record into the appropriate Path ORAM
        self.orams[oram_id].access(op='write', a=record_id, data=encrypted_data)

        # Insert metadata into SQLite database
        cursor.execute('''
            INSERT INTO records (
                id, cb_no, case_number, arrest_date, race,
                charge_1_statute, charge_1_description, charge_1_type, charge_1_class,
                charge_2_statute, charge_2_description, charge_2_type, charge_2_class,
                charge_3_statute, charge_3_description, charge_3_type, charge_3_class,
                charge_4_statute, charge_4_description, charge_4_type, charge_4_class,
                charges_statute, charges_description, charges_type, charges_class,
                oram_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record_id,
            encrypted_fields.get("CB_NO", ""),
            encrypted_fields.get("CASE NUMBER", ""),
            encrypted_fields.get("ARREST DATE", ""),
            encrypted_fields.get("RACE", ""),
            encrypted_fields.get("CHARGE 1 STATUTE", ""),
            encrypted_fields.get("CHARGE 1 DESCRIPTION", ""),
            encrypted_fields.get("CHARGE 1 TYPE", ""),
            encrypted_fields.get("CHARGE 1 CLASS", ""),
            encrypted_fields.get("CHARGE 2 STATUTE", ""),
            encrypted_fields.get("CHARGE 2 DESCRIPTION", ""),
            encrypted_fields.get("CHARGE 2 TYPE", ""),
            encrypted_fields.get("CHARGE 2 CLASS", ""),
            encrypted_fields.get("CHARGE 3 STATUTE", ""),
            encrypted_fields.get("CHARGE 3 DESCRIPTION", ""),
            encrypted_fields.get("CHARGE 3 TYPE", ""),
            encrypted_fields.get("CHARGE 3 CLASS", ""),
            encrypted_fields.get("CHARGE 4 STATUTE", ""),
            encrypted_fields.get("CHARGE 4 DESCRIPTION", ""),
            encrypted_fields.get("CHARGE 4 TYPE", ""),
            encrypted_fields.get("CHARGE 4 CLASS", ""),
            encrypted_fields.get("CHARGES STATUTE", ""),
            encrypted_fields.get("CHARGES DESCRIPTION", ""),
            encrypted_fields.get("CHARGES TYPE", ""),
            encrypted_fields.get("CHARGES CLASS", ""),
            oram_id
        ))
        self.conn.commit()
        print(f"Record inserted with ID: {record_id} (ORAM {oram_id})")

    def retrieve_record(self, record_id):
        """Retrieve and decrypt a record by ID."""
        # Compute ORAM ID using a PRP
        oram_id = self.compute_oram_id(record_id)

        # Retrieve the record from the appropriate Path ORAM
        encrypted_data = self.orams[oram_id].access(op='read', a=record_id)
        if encrypted_data is not None:
            decrypted_data = self.encryption.decrypt_data(encrypted_data)
            # Split the decrypted data into individual fields
            fields = decrypted_data.split(',')
            return {
                "CB_NO": fields[0],
                "CASE NUMBER": fields[1],
                "ARREST DATE": fields[2],
                "RACE": fields[3],
                "CHARGE 1 STATUTE": fields[4],
                "CHARGE 1 DESCRIPTION": fields[5],
                "CHARGE 1 TYPE": fields[6],
                "CHARGE 1 CLASS": fields[7],
                "CHARGE 2 STATUTE": fields[8],
                "CHARGE 2 DESCRIPTION": fields[9],
                "CHARGE 2 TYPE": fields[10],
                "CHARGE 2 CLASS": fields[11],
                "CHARGE 3 STATUTE": fields[12],
                "CHARGE 3 DESCRIPTION": fields[13],
                "CHARGE 3 TYPE": fields[14],
                "CHARGE 3 CLASS": fields[15],
                "CHARGE 4 STATUTE": fields[16],
                "CHARGE 4 DESCRIPTION": fields[17],
                "CHARGE 4 TYPE": fields[18],
                "CHARGE 4 CLASS": fields[19],
                "CHARGES STATUTE": fields[20],
                "CHARGES DESCRIPTION": fields[21],
                "CHARGES TYPE": fields[22],
                "CHARGES CLASS": fields[23],
            }
        return None

    def query_by_field(self, field_name, field_value):
        """Query records by a specific field and return padded results."""
        # Encrypt the field value
        encrypted_field_value = self.deterministic_token(field_value)

        # Map the field name to the corresponding database column
        field_to_column = {
            "RACE": "race",
            "CB_NO": "cb_no",
            "CASE NUMBER": "case_number",
            "ARREST DATE": "arrest_date",
            "CHARGE 1 STATUTE": "charge_1_statute",
            "CHARGE 1 DESCRIPTION": "charge_1_description",
            "CHARGE 1 TYPE": "charge_1_type",
            "CHARGE 1 CLASS": "charge_1_class",
            "CHARGE 2 STATUTE": "charge_2_statute",
            "CHARGE 2 DESCRIPTION": "charge_2_description",
            "CHARGE 2 TYPE": "charge_2_type",
            "CHARGE 2 CLASS": "charge_2_class",
            "CHARGE 3 STATUTE": "charge_3_statute",
            "CHARGE 3 DESCRIPTION": "charge_3_description",
            "CHARGE 3 TYPE": "charge_3_type",
            "CHARGE 3 CLASS": "charge_3_class",
            "CHARGE 4 STATUTE": "charge_4_statute",
            "CHARGE 4 DESCRIPTION": "charge_4_description",
            "CHARGE 4 TYPE": "charge_4_type",
            "CHARGE 4 CLASS": "charge_4_class",
            "CHARGES STATUTE": "charges_statute",
            "CHARGES DESCRIPTION": "charges_description",
            "CHARGES TYPE": "charges_type",
            "CHARGES CLASS": "charges_class",
        }

        # Get the corresponding column name
        column_name = field_to_column.get(field_name.upper())
        if not column_name:
            raise ValueError(f"Field '{field_name}' does not exist in the database schema.")

        cursor = self.conn.cursor()

        # Retrieve all records with the matching field
        cursor.execute(f'SELECT id, oram_id FROM records WHERE {column_name} = ?', (encrypted_field_value,))
        results = cursor.fetchall()

        # Collect all matching records
        all_records = []
        for record_id, oram_id in results:
            encrypted_data = self.orams[oram_id].access(op='read', a=record_id)
            if encrypted_data is not None:  # Only process if data is found
                decrypted_data = self.encryption.decrypt_data(encrypted_data)
                all_records.append(decrypted_data)

        # Pad the total number of results
        padded_records = self.pad_results(all_records)
        print(f"Query results for '{field_name} = {field_value}': {padded_records}")

        # Return the padded results
        return padded_records

    def pad_results(self, results):
        """Pad the results to the next power-of-x."""
        current_length = len(results)
        if current_length == 0:
            return ['dummy'] * self.x  # Handle empty results

        # Find the next power of x
        target_length = 1
        while target_length < current_length:
            target_length *= self.x

        # Pad only if the current length is not already a power of x
        if target_length > current_length:
            return results + ['dummy'] * (target_length - current_length)
        else:
            return results  # No padding needed
