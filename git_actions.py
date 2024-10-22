import subprocess
import shutil
import os
import json

CONFIG_FILE = 'config.json'


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    return {}


def save_config(config):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent=4)


def clone_repo(repo_url, method='https'):
    try:
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        # Check if the repo already exists locally and remove it if it does
        if os.path.exists(repo_name):
            shutil.rmtree(repo_name)

        if method == 'gh':
            clone_command = ['gh', 'repo', 'clone', repo_url]
        else:
            clone_command = ['git', 'clone', repo_url]

        subprocess.run(clone_command, check=True)
        return repo_name
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Error cloning the repository: {e}")


def copy_folders(folders, repo_name):
    try:
        for folder in folders:
            dest = os.path.join(repo_name, os.path.basename(folder))
            if os.path.exists(dest):
                shutil.rmtree(dest)
            shutil.copytree(folder, dest)
        return True
    except Exception as e:
        raise ValueError(f"Error copying folders: {e}")


def add_commit_push(commit_message):
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        subprocess.run(['git', 'push'], check=True)
        return True, "  temp history folder have been pushed to the remote repository successfully."
    except subprocess.CalledProcessError as e:
        return False, f"Error pushing to the repository: {e}"


def limit_commit_message_length(commit_message, word_limit=50):
    words = commit_message.split()
    if len(words) > word_limit:
        commit_message = ' '.join(words[:word_limit])
    return commit_message


def filter_alphabetic_characters(commit_message):
    return ' '.join(filter(str.isalpha, commit_message.split()))


def git_commit_push(commit_message):
    folders = ["proof_analysis", "temp_history"]
    config = load_config()
    repo_url = config.get('repo_url')
    method = config.get('method')
    current_directory = os.getcwd()  # Save the current working directory
    try:
        repo_name = clone_repo(repo_url, method)
        if not repo_name:
            raise ValueError("Failed to clone the repository.")
        if not copy_folders(folders, repo_name):
            raise ValueError("Failed to copy the folders.")

        os.chdir(repo_name)
        default_commit_message = "Updates " + ' '.join(folders)
        if not commit_message.strip():
            commit_message = default_commit_message
        else:
            commit_message = limit_commit_message_length(commit_message)
            commit_message = filter_alphabetic_characters(commit_message)

        success, message = add_commit_push(commit_message)
        os.chdir(current_directory)  # Restore the original working directory
        return success, message
    except ValueError as e:
        os.chdir(current_directory)  # Restore the original working directory
        return False, str(e)
    except Exception as e:
        os.chdir(current_directory)  # Restore the original working directory
        return False, f"An unexpected error occurred: {e}"