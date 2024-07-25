import os
import openai
from dotenv import load_dotenv, find_dotenv

"""
Auther: @Amer N. Tahat, Collins Aerospace, This is a legacy code for the early desktop version of coqdog. 2023 all rights reserved.
"""

_ = load_dotenv(find_dotenv())  # read local .env file

openai.api_key = os.getenv('OPENAI_API_KEY')

context = [{'role': 'system', 'content': """
You are a proof assistant of coq theorem prover, an automated service to build proofs for lemmas in a coq file. \
You first ask the user for the context such as definitions, or given lemmas, hints, or modifiers \
You wait to collect all context \
ask one last time if the user wants to add anything else. \
make sure that the modifiers are in the below white list\
You respond in the following style lemma lemma-name: lemma-body.\n Proof. step_1\n, ...step_n\n. Qed.\n unless directed\
to close the proof with the key word defined.\
"""}]


def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0.0):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message["content"]


def main():
    while True:
        user_input = input("User: ")
        if user_input.lower() == "quit":
            break
        context.append({'role': 'user', 'content': user_input})
        response = get_completion_from_messages(context)
        context.append({'role': 'assistant', 'content': response})
        print("Assistant: ", response)

    messages_1 = context.copy()
    messages_1.append(
        {'role': 'system', 'content': 'create a json summary of the previous lemma and proof.\
         Itemize the proof for each lemma\
        The fields should be 1) lemma, include lemma name and body 2) proof \
          3) ends_statement, like Qed. or defined '},
    )
    response = get_completion_from_messages(messages_1, temperature=0.7)
    print(response)


if __name__ == "__main__":
    main()
