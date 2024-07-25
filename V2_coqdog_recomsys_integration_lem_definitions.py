# -*- coding: utf-8 -*-
"""
Author: @Amer N.Tahat, Collins Aerospace 2023
Created: 14 May 2024
Description: V2 of CoqDog RecomSystem Integration of Lem, Proofs.
"""

import openai
import pandas as pd
import pickle
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())  # read local .env file
openai.api_key = os.getenv('OPENAI_API_KEY')
user_input = " "
k_input = int(1)

from openai.embeddings_utils import (
    get_embedding,
    distances_from_embeddings,
    tsne_components_from_embeddings,
    chart_from_components_3D, chart_from_components,
    indices_of_nearest_neighbors_from_distances,
)

# constants
EMBEDDING_MODEL = "text-embedding-ada-002"
df = pd.read_csv(
    './assets/coq_data.csv')  # chunks-def-lem-prf/chunck_1.csv')  #
# coq_data_updated_with_definitions.csv#coq_data_merge_def_lem_pr_updated.csv'), coq_contexts.csv')

"""### 2. Load data

Next, let's load the Coq_data news data and see what it looks like.
"""

n_examples = 10
print(df.shape)
df.head(n_examples)

# Display rows from n1 to n2
# df.iloc[0:10]

"""Let's take a look at those same examples, but not truncated by ellipses."""

# print the item-name, item-body, and label of each example
for idx, row in df.head(n_examples).iterrows():
    print("")
    print(f"item-name: {row['item-name']}")
    print(f"item-body: {row['item-body']}")
    print(f"Label: {row['label']}")

comment_2 = ("""3. Build cache to save embeddings Before getting embeddings for these lemmas-proof items, 
set up a cache to save the embeddings we generate. In general, it's a good idea to save embeddings so one can re-use 
them later. If we don't save them, we'll pay again each time you compute them again. The cache is a dictionary that 
maps tuples of `( text, model)` to an embedding, which is a list of floats. The cache is saved as a Python pickle 
file.""")

# establish a cache of embeddings to avoid recomputing
# cache is a dict of tuples (text, model) -> embedding, saved as a pickle file

# set path to embedding cache
embedding_cache_path = "./assets/recommendations_coq_embeddings_cache.pkl"
# another is:chunks-def-lem-prf/chunck_1.pkl

# load the cache if it exists, and save a copy to disk
try:
    embedding_cache = pd.read_pickle(embedding_cache_path)
except FileNotFoundError:
    embedding_cache = {}
with open(embedding_cache_path, "wb") as embedding_cache_file:
    pickle.dump(embedding_cache, embedding_cache_file)


# define a function to retrieve embeddings from the cache if present, and otherwise request via the API
def embedding_from_string(
        string: str,
        model: str = EMBEDDING_MODEL,
        embedding_cache=embedding_cache
) -> list:
    """Return embedding of given string, using a cache to avoid recomputing."""
    if (string, model) not in embedding_cache.keys():
        embedding_cache[(string, model)] = get_embedding(string, model)
        with open(embedding_cache_path, "wb") as embedding_cache_file:
            pickle.dump(embedding_cache, embedding_cache_file)
    return embedding_cache[(string, model)]


"""Let's check that it works by getting an embedding."""
# as an example, take the first Coq item-body ( lemma ) from the dataset
example_item_body = df["item-body"].values[5]
example_item_label = df["label"].values[5]
example_item_name = df["item-name"].values[5]

print(f"\nExample item-label: {example_item_label}")
print(f"\nExample item-name: {example_item_name}")
print(f"\nExample item-body: {example_item_body}")

# print the first 10 dimensions of the embedding
example_embedding = embedding_from_string(example_item_body)

print(f"\nExample embedding: {example_embedding[:10]}...")

comment = ("### 4. Recommend similar items (lemmas, proofs, etc..) based on embeddings\n"
           "\n"
           "To find similar items, let's follow a three-step plan:\n"
           "1. Get the similarity embeddings of all the item body\n"
           "2. Calculate the distance between a source lemma-item and all other items\n"
           "3. Print out the other items closest to the source item\n"
           "\n")


