import re
import json

def extract_lemmas_and_proofs(file_path):
    lemmas = {}
    current_lemma = None
    collecting = False
    proof_lines = []

    # Regular expression to match the lemma definition line
    lemma_start_pattern = r"CoqDog:\s+Lemma\s+([a-zA-Z0-9_]+)\s*:"
    # Patterns to detect the start and end of proofs
    proof_start_pattern = "Proof."
    proof_end_patterns = ["Qed.", "Defined."]

    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith("CoqDog:"):
                # Check if a new lemma starts
                start_match = re.search(lemma_start_pattern, line)
                if start_match:
                    # Save the previous lemma if there was one collecting
                    if current_lemma and proof_lines:
                        proof_text = '\n'.join(proof_lines).strip()
                        if current_lemma in lemmas:
                            lemmas[current_lemma]["proof-shots"].append(proof_text)
                        else:
                            lemmas[current_lemma] = {"lemma-name": current_lemma, "proof-shots": [proof_text]}
                    # Reset for the new lemma
                    current_lemma = start_match.group(1)
                    collecting = False
                    proof_lines = []

            # Check for the start of a proof
            elif collecting or proof_start_pattern in line:
                collecting = True
                proof_lines.append(line.replace(proof_start_pattern, "").strip())  # Remove the "Proof." marker

            # Check for the end of a proof
            if any(end_pattern in line for end_pattern in proof_end_patterns):
                collecting = False
                proof_text = '\n'.join(proof_lines).strip()
                if current_lemma in lemmas:
                    lemmas[current_lemma]["proof-shots"].append(proof_text)
                else:
                    lemmas[current_lemma] = {"lemma-name": current_lemma, "proof-shots": [proof_text]}
                proof_lines = []

    # Convert the dictionary values to a list of dictionaries
    lemmas_list = list(lemmas.values())
    return lemmas_list

def main():
    file_name = input("Enter the file name: ")
    lemmas = extract_lemmas_and_proofs(file_name)
    
    # Convert the list of dictionaries to JSON
    json_output = json.dumps(lemmas, indent=4)

    # Save to a file
    output_file = "lemmas.json"
    with open(output_file, "w") as file:
        file.write(json_output)

    print(f"Lemmas and proofs have been saved to '{output_file}'")

if __name__ == "__main__":
    main()
