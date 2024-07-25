import re
import json

""""
@Auther: Amer N. Tahat, Collins Aerospace, USA
@Date: 17 May 2024
@Description: under testing. 
"""


def extract_coqdog_proofs(log_file_path_1, output_json_path_2):
    # Define the pattern for extracting lemmas and proofs from CoqDog replies
    coqdog_pattern = re.compile(
        r"''' coq\s*CoqDog:\s*Proof\.(.*?)\b(?:Defined|Qed)\.\s*'''",
        re.DOTALL
    )

    with open(log_file_path, 'r') as file:
        log_content = file.read()

    # Find all matches for the pattern
    proofs = coqdog_pattern.findall(log_content)

    # Extract the matched proofs, ignoring the user input parts
    extracted_proofs = [match.strip() for match in proofs]

    # Create a dictionary for JSON output
    proofs_dict = {
        f"Proof_{idx + 1}": proof for idx, proof in enumerate(extracted_proofs)
    }

    # Write the dictionary to a JSON file
    with open(output_json_path, 'w') as json_file:
        json.dump(proofs_dict, json_file, indent=4)

    return proofs_dict


# Example usage:
log_file_path = 'path_to_log_file.txt'
output_json_path = 'extracted_proofs.json'
extracted_proofs_dict = extract_coqdog_proofs(log_file_path, output_json_path)

# Print the JSON dictionary
print(json.dumps(extracted_proofs_dict, indent=4))