def indices_of_recommendations_from_source_string(
        strings: list[str],
        index_of_source_string: int,
        k_nearest_neighbors: int = 1,
        model=EMBEDDING_MODEL,
) -> list[int]:
    """ Here is what each parameter does:"
           "\n"
           "    strings: list[str]:\n"
           "    This is a list of strings from which the function will find the nearest neighbors.\n"
           "\n"
           "    index_of_source_string: int:\n"
           "This is the index of the string in the list strings that will be used as the source string.\n"
           "The function will find the nearest neighbors to this source string.\n"
           "\n"
           "    k_nearest_neighbors: int = 1:\n"
           "    This is an optional parameter that specifies how many nearest neighbors to find and print."
           "    If not provided, it defaults to 1\n"
           "\n" """
    # get embeddings for all strings
    embeddings = [embedding_from_string(string, model=model) for string in strings]
    # get the embedding of the source string
    query_embedding = embeddings[index_of_source_string]
    # get distances between the source embedding and other embeddings (function from embeddings_utils.py)
    distances = distances_from_embeddings(query_embedding, embeddings, distance_metric="cosine")
    # get indices of nearest neighbors (function from embeddings_utils.py)
    indices_of_nearest_neighbors = indices_of_nearest_neighbors_from_distances(distances)

    # print out source string
    query_string = strings[index_of_source_string]
    print(f"Source string: {query_string}")
    # print out its k nearest neighbors
    k_counter = 0
    for i in indices_of_nearest_neighbors:
        # skip any strings that are identical matches to the starting string
        if query_string == strings[i]:
            continue
        # stop after printing out k items
        if k_counter >= k_nearest_neighbors:
            break
        k_counter += 1

        # print out the similar strings and their distances
        print(
            f"""
        --- Recommendation #{k_counter} (nearest neighbor {k_counter} of {k_nearest_neighbors}) ---
        String: {strings[i]}
        Distance: {distances[i]:0.3f}"""
        )

    return indices_of_nearest_neighbors


def recommendations_list(
        strings: list[str],
        index_of_source_string: int,
        k_nearest_neighbors: int = 1,
        model=EMBEDDING_MODEL,
) -> list[str]:
    """Return a list of at most k nearest neighbors of a given string. with no logical circular output"""
    # get embeddings for all strings
    embeddings = [embedding_from_string(string, model=model) for string in strings]
    # get the embedding of the source string
    query_embedding = embeddings[index_of_source_string]
    # get distances between the source embedding and other embeddings (function from embeddings_utils.py)
    distances = distances_from_embeddings(query_embedding, embeddings, distance_metric="cosine")
    # get indices of nearest neighbors (function from embeddings_utils.py)
    indices_of_nearest_neighbors = indices_of_nearest_neighbors_from_distances(distances)

    # Print out the source string
    query_string = strings[index_of_source_string]
    print(f"Source string: {query_string} with index {index_of_source_string}")

    # Initialize the list of recommendations
    recommendations = []
    next_recommendation = " "
    pr_recommendations = []

    # Collect the k nearest neighbors
    k_counter = 0
    for i in indices_of_nearest_neighbors:
        # skip any strings that are identical matches to the query string
        if query_string == strings[i] or i >= index_of_source_string:
            continue
        # print(f"recommendation_{i}:\n")
        # stop after collecting k items
        if k_counter >= k_nearest_neighbors:
            break

        item_label = df.iloc[i]['label']
        item_name = df.iloc[i]['item-name']
        item_body = strings[i]
        distance = distances[i]

        recommendation = f"\n{item_label} {item_name} : {item_body}\nDistance: {distance:.3f}\n"
        recommendations.append(recommendation)
        if i + 1 < len(df) and 'proof' in df.iloc[i + 1]['label'].lower():
            item_proof = df.iloc[i + 1]['item-name'] + ": " + strings[i + 1]
            pr_item_label = df.iloc[i + 1]['label']
            pr_item_name = df.iloc[i + 1]['item-name']
            pr_item_body = strings[i + 1]
            pr_distance = distances[i + 1]

            next_recommendation = f"{pr_item_label}.\n{pr_item_body} Qed.\n"  # pr_Distance: {pr_distance:.3f}\n"  #
            # removed {pr_item_name}: {pr_item_label}.
            recommendations.append(next_recommendation)
        else:
            next_recommendation = "a recommendation context lemma's proof was not found.\n"
            continue
            # recommendations.append(next_recommendation)

        # Save the similar strings and their distances in the recommendations list recommendation = f"Recommendation
        # #{k_counter + 1} (nearest neighbor {k_counter + 1} of {k_nearest_neighbors}): String: {strings[i]},
        # Distance: {distances[i]:0.3f}" recommendations.append(recommendation)

        k_counter += 1

    return recommendations


