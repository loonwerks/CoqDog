"""
Author: @Amer N.Tahat, Collins Aerospace,
Description: CoqDog-Team Webservice User Friendly WebApp
Date : 13 June 2024
"""
import os
import re
import json
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import openai
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
import zipfile
import base64
import subprocess
import shutil
from V2_coqdog_recomsys_integration_lem_definitions import find_k_nearest_neighbors_for_input_string

# Import git operations
from git_actions import git_commit_push

load_dotenv(find_dotenv())
openai.api_key = os.getenv('OPENAI_API_KEY')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Add a component to the layout for displaying the token count
token_display = html.Div(id='token-count', style={"margin-top": "20px"})

app.layout = dbc.Container([
    html.Footer([
        html.P([
            html.Span("", style={"font-size": "14px"}),  # This is the copyright symbol
            html.Span("©", style={"font-size": "14px"}),
            "Proof of Concept Web Service"
        ])
    ], style={
        "text-align": "center",
        "background-color": "#f1f1f1",
        "padding": "10px",
        "margin-bottom": "20px"
    }),
    html.Div([
        html.Img(src="assets/coqdog-5.png", id="app-logo", style={
            "display": "inline-block",
            "height": "50px",
            "vertical-align": "middle"
        }),
        html.H1("CoqDog-Team", style={
            "display": "inline-block",
            "vertical-align": "middle",
            "margin-left": "20px"
        })
    ]),
    dcc.Textarea(id='user-input', style={"width": "100%", "height": 200}, placeholder='Enter your context...'),
    dbc.Input(id='initial-file', placeholder='Enter the start file (e.g., file_name)', type='text'),
    html.Div([
        dbc.Button("Submit", id='submit-button', color="primary", className="mr-1"),
        dbc.Button("Save History", id='copy-button', color="secondary", className="mr-1"),
        dcc.RadioItems(
            id='include-upload-folder',
            options=[
                {"label": "Enable Upload Folder", "value": "yes"},
                {"label": "Disable Upload Folder", "value": "no"},
            ],
            value="no",
            inline=True,
        ),
        dcc.Upload(
            id='upload-folder',
            children=dbc.Button("Upload Folder", color="secondary", className="mr-1"),
            multiple=False
        )
    ], style={"display": "flex", "align-items": "center"}),
    html.Div(id='upload-status'),
    html.Div([
        dcc.RadioItems(
            id='include-requirements-chain',
            options=[
                {"label": "Include requirement chain", "value": "yes"},
                {"label": "Don't include requirement chain", "value": "no"},
            ],
            value="no",
            inline=True
        )
    ], style={"display": "flex", "align-items": "center", "margin-top": "10px"}),
    html.Div(id='copy-status'),
    html.Div(id='response-output', style={"white-space": "pre-line", "margin-top": "20px"}),
    dbc.RadioItems(
        id="model-choice",
        options=[
            {"label": "GPT-4o multi-modal (128k tk)", "value": "gpt-4o"},
            {"label": "GPT-4-Turbo (128k tk)", "value": "gpt-4-turbo"},
            {"label": "GPT-4 (8k tk)", "value": "gpt-4-0613"},
            {"label": "GPT-3.5 (16K tk)", "value": "gpt-3.5-turbo-16k-0613"},
        ],
        value="gpt-4o",
        inline=True
    ),
    dbc.RadioItems(
        id="display-mode",
        options=[
            {"label": "Full History", "value": "full"},
            {"label": "Last Response", "value": "last"},
        ],
        value="full",
        inline=True
    ),
    dcc.RadioItems(
        id="use-recommendation",
        options=[
            {"label": "Use Copland Customized Recommendation System", "value": "yes"},
            {"label": "Don't Use Recommendation System", "value": "no"},
        ],
        value="no",
        inline=True
    ),
    html.Div(id='conversation-history', style={'display': 'none'}, children="[]"),
    html.Div(id='context-added', style={'display': 'none'}, children="false"),
    token_display,
    dbc.Input(id='commit-message', placeholder='Enter commit message', type='text'),
    dbc.Button("Git Commit and Push", id='git-commit-push', color="success", className="mr-1"),
    html.Div(id='push-status', style={"margin-top": "20px"})
])


