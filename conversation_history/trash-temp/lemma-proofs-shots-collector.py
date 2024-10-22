import json
import re
import sys

def extract_lemmas_and_proofs(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    lemma_proofs = {}
    lemma_pattern = re.compile(r"Lemma\s+(\w+)\s*:(.*?)Proof\.(.*?)Qed\.", re.DOTALL)

    for item in data:
        if item['role'] == 'assistant':
            content = item['content']
            matches = re.findall(lemma_pattern, content)
            for match in matches:
                lemma_name, _, proof_body = match
                lemma_proofs[lemma_name.strip()] = proof_body.strip()

    return lemma_proofs

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py path_to_json_file")
        sys.exit(1)

    json_file_path = sys.argv[1]
    lemmas_and_proofs = extract_lemmas_and_proofs(json_file_path)

    for lemma, proof in lemmas_and_proofs.items():
        print(f"Lemma: {lemma}\nProof:\n{proof}\n")

if __name__ == "__main__":
    main()