import re


def find_k_nearest_neighbors_for_input_string(
        user_input: str,
        k_nearest_neighbors: int = 5,
        model=EMBEDDING_MODEL,
) -> list[str]:
    """
    This function takes a user input string, adds it to the dataframe,
    then calls the recommendations_list function to find its k nearest neighbors.
    """
    # Extract the part enclosed between `######` and `#####`
    enclosed_part_match = re.search(r"###(.*?)###", user_input, re.DOTALL)
    enclosed_part = enclosed_part_match.group(1).strip() if enclosed_part_match else ""
    if not enclosed_part:
        return ["No content found between ###### and #####."]

    # Extract lemma name and body from user input
    lemma_name = " "

    # Search for the lemma pattern within the extracted part
    # Adjusted regex pattern to capture the lemma name and body separately
    lemma_pattern = re.search(r"Lemma\s+([\w{}:]+)\s*:(.*?)(?:Proof|Qed|Defined|\.|$)", user_input, re.DOTALL)
      #re.search(r"Lemma\s+(\w+)\s*:(.\s*?)(?:Proof|Qed|Defined|\.|$)", user_input, re.DOTALL)

    if lemma_pattern:
        # Extracting the lemma name
        lemma_name = lemma_pattern.group(1)
        # Extracting the lemma body and stripping leading/trailing whitespace
        lemma_body = lemma_pattern.group(2).strip()
    # re.search(r"Lemma\s+(\w+)\s*:(.*?)(?:Proof|Qed|Defined|\.)(?!\s*with)", user_input,
    #          re.DOTALL)  # modified for multi-lines, it was "Lemma\s+\S+:\s+(.*?)\s+\."
    # one liner -> re.search(r"Lemma\s(.*?):", user_input), r"Lemma\s+\S+:\s+(.*?)\s+\."
    if lemma_pattern:
        lemma_name = lemma_pattern.group(1).strip()
        lemma_body = lemma_pattern.group(2).strip()
    else:
        return ["Invalid lemma format within the enclosed part."]
    
    if lemma_pattern:
        lemma_name = lemma_pattern.group(1).strip()
        print(f"lemma name is {lemma_name}_extracted.")
    else:
        lemma_name = 'Unknown'

    lemma_body = " "
    lemma_body = lemma_pattern.group(2).strip()  # re.search(rf"\s+{lemma_name}\s*:\s(.*?)", user_input, re.DOTALL)  #
    # lemma, lemma_body in lemmas added ? may need to
    # remove it test
    if lemma_body:
        lemma_body = lemma_pattern.group(2).strip()
    else:
        lemma_body = 'Unknown'

    global df

    # Check if the lemma body or name already exists in the dataframe
    if lemma_body in df['item-body'].values or lemma_name in df['item-name'].values:
        # index_of_user_input = df.index[df['item-body'] == lemma_body].tolist()[0]
        print(f"lemma body is {lemma_body} found")
        index_of_user_input = df.index[df['item-name'] == lemma_name].tolist()[0]
        print(f"lemma name is {lemma_name} found")

    else:
        # Add the user input to the dataframe
        new_row = {'item-name': lemma_name, 'item-body': lemma_body, 'label': 'Lemma', 'label_int': 1}
        df = df.append(new_row, ignore_index=True)

        # Get the index of the user input in the dataframe
        index_of_user_input = df.index[df['item-body'] == lemma_body].tolist()[0]

    # Call the recommendations_list function to find the k nearest neighbors
    recommendations = recommendations_list(
        strings=df['item-body'].fillna("").tolist(),
        index_of_source_string=index_of_user_input,
        k_nearest_neighbors=k_nearest_neighbors,
        model=model,
    )

    return recommendations


