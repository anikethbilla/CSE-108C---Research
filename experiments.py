import os
import time
import random
import matplotlib.pyplot as plt
import pandas as pd
from SEAL import SEAL

def write_to_report(message, report_file):
    with open(report_file, 'a') as f:  # Use 'a' to append to the file
        f.write(message + "\n")  # Write the message and add a newline

# Function to read data from CSV file
def read_data_from_csv(file_path):
    df = pd.read_csv(file_path)
    data = df.to_dict('records')
    return data

# Experiment 1: Compare execution time for different alpha values
def experiment_1(data, report_file):
    alpha_values = [1, 2, 3, 4, 5, 6]  # Different alpha values to test
    execution_times = []
    print("Fixed x for this experiment: 2")
    write_to_report("Fixed x for this experiment: 2", report_file)

    for a in alpha_values:
        seal = SEAL(alpha=a)

        start_time = time.time()
        for record in data:
            seal.insert_record(record)
        end_time = time.time()

        execution_time = end_time - start_time
        execution_times.append(execution_time)
        print(f"Alpha = {a}, Execution Time = {execution_time:.2f} seconds")
        write_to_report(f"Alpha = {a}, Execution Time = {execution_time:.2f} seconds", report_file)


    # Plot results
    plt.plot(alpha_values, execution_times, marker='o')
    plt.xlabel('Alpha (α)')
    plt.ylabel('Execution Time (seconds)')
    plt.title('Execution Time vs Alpha (SEAL)')
    plt.grid(True)
    plt.savefig('experiment_1_alpha_vs_time.png')  # Save the plot as a file
    plt.close()  # Close the plot to free memory

# Experiment 2: Adjustable padding and its impact on performance
def experiment_2(data, report_file):
    a = 2  # Fixed alpha for this experiment
    print("Fixed alpha for this experiment: 2")
    write_to_report("Fixed alpha for this experiment: 2", report_file)
    x_values = [2, 3, 4, 5, 6, 7]  # Different padding factors to test
    execution_times = []

    for x_val in x_values:
        seal = SEAL(alpha=a, x=x_val)

        start_time = time.time()
        for record in data:
            seal.insert_record(record)
        end_time = time.time()

        execution_time = end_time - start_time
        execution_times.append(execution_time)
        print(f"Padding Factor (x) = {x_val}, Execution Time = {execution_time:.2f} seconds")
        write_to_report(f"Padding Factor (x) = {x_val}, Execution Time = {execution_time:.2f} seconds", report_file)

    # Plot results
    plt.plot(x_values, execution_times, marker='o')
    plt.xlabel('Padding Factor (x)')
    plt.ylabel('Execution Time (seconds)')
    plt.title('Execution Time vs Padding Factor (SEAL)')
    plt.grid(True)
    plt.savefig('experiment_2_padding_vs_time.png')  # Save the plot as a file
    plt.close()  # Close the plot to free memory

def experiment_3(seal, data, report_file):
    # Simulate attack: Adversary queries specific fields and uses statistical analysis
    field_name = "RACE"
    field_values = ["WHITE", "BLACK", "ASIAN", "HISPANIC"]
    success_count = 0
    total_queries = 0

    for field_value in field_values:
        # Adversary performs query
        padded_results = seal.query_by_field(field_name, field_value)
        print(padded_results)

        # Adversary uses statistical analysis to infer true result size
        # For example, using the mean padding size to estimate true size
        mean_padding_size = 0.1 * len(padded_results)
        inferred_size = len(padded_results) - mean_padding_size
        inferred_size = max(inferred_size, 0)  # Ensure non-negative

        true_size = sum(1 for record in data if record[field_name] == field_value)

        # Check if adversary's inference is correct within a tolerance
        tolerance = 2  # Allow some margin of error
        if abs(inferred_size - true_size) <= tolerance:
            success_count += 1
        total_queries += 1

    # Calculate success rate
    success_rate = (success_count / total_queries) * 100
    print(f"Attack 1: Volumetric Leakage Attack")
    write_to_report(f"Attack 1: Volumetric Leakage Attack", report_file)
    print("Alpha for this experiment: 5")
    print("X for this experiment: 4")
    write_to_report("Alpha for this experiment: 5", report_file)
    write_to_report("X for this experiment: 4", report_file)
    print(f"Adversary Success Rate: {success_rate:.2f}%")
    write_to_report(f"Adversary Success Rate: {success_rate:.2f}%", report_file)

def experiment_4(seal, data, report_file):
    # Simulate attack: Adversary observes access patterns and uses correlation analysis
    record_ids = [1, 2, 3]  # Example record IDs to access
    success_count = 0
    total_accesses = 0

    # Adversary builds a correlation matrix based on access patterns
    correlation_matrix = {}  # Key: (record_id1, record_id2), Value: correlation score

    for record_id in record_ids:
        # Adversary observes access to record
        record = seal.retrieve_record(record_id)

        # Adversary updates correlation matrix based on access patterns
        for other_id in record_ids:
            if other_id != record_id:
                key = tuple(sorted((record_id, other_id)))
                correlation_matrix[key] = correlation_matrix.get(key, 0) + 1

        # Adversary infers relationships based on correlation scores
        # For simplicity, assume records are related if correlation score is above a threshold
        threshold = 1  # Example threshold
        inferred_related = any(correlation_matrix.get(tuple(sorted((record_id, other_id))), 0) > threshold
                               for other_id in record_ids if other_id != record_id)

        true_related = True  # Assume records are related (for demonstration)

        # Check if adversary's inference is correct
        if inferred_related == true_related:
            success_count += 1
        total_accesses += 1

    # Calculate success rate
    success_rate = (success_count / total_accesses) * 100
    print(f"Attack 2: Access Pattern Leakage Attack")
    write_to_report(f"Attack 2: Access Pattern Leakage Attack", report_file)
    print("Alpha for this experiment: 5")
    print("X for this experiment: 4")
    write_to_report("Alpha for this experiment: 5", report_file)
    write_to_report("X for this experiment: 4", report_file)
    print(f"Adversary Success Rate: {success_rate:.2f}%")
    write_to_report(f"Adversary Success Rate: {success_rate:.2f}%", report_file)

# Run all experiments
if __name__ == "__main__":
    file_path = "Arrests_20250316.csv"  # Replace with the path to your CSV file
    report_file = "experiment_report.txt"  # File to store the report
    data = read_data_from_csv(file_path)

    # Delete the report file if it exists
    if os.path.exists(report_file):
        os.remove(report_file)
        print(f"Deleted existing report file: {report_file}")

    """
    print("Running Experiment 1: Varying Alpha")
    write_to_report("Running Experiment 1: Varying Alpha", report_file)
    experiment_1(data, report_file)

    print("\nRunning Experiment 2: Adjustable Padding")
    write_to_report("\nRunning Experiment 2: Adjustable Padding", report_file)
    experiment_2(data, report_file)
    """

    print("Setting Up SEAL database for experiments 3 and 4")
    seal = SEAL(alpha = 5, x = 4)

    # Insert records
    for record in data:
        seal.insert_record(record)

    print("\nRunning Experiment 3: Attack 1 (Volumetric Leakage)")
    write_to_report("\nRunning Experiment 3: Attack 1 (Volumetric Leakage)", report_file)
    experiment_3(seal, data, report_file)

    print("\nRunning Experiment 4: Attack 2 (Access Pattern Leakage)")
    write_to_report("\nRunning Experiment 4: Attack 2 (Access Pattern Leakage)", report_file)
    experiment_4(seal, data, report_file)
