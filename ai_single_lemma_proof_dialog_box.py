import tkinter as tk
from tkinter import filedialog
from predict_a_proof_for_single_lemma import add_proof_to_single_lemma

"""
Auther: @Amer N. Tahat, Collins Aerospace, This is a legacy code for the early desktop version of coqdog. 2023 all rights reserved.
"""


def browse_input_file():
    file_path = filedialog.askopenfilename()
    input_file_entry.delete(0, tk.END)
    input_file_entry.insert(0, file_path)


def browse_output_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".v")
    output_file_entry.delete(0, tk.END)
    output_file_entry.insert(0, file_path)


def submit_form():
    # api_key = "My_OpenAI_Key"
    api_key = api_key_entry.get()
    input_file_path = input_file_entry.get()
    output_file_path = output_file_entry.get()
    lemma_name = lemma_name_entry.get()
    add_proof_to_single_lemma(api_key, input_file_path, output_file_path, lemma_name)
    root.destroy()


def show_submit_form_dialog():
    global root
    root = tk.Tk()
    root.title("Add AI-Proof to a Single Lemma")

    api_key_label = tk.Label(root, text="API Key:")
    api_key_label.grid(row=0, column=0, sticky="e")
    global api_key_entry
    api_key_entry = tk.Entry(root, width=40)
    api_key_entry.grid(row=0, column=1)

    input_file_label = tk.Label(root, text="Input File:")
    input_file_label.grid(row=1, column=0, sticky="e")
    global input_file_entry
    input_file_entry = tk.Entry(root, width=40)
    input_file_entry.grid(row=1, column=1)
    input_file_button = tk.Button(root, text="Browse", command=browse_input_file)
    input_file_button.grid(row=1, column=2)

    output_file_label = tk.Label(root, text="Output File:")
    output_file_label.grid(row=2, column=0, sticky="e")
    global output_file_entry
    output_file_entry = tk.Entry(root, width=40)
    output_file_entry.grid(row=2, column=1)
    output_file_button = tk.Button(root, text="Browse", command=browse_output_file)
    output_file_button.grid(row=2, column=2)

    lemma_name_label = tk.Label(root, text="Lemma Name:")
    lemma_name_label.grid(row=3, column=0, sticky="e")
    global lemma_name_entry
    lemma_name_entry = tk.Entry(root, width=40)
    lemma_name_entry.grid(row=3, column=1)

    start_marker_label = tk.Label(root, text="Start marker:")
    start_marker_label.grid(row=4, column=0, sticky="e")
    global start_marker_entry
    start_marker_entry = tk.Entry(root, width=40)
    start_marker_entry.grid(row=4, column=1)

    stop_marker_label = tk.Label(root, text="Stop marker:")
    stop_marker_label.grid(row=5, column=0, sticky="e")
    global stop_marker_entry
    stop_marker_entry = tk.Entry(root, width=40)
    stop_marker_entry.grid(row=5, column=1)

    submit_button = tk.Button(root, text="Submit", command=submit_form)
    submit_button.grid(row=6, column=1, pady=10)

    root.mainloop()


if __name__ == "__main__":
    show_submit_form_dialog()
