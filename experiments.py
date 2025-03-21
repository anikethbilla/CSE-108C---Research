import time
import random
import matplotlib.pyplot as plt
import pandas as pd
from SEAL import SEAL

# Function to read data from CSV file
def read_data_from_csv(file_path):
    df = pd.read_csv(file_path)
    data = df.to_dict('records')
    return data

# Experiment 1: Compare execution time for different alpha values
def experiment_1(file_path):
    alpha_values = [1, 2, 3]  # Different alpha values to test
    execution_times = []

    for alpha in alpha_values:
        seal = SEAL(alpha=alpha)
        data = read_data_from_csv(file_path)

        start_time = time.time()
        for record in data:
            seal.insert_record(record)
        end_time = time.time()

        execution_time = end_time - start_time
        execution_times.append(execution_time)
        print(f"Alpha = {alpha}, Execution Time = {execution_time:.2f} seconds")

    # Plot results
    plt.plot(alpha_values, execution_times, marker='o')
    plt.xlabel('Alpha (α)')
    plt.ylabel('Execution Time (seconds)')
    plt.title('Execution Time vs Alpha (SEAL)')
    plt.grid(True)
    plt.savefig('experiment_1_alpha_vs_time.png')  # Save the plot as a file
    plt.close()  # Close the plot to free memory

# Experiment 2: Adjustable padding and its impact on performance
def experiment_2(file_path):
    alpha = 2  # Fixed alpha for this experiment
    x_values = [2, 4, 8]  # Different padding factors to test
    execution_times = []

    for x in x_values:
        seal = SEAL(alpha=alpha, x=x)
        data = read_data_from_csv(file_path)

        start_time = time.time()
        for record in data:
            seal.insert_record(record)
        end_time = time.time()

        execution_time = end_time - start_time
        execution_times.append(execution_time)
        print(f"Padding Factor (x) = {x}, Execution Time = {execution_time:.2f} seconds")

    # Plot results
    plt.plot(x_values, execution_times, marker='o')
    plt.xlabel('Padding Factor (x)')
    plt.ylabel('Execution Time (seconds)')
    plt.title('Execution Time vs Padding Factor (SEAL)')
    plt.grid(True)
    plt.savefig('experiment_2_padding_vs_time.png')  # Save the plot as a file
    plt.close()  # Close the plot to free memory

def experiment_3(file_path):
    alpha = 2
    seal = SEAL(alpha=alpha)
    data = read_data_from_csv(file_path)

    # Insert records
    for record in data:
        seal.insert_record(record)

    # Simulate attack: Adversary queries specific fields
    field_name = "RACE"
    field_values = ["WHITE", "BLACK", "ASIAN", "HISPANIC"]
    success_count = 0
    total_queries = 0

    for field_value in field_values:
        # Adversary performs query
        padded_results = seal.query_by_field(field_name, field_value)

        # Adversary attempts to infer true result size
        true_size = sum(1 for record in data if record[field_name] == field_value)
        inferred_size = len(padded_results)  # Adversary assumes no padding

        # Check if adversary's inference is correct
        if inferred_size == true_size:
            success_count += 1
        total_queries += 1

    # Calculate success rate
    success_rate = (success_count / total_queries) * 100
    print(f"Attack 1: Volumetric Leakage Attack")
    print(f"Adversary Success Rate: {success_rate:.2f}%")

# Function to simulate access pattern leakage attack
def experiment_4(file_path):
    alpha = 2
    seal = SEAL(alpha=alpha)
    data = read_data_from_csv(file_path)

    # Insert records
    for record in data:
        seal.insert_record(record)

    # Simulate attack: Adversary observes access patterns
    record_ids = [1, 2, 3]  # Example record IDs to access
    success_count = 0
    total_accesses = 0

    for record_id in record_ids:
        # Adversary observes access to record
        record = seal.retrieve_record(record_id)

        # Adversary attempts to infer relationships (e.g., related records)
        # For simplicity, assume adversary guesses randomly
        inferred_related = random.choice([True, False])
        true_related = True  # Assume records are related (for demonstration)

        # Check if adversary's inference is correct
        if inferred_related == true_related:
            success_count += 1
        total_accesses += 1

    # Calculate success rate
    success_rate = (success_count / total_accesses) * 100
    print(f"Attack 2: Access Pattern Leakage Attack")
    print(f"Adversary Success Rate: {success_rate:.2f}%")


# Run all experiments
if __name__ == "__main__":
    file_path = "Arrests_20250316.csv"  # Replace with the path to your CSV file

    print("Running Experiment 1: Varying Alpha")
    experiment_1(file_path)

    print("\nRunning Experiment 2: Adjustable Padding")
    experiment_2(file_path)

    print("\nRunning Experiment 3: Attack 1 (Volumetric Leakage)")
    experiment_3(file_path)

    print("\nRunning Experiment 4: Attack 2 (Access Pattern Leakage)")
    experiment_4(file_path)