"""
5. Example recommendations
Let's look for lemmas similar to first lemma.
"""

# def num_tokens_from_string(string: str, encoding_name: str) -> int:
#    """Returns the number of tokens in a text string."""
#    encoding = tiktoken.get_encoding(encoding_name)
#    num_tokens = len(encoding.encode(string))
#    return num_tokens#

# num_tokens_from_string("tiktoken is great!", "cl100k_base")
# max_tokens = 8000

# Handle missing values and convert the "item-body" column to a list
article_descriptions = df["item-body"].fillna("").tolist()

# Check token count and truncate text if necessary for i in range(len(article_descriptions)): token_count =
# count_tokens(article_descriptions[i]) if token_count > max_tokens: article_descriptions[i] = article_descriptions[
# i][:max_tokens]  # Truncate the text to fit within the token limit

Coq_Copland_lemmas = recommendations_list(strings=article_descriptions, index_of_source_string=1, k_nearest_neighbors=5)

"""Pretty good! 5 of the 5 recommendations picked with bodies and names close from the input lemma.

Let's see how our recommender does on the first lemma's proofs similarities
"""

# coq_copland_proofs = recommendations_list(strings=article_descriptions, index_of_source_string=5,
#                                          k_nearest_neighbors=5)

"""From the printed distances, you can see that the #1 recommendation is much closer than all the others (0.11 vs 
0.14+). And the #1 recommendation looks  similar to the starting item. Pretty good!

## Appendix: Using embeddings in more sophisticated recommenders

A more sophisticated way to build a recommender system is to train a machine learning model that takes in tens or 
hundreds of signals, such as item popularity or user click data. Even in this system, embeddings can be a very useful 
signal into the recommender, especially for items that are being 'cold started' with no user data yet (e.g., 
a brand new product added to the catalog without any clicks yet).

## Appendix: Using embeddings to visualize similar articles

To get a sense of what our nearest neighbor recommender is doing, let's visualize the article embeddings. Although we 
can't plot the 2048 dimensions of each embedding vector, we can use techniques like [t-SNE](
https://en.wikipedia.org/wiki/T-distributed_stochastic_neighbor_embedding) or [PCA](
https://en.wikipedia.org/wiki/Principal_component_analysis) to compress the embeddings down into 2 or 3 dimensions, 
which we can chart.

Before visualizing the nearest neighbors, let's visualize all of the items bodies using t-SNE. Note that 
t-SNE is not deterministic, meaning that results may vary from run to run."""

# get embeddings for all items in the csv file
# embeddings = [embedding_from_string(string) for string in article_descriptions]
# compress the 2048-dimensional embeddings into 2 dimensions using t-SNE
"""tsne_components = tsne_components_from_embeddings(embeddings)
tsne_components_3 = tsne_components_from_embeddings(embeddings, n_components=3)
# get the article labels for coloring the chart
labels = df["label"].tolist()

chart_from_components(
    components=tsne_components,
    labels=labels,
    strings=article_descriptions,
    width=600,
    height=500,
    title="t-SNE 2D components of Copland Repo Coq lemmas and proofs",
)
"""
"""As you can see in the chart above, even the highly compressed embeddings do a good job of clustering Coq file 
items by category (lemmas, proofs, etc..). And it's worth emphasizing: this clustering is done with no knowledge of 
the labels themselves!

Also, if you look closely at the most egregious outliers, they are often due to mislabeling rather than poor 
embedding. For example, the majority of the blue Proof points in the red cluster appear to be actual lemmas' proofs.

Next, let's recolor the points by whether they are a source lemma, its nearest neighbors, or other.
"""

# chart_from_components_3D(
#    components=tsne_components_3,
#    labels=labels,
#    strings=article_descriptions,
#    width=1000,
#    height=1000,
#    title="t-SNE components of Coq files (lemmas and Proofs) in our Repo",
# )

