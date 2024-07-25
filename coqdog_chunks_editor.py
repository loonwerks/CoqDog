"""
Author: @Amer N.Tahat, Collins Aerospace 2023
Created: November 2023
Description: This is chuncks editor. 2023 all rights reserved.
"""


import pandas as pd
import os

base_path = input("Enter the directory path where chunks will be saved: ")
file_path = input("Enter the path of your CSV file: ")


def chunk_csv_with_pandas(file_path, base_path, chunk_size):
    file_number = 1
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        file_path = os.path.join(base_path, f'chunk_{file_number}.csv')
        chunk.to_csv(file_path, index=False)
        file_number += 1


def main():
    # base_path = input("Enter the directory path where chunks will be saved: ")
    # file_path = input("Enter the path of your CSV file: ")
    chunk_size = int(input("Enter the chunk size (number of rows per chunk):  "))
    chunk_csv_with_pandas(file_path, base_path, chunk_size)


if __name__ == "__main__":
    main()
