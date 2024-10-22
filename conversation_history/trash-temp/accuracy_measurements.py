import json
import csv
from coqdog_lemma_proofshots_json_dict import calculate_acc_w  # Import the function from your existing script


def process_json_and_write_csv(json_file_path, csv_file_path):
    # Read JSON data
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Open CSV file for writing
    with open(csv_file_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['lemma-name', 'acc_w', 'number of shots'])

        # Process each entry in JSON data
        for entry in data:
            lemma_name = entry['lemma-name']
            proofshots = entry['proof-shots']
            acc_w_results = calculate_acc_w(proofshots)
            number_of_shots = len(proofshots)

            # Write to CSV
            csvwriter.writerow([lemma_name, acc_w_results, number_of_shots])


def main():
    json_file_path = './conversation_history_proofshots.json'  # Replace with your JSON file path
    csv_file_path = './conversation_proofshots_acc_w.csv'  # Path for the output CSV file
    process_json_and_write_csv(json_file_path, csv_file_path)
    print(f"Processed data has been written to {csv_file_path}")