# create labels for the recommended Coq file items ( lemmas, proofs, etc..)
"""
def nearest_neighbor_labels(
    list_of_indices: list[int],
    k_nearest_neighbors: int = 10
) -> list[str]:

     #Return a list of labels to color the k nearest neighbors.
    labels = ["Other" for _ in list_of_indices]
    source_index = list_of_indices[0]
    labels[source_index] = "Source"
    for i in range(k_nearest_neighbors):
        nearest_neighbor_index = list_of_indices[i + 1]
        labels[nearest_neighbor_index] = f"Nearest neighbor (top {k_nearest_neighbors})"
    return labels


Coq_Copland_labels = nearest_neighbor_labels(Coq_Copland_lemmas, k_nearest_neighbors=10)
coq_copland_proofs_labels = nearest_neighbor_labels(coq_copland_proofs, k_nearest_neighbors=10)

# a 2D chart of nearest neighbors of the example-item
"""
""""
chart_from_components(
    components=tsne_components,
    labels=Coq_Copland_labels,
    strings=article_descriptions,
    width=600,
    height=500,
    title="Nearest neighbors of the Coq item in the repo",
    category_orders={"label": ["Other", "Nearest neighbor (top n)", "Source"]},
)

"""
"""Looking at the 2D chart above, we can see that the lemma are somewhat close together inside of the lemma cluster. 
Interestingly, although the 5 nearest neighbors (red) were closest in high dimensional space, they are not the 
closest points in this compressed 2D space. Compressing the embeddings down to 2 dimensions discards much of their 
information, and the nearest neighbors in the 2D space don't seem to be as relevant as those in the full embedding 
space."""

# a 3D chart of nearest neighbors of the example-item
""""chart_from_components_3D(
    components=tsne_components_3,
    labels=Coq_Copland_labels,
    strings=article_descriptions,
    width=1000,
    height=1000,
    title="Nearest neighbors of a Coq lemma in the repo",
    category_orders={"label": ["Other", "Nearest neighbor (top 5)", "Source"]},
)

# a 2D chart of nearest neighbors of the proof of the first example-item
chart_from_components(
    components=tsne_components,
    labels=coq_copland_proofs_labels,
    strings=article_descriptions,
    width=600,
    height=500,
    title="Nearest neighbors of the first lemma's proof",
    category_orders={"label": ["Other", "Nearest neighbor (top 5)", "Source"]},
)

"""
"""For the first lemma's proof example, the 4 closest nearest neighbors in the full embedding space remain nearest 
neighbors in this compressed 2D visualization. The fifth is displayed as more distant, despite being closer in the 
full embedding space.

Should you want to, you can also make an interactive 3D plot of the embeddings with the function 
`chart_from_components_3D`. (Doing so will require recomputing the t-SNE components with `n_components=3`.)"""

# a 3D chart of nearest neighbors of the proof of the first example-item
"""chart_from_components_3D(
    components=tsne_components_3,
    labels=coq_copland_proofs_labels,
    strings=article_descriptions,
    width=1000,#600
    height=1000,#500
    title="Nearest neighbors of the first lemma's proof",
    category_orders={"label": ["Other", "Nearest neighbor (top n)", "Source"]},
)

"""

"""def main():
    # Your code here
    print("Script execution started...")
    # Example recommendations
    Coq_Copland_Recommended_Items_List = recommendations_list(strings=article_descriptions, index_of_source_string=1,
                                                              k_nearest_neighbors=5)
    Coq_Copland_lemmas_string = ''.join(Coq_Copland_Recommended_Items_List)
    print(Coq_Copland_lemmas_string)
    print("Script execution completed.")
"""


def main():
    global user_input

    print("Script execution started...")
    # Ask user for input
    user_input = input("Please input a lemma in the format 'Lemma lemma_name : lemma_body.':\n")

    global k_input
    K_input = input("Please input an int for max number of lemmas in recommendations':\n")
    k_input = int(K_input)
    # Example recommendations
    Coq_Copland_Recommended_Items_List = find_k_nearest_neighbors_for_input_string(user_input,
                                                                                   k_nearest_neighbors=k_input)

    Coq_Copland_lemmas_string = ' '.join(Coq_Copland_Recommended_Items_List)
    print(Coq_Copland_lemmas_string)
    print("Script execution completed.")
    # needs more work to integrate def recommendations


if __name__ == "__main__":
    main()