# Function to read the start file content
def read_start_file_content(file_path):
    with open(file_path, 'r') as f:
        file_content = f.read()

    start_pattern = r"\(\*###Start-Here###\*\)"
    stop_pattern = r"\(\*###Stop-Here###\*\)"

    match = re.search(f"{start_pattern}(.*?){stop_pattern}", file_content, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        print(f"Unable to find content between {start_pattern} and {stop_pattern} in {file_path}")
        return ""


# Function to read generic file content
def read_generic_file_content(file_path):
    with open(file_path, 'r') as f:
        return f.read()


# Function to handle the requires statements in files.
def handle_requires(file_path, project_files, files_to_check):
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('Require'):
                required_files = [item.strip() for item in line.replace('Require', '').replace('.', '').split() if item]
                for required_file in required_files:
                    if required_file in project_files:
                        files_to_check.append(required_file)


# Function to concatenate all imported files based on the start file
def concatenate_imports(start_file, project_files, folder_path):
    processed_files = set()
    context = ""
    files_to_check = [start_file]

    while files_to_check:
        current_file = files_to_check.pop()
        if current_file in processed_files:
            continue
        processed_files.add(current_file)

        file_path = os.path.join(folder_path, current_file + ".v")
        if not os.path.exists(file_path):
            print(rf'{current_file} is not in _CoqProject')
            continue

        if current_file == start_file:
            content = read_start_file_content(file_path)
        else:
            content = read_generic_file_content(file_path)
        context += content
        handle_requires(file_path, project_files, files_to_check)

    return context


# Function to read .v files listed in _CoqProject file
def read_project_files(directory):
    coq_project_file = os.path.join(directory, "_CoqProject")
    if not os.path.exists(coq_project_file):
        return []

    project_files = []
    with open(coq_project_file, 'r') as file:
        for line in file:
            filename = line.strip()
            if filename.endswith(".v"):
                project_files.append(filename[:-2])
    return project_files


# The highlighting function
def highlight_keywords(text):
    keywords = ["Lemma", "Proof", "Qed"]
    elements = []
    start = 0
    for keyword in keywords:
        while (idx := text.find(keyword, start)) != -1:
            if idx != start:
                elements.append(text[start:idx])
            elements.append(html.Span(keyword, style={'color': 'purple'}))
            start = idx + len(keyword)
    elements.append(text[start:])
    return elements


# Prepare display text
def format_display_text(conversation_history, display_mode):
    if display_mode == "full":
        display_elements = []
        for message in conversation_history:
            if message['role'] == 'user':
                label = html.Span("User:", style={'color': 'blue'})
            elif message['role'] == 'assistant':
                label = html.Span("CoqDog:", style={'color': 'red'})
            else:
                continue
            display_elements.append(label)
            display_elements.extend(highlight_keywords(" " + message['content'] + "\n\n"))
        return display_elements
    else:
        last_message = conversation_history[-1]
        if last_message['role'] == 'user':
            label = html.Span("User:", style={'color': 'blue'})
        else:
            label = html.Span("CoqDog:", style={'color': 'red'})
        return [label, " " + last_message['content']]


@app.callback(
    Output('response-output', 'children'),
    Output('conversation-history', 'children'),
    Output('user-input', 'value'),
    Output('token-count', 'children'),
    State('context-added', 'children'),
    State('model-choice', 'value'),
    State('conversation-history', 'children'),
    State('display-mode', 'value'),
    State('use-recommendation', 'value'),
    Input('submit-button', 'n_clicks'),
    State('user-input', 'value'),
    State('initial-file', 'value'),
    State('include-requirements-chain', 'value')
)
def ask_coqdog(context_added, model_choice, conversation_history_json, display_mode, use_recommendation, n_clicks,
               user_input, initial_file, include_requirements_chain):
    user_input_original = user_input
    if n_clicks is None:
        return "Enter your context and press 'Submit' to get a response from CoqDog.\n " \
               "If the context is large you can select copland recommendation system ", "[]", user_input, f"Tokens used: {0}"

    conversation_history = json.loads(conversation_history_json)
    conversation_history_text = " ".join(msg['content'] for msg in conversation_history)

    if not conversation_history:
        conversation_history = [{'role': 'system',
                                 'content': """ You are a proof assistant of coq theorem prover, an automated service\ 
                                 to build proofs for lemmas in a coq file. \ You first ask the user for the context \ 
                                 such as definitions, or useful lemmas, hints, or modifiers. \ You collect all context.\ 
                                 If the user is using gpt-4o, you may process images and display them. Remember to use\
                                  a previously proved lemma in the conversation to prove a new lemma in the\ 
                                  conversation if applicable. You respond in the following style:
                                  \ lemma lemma-name: lemma-body.\n Proof. step_1\n, ...step_n\n. Qed.\n 
                                  unless directed\ to close the proof with the key word defined.\ """}]
        context_added = "false"

    upload_directory = "uploaded_dir"
    subdirectories = [os.path.join(upload_directory, d) for d in os.listdir(upload_directory) if
                      os.path.isdir(os.path.join(upload_directory, d))]
    if not subdirectories:
        return "No subdirectory found in the uploaded directory.", json.dumps(
            conversation_history), user_input, f"Tokens used: {0}"

    target_directory = subdirectories[0]

    project_files = read_project_files(target_directory)

    if include_requirements_chain == "yes" and initial_file and context_added == "false":
        file_context = concatenate_imports(initial_file, project_files, target_directory)
        if file_context:
            user_input = f"{file_context}\n{user_input}"
        context_added = "true"
    elif include_requirements_chain == "no" and initial_file and context_added == "false":
        user_input = user_input_original

    if use_recommendation == 'yes':
        context_list = find_k_nearest_neighbors_for_input_string(user_input_original, 3)
        context_list = [lemma for lemma in context_list if lemma not in conversation_history_text]
        context = ' '.join(context_list)
        if include_requirements_chain == "yes" and context_added == "true":
            user_input = f"Given the context {file_context} and\n {context}, and \n {user_input_original}\n - remember" \
                         f"to use any previously proved lemmas in the context to prove the lemma when applicable."
        elif include_requirements_chain == "no":
            user_input = f"Given the context \n {context}, \n {user_input_original} \n - remember to use " \
                         f"any previously proved lemmas in the context to prove the lemma when " \
                         f"applicable."

    conversation_history.append({'role': 'user', 'content': user_input})
    response = get_completion_from_messages(conversation_history, model=model_choice).choices[0].message["content"]
    tokens_used = get_completion_from_messages(conversation_history, model=model_choice)['usage']['total_tokens']

    conversation_history.append({'role': 'assistant', 'content': response})
    save_conversation_history_to_file(conversation_history)
    display_text = format_display_text(conversation_history, display_mode)

    warning = ""
    if 7000 <= tokens_used < 8000 and model_choice == "gpt-4-0613":
        warning = " Warning: Tokens used are higher than 7000. If you are using GPT-4 8k, switch to GPT-3.5 16K."

    return display_text, json.dumps(conversation_history), "", f"Tokens used : {tokens_used}" + warning


@app.callback(
    Output('copy-status', 'children'),
    Input('copy-button', 'n_clicks'),
    prevent_initial_call=True
)
def copy_conversation_history(n_clicks):
    if n_clicks is None:
        return "Click the button to copy the conversation history."

    source_file = 'conversation_history/conversation_history.json'
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destination_dir = 'temp_history'
    destination_file = f'{destination_dir}/conversation_history_{timestamp}.json'

    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    current_directory = os.getcwd()  # Save the current working directory

    try:
        subprocess.run(['cp', source_file, destination_file], check=True)
        os.chdir(current_directory)  # Restore the original working directory
        return f"Successfully copied to {destination_file}"
    except subprocess.CalledProcessError:
        os.chdir(current_directory)  # Restore the original working directory
        return "Error occurred while copying the file."


@app.callback(
    Output('upload-folder', 'style'),
    [Input('include-upload-folder', 'value')]
)
def toggle_upload_visibility(include_upload):
    if include_upload == "yes":
        return {'display': 'block', 'margin-left': '10px'}
    else:
        return {'display': 'none'}


@app.callback(
    Output('upload-status', 'children'),
    [Input('upload-folder', 'contents')],
    [State('upload-folder', 'filename'), State('include-upload-folder', 'value')]
)
def handle_upload(contents, filename, include_upload):
    if contents is None or include_upload != "yes":
        return "Upload a folder containing the necessary files."

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    upload_directory = "uploaded_dir"
    if not os.path.exists(upload_directory):
        os.makedirs(upload_directory)

    zip_path = os.path.join(upload_directory, filename)
    with open(zip_path, "wb") as file:
        file.write(decoded)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(upload_directory)

    return "Folder uploaded and extracted successfully!"


def get_completion_from_messages(messages, temperature=0.7, model="gpt-4-0613"):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response


def save_conversation_history_to_file(conversation_history, dir_name='conversation_history'):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    file_name = f"{dir_name}/conversation_history.json"
    json_string = json.dumps(conversation_history, indent=4)
    with open(file_name, 'w') as file:
        file.write(json_string)


@app.callback(
    Output('push-status', 'children'),
    Input('git-commit-push', 'n_clicks'),
    State('commit-message', 'value'),
    prevent_initial_call=True
)
def commit_and_push(n_clicks, commit_message):
    if n_clicks is not None:
        current_directory_1 = os.getcwd()  # Save the current working directory
        try:
            success, message = git_commit_push(commit_message)
            os.chdir(current_directory_1)  # Restore the original working directory
            return message
        except Exception as e:
            os.chdir(current_directory_1)  # Restore the original working directory
            return f"An error occurred: {e}"


if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0')
