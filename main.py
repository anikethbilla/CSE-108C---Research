import csv
from SEAL import SEAL
from AttackSimulator import AttackSimulator

def load_dataset(csv_file):
    """
    Load the dataset from a CSV file.
    :param csv_file: Path to the CSV file.
    :return: A list of dictionaries representing the dataset.
    """
    dataset = []
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            dataset.append(row)
    return dataset

def main():
    # Initialize the SEAL system
    seal_system = SEAL(N=10, Z=4, alpha=2, x=2)

    # Load the dataset from a CSV file
    csv_file = "Arrests_20250316.csv"  # Replace with the path to your CSV file
    dataset = load_dataset(csv_file)

    # Insert the dataset into the SEAL system
    for record in dataset:
        seal_system.insert_record(record)

    # Query records by field
    print("Querying records by field 'RACE = BLACK':")
    seal_system.query_by_field("RACE", "BLACK")

    print("\nQuerying records by field 'CHARGE 1 DESCRIPTION = DRIVING ON SUSPENDED LICENSE':")
    seal_system.query_by_field("CHARGE 1 DESCRIPTION", "DRIVING ON SUSPENDED LICENSE")

    # Retrieve a specific record
    print("\nRetrieving record with ID 1:")
    record = seal_system.retrieve_record(1)
    if record:
        print(f"Retrieved record: {record}")
    else:
        print("Record not found.")

    # Simulate attacks using the dataset
    attack_simulator = AttackSimulator(seal_system)
    print("\nSimulating access pattern attack:")
    attack_simulator.access_pattern_attack()

    print("\nSimulating query result attack:")
    attack_simulator.query_result_attack()

if __name__ == "__main__":
    main()
