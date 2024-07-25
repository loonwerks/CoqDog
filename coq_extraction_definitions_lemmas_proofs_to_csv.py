import re
import csv
import os
import zipfile
import pandas as pd

""" @Amer Tahat, senior Engineer, collins Aerospace, 
    coq defintions and lemmas and proofs to csv"""

# Regex patterns for lemmas, proofs, and definitions
lemma_pattern = re.compile(r"Lemma\s+(\w+)\s*:(.*?)(?:Proof|Qed|Defined|\.)(?!\s*with)", re.DOTALL)
proof_pattern = re.compile(r"Proof\s*.(.*?)(?:Qed|Defined)\.", re.DOTALL)
definition_pattern = re.compile(
    r"Definition\s+(\w+)([^.]*?)(?:\.\s*(?:\n|\Z|(?=\s*Proof)|(?=\s*Lemma)|(?=\s*Definition)))", re.DOTALL)


# Extract lemmas, definitions, and proofs using the patterns
def extract_items(file_content, lemma_pattern, definition_pattern, proof_pattern):
    lemmas = lemma_pattern.findall(file_content)
    definitions = definition_pattern.findall(file_content)
    proofs = proof_pattern.findall(file_content)
    return lemmas, definitions, proofs


# Function to integrate lemmas, definitions, and their proofs for CSV writing
def extract_all_items_to_csv(zip_path, csv_output_path, subdir, lemma_pattern, definition_pattern, proof_pattern):
    output_data = []

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Extract all the files into a temporary directory
        temp_extract_folder = "/path/to/extracted_directory"
        subdir_path = os.path.join(temp_extract_folder, subdir)

        # Process each Coq file within the subdirectory
        for coq_file in os.listdir(subdir_path):
            if coq_file.endswith('.v'):
                file_path = os.path.join(subdir_path, coq_file)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_content = f.read()

                lemmas, definitions, proofs = extract_items(file_content, lemma_pattern, definition_pattern,
                                                            proof_pattern)

                # Integrate lemmas, definitions, and their proofs
                for lemma, lemma_body in lemmas:
                    output_data.append([lemma, lemma_body.strip(), 1, "Lemma"])
                    # If proof exists for this lemma, add it
                    if proofs:
                        proof_body = proofs.pop(0)
                        output_data.append([lemma + "_proof", proof_body[0].strip(), 1, "Proof"])

                for definition_name, definition_body in definitions:
                    output_data.append([definition_name, definition_body.strip(), 2, "Definition"])
                    # If proof exists for this definition, add it
                    if proofs:
                        proof_body = proofs.pop(0)
                        output_data.append([definition_name + "_proof", proof_body[0].strip(), 2, "Proof"])

    # Write data to CSV
    with open(csv_output_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(["item-name", "item-body", "label_int", "label"])
        # Write extracted data
        for row in output_data:
            writer.writerow(row)

    return csv_output_path

# Example usage (paths will need to be updated):
# output_path_all_items = extract_all_items_to_csv('/path/to/src.zip', '/path/to/output.csv', 'src', lemma_pattern, definition_pattern, proof_pattern)
