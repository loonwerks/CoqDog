import re
import csv
import os
""" extract items from coq to csv and clean comments and spaces """
# Regular expressions for extraction
lemma_pattern = re.compile(r"Lemma\s+(\w+)\s*:(.*?)(?:Proof|Qed)\.", re.DOTALL)
proof_pattern = re.compile(r"Proof\s*.(.*?)(?:Qed|Defined)\.", re.DOTALL)


# Extract lemmas and proofs from a Coq file content
def extract_lemmas_and_proofs(file_content):
    lemmas = lemma_pattern.findall(file_content)
    proofs = proof_pattern.findall(file_content)
    return lemmas, proofs


# Preprocess Coq file content: Remove comments and unnecessary white spaces
def preprocess_content(file_content):
    # Remove comments
    no_comments = re.sub(r"\(\*.*?\*\)", "", file_content, flags=re.DOTALL)
    # Remove excessive whitespaces
    cleaned_content = re.sub(r"\s+", " ", no_comments).strip()
    return cleaned_content


# Extract information from a Coq file
def extract_info(file_content):
    cleaned_content = preprocess_content(file_content)
    lemmas, proofs = extract_lemmas_and_proofs(cleaned_content)
    return lemmas, proofs


# List of specified Coq files to process
specified_files = [...]  # List of file names goes here

# Output CSV file path
csv_output_path = '/path/to/output/coq_data.csv'  # Specify your output path here

# Extracting data and writing to CSV
with open(csv_output_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Write header
    writer.writerow(["item-name", "item-body", "label_int", "label"])

    # Process each specified file
    for coq_file in specified_files:
        file_path = os.path.join('/path/to/coq/files', coq_file)  # Specify your path here
        try:
            # Load file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_content = f.read()
            # Extract information
            lemmas, proofs = extract_info(file_content)
            # Write to CSV
            for lemma, proof in zip(lemmas, proofs):
                lemma_name, lemma_body = lemma
                proof_body = proof
                # Write lemma and proof in CSV
                writer.writerow([lemma_name, lemma_body.strip(), 1, "Lemma"])
                writer.writerow([lemma_name + "_proof", proof_body.strip(), 1, "Proof"])
        except Exception as e:
            print(f"Error processing file {coq_file}: {str(e)}")