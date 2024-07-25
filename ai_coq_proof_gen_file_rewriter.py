import os
import re
import openai
from dotenv import load_dotenv, find_dotenv

"""
Auther: @Amer N. Tahat, Collins Aerospace, This is a legacy code for the early desktop version of coqdog. 2023 all rights reserved.
"""

_ = load_dotenv(find_dotenv())

openai.api_key = os.getenv('OPENAI_API_KEY')


# Initialize OpenAI API with your key
# . openai.api_key = 'YOUR_OPENAI_API_KEY'


def extract_lemmas_and_proofs(file_path):
    with open(file_path, 'r') as f:
        contents = f.read()

    #lemma_pattern = r'Lemma\s+(?P<name>[\w]+)\s*:\s*(?P<context>.*?)\s*Proof\.\s*(?P<proof>.*?)(' \
    #                r'?P<end_statement>\s*Qed\.|\s*Defined\.)'

    #lemma_pattern = r'Lemma\s+(?P<name>[\w{}]+)\s*:\s*(?P<context>.*?)\s*Proof\.\s*(?P<proof>.*?)(' \
    #               r'?P<end_statement>\s*Qed\.|\s*Defined\.)'

    lemma_pattern = r'Lemma\s+(?P<name>[\w]+\{.*?\})?\s*:\s*(?P<context>.*?)\s*Proof\.\s*(?P<proof>.*?)(' \
                    r'?P<end_statement>\s*Qed\.|\s*Defined\.)'

    #lemma_pattern = r'Lemma\s+(?P<name>[\w\'_]+(\{.*?\})?)\s*:\s*(?P<context>.*?)\s*Proof\.\s*(?P<proof>.*?)(' \
    #                r'?P<end_statement>\s*Qed\.|\s*Defined\.)'

    matches = re.findall(lemma_pattern, contents, re.DOTALL)

    lemmas = ['Lemma {} : {}'.format(name, context) for name, context, _, _ in matches]
    proofs = [('Proof.', proof, end_statement) for _, _, proof, end_statement in matches]

    return lemmas, proofs


def generate_new_proofs_completion_models(lemmas):
    new_proofs = []

    for lemma in lemmas:
        prompt = f"Prove the following lemma:\n{lemma}"
        response = openai.Completion.create(
            engine="text-davinci-003",  # We can adjust as per our subscription
            prompt=prompt,
            max_tokens=500
        )
        new_proofs.append(response.choices[0].text.strip())

    return new_proofs


def generate_new_proofs(lemmas):
    new_proofs = []

    for lemma in lemmas:
        messages = [
            {"role": "system", "content": "You are a helpful assistant of coq prover."},
            {"role": "user", "content": f"Prove the following lemma:\n{lemma} in coq. write the proof as coq proof scripts only. Don't add illustrations"},
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # gpt-4 We can adjust as per our subscription
            messages=messages
        )

        # Extract the proof from the response
        proof_text = response['choices'][0]['message']['content']
        proof_pattern = re.compile(r"(Proof.)(.+?)(Qed.|Defined.|Admitted.)", re.DOTALL)
        match = proof_pattern.search(proof_text)

        if match:
            # If a proof was found, append it to the list of new proofs
            new_proofs.append(match.group(0).strip())
            print(match.group(0).strip())
        else:
            # If no proof was found, add a placeholder or handle this case appropriately
            new_proofs.append("No proof found.")
            print("No proof found.")

    return new_proofs


def rewrite_file(file_path, lemmas, old_proofs, new_proofs):
    with open(file_path, 'r') as f:
        contents = f.read()

    for lemma, old_proof, new_proof in zip(lemmas, old_proofs, new_proofs):
        old_proof_text = old_proof[1].strip()
        stripped_new_proof_text = new_proof.replace('Proof.', '').replace('Qed.', '')
        contents = contents.replace(old_proof_text, f"(* {old_proof_text} *)\n{stripped_new_proof_text}")

    with open(file_path, 'w') as f:
        f.write(contents)


def process_directory(directory_path):
    for filename in os.listdir(directory_path):

        if filename.endswith(".v"):
            file_path = os.path.join(directory_path, filename)
            print(file_path)
            lemmas, proofs = extract_lemmas_and_proofs(file_path)
            new_proofs = generate_new_proofs(lemmas)
            rewrite_file(file_path, lemmas, proofs, new_proofs)


def main():
    # Replace with directory input path
    dir_path = "/home/amertahat/AI-powered-proof-manager-coq-assist/copland-src-compiled/src"
    process_directory("/home/amertahat/AI-powered-proof-manager-coq-assist/test")


if __name__ == "__main__":
    main()
