import re
import pandas as pd

"""
Auther: @Amer N. Tahat, Collins Aerospace, This is a legacy code for the early desktop version of coqdog, used also for wepp app to extract lemmas and proofs. 2023 all rights reserved.
"""

# Regular expressions for the described patterns
re_imports = re.compile(r'^Require Import assets\.(?P<filename>\w+).$', re.MULTILINE)
re_definitions = re.compile(r'definition\s+(?P<definition>.*?)\.\n\n', re.DOTALL)
re_lemmas_proofs = re.compile(r'Lemma\s+(?P<lemma>.*?)Proof\.(?P<proof>.*?)(Qed\.|Defined\.)', re.DOTALL)

# Lists to store extracted content
imports = []
definitions = []
lemmas_proofs = []

# Iterate through Coq files and extract content
for file in os.listdir(assets_path):
    if file.endswith(".v"):
        with open(os.path.join(assets_path, file), 'r') as f:
            content = f.read()
            # Extract imports, definitions, and lemmas & proofs
            imports.extend(re_imports.findall(content))
            definitions.extend(re_definitions.findall(content))
            lemmas_proofs.extend(re_lemmas_proofs.findall(content))

# Convert the lists to a pandas DataFrame
df_coq = pd.DataFrame({
    'import': imports,
    'definition': definitions,
    'lemma_proof': lemmas_proofs
})

df_coq.head()
