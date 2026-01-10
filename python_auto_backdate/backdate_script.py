import subprocess
from datetime import datetime, timedelta
import os
import time

# Path to the file to modify
file_path = "auto_backdate_file.py"
# Path to the Git repository
repo_path = r"C:\Users\HomePC\Desktop\backdate_github_squares\python_auto_backdate"
# Hard-code the start date
start_date = datetime(2022, 7, 3)
commit_message = "Done for today"

# Function to alter the file by adding and then removing '#mcc\n'
def modify_file(file_path, action, date_str):
    try:
        # Add or remove '#mcc' with a unique identifier (date) to ensure a real change
        if action == 'add':
            with open(file_path, 'a') as file:  
                file.write(f'#mcc {date_str}\n')  
                file.flush()  
                os.fsync(file.fileno()) 
            print(f"Successfully added '#mcc {date_str}' to {file_path}")
        elif action == 'remove':
            with open(file_path, 'rb+') as file:  
                file.seek(-len(f'#mcc {date_str}\n'), 2)  # Move to the position of the unique comment
                if file.read(len(f'#mcc {date_str}\n')) == f'#mcc {date_str}\n'.encode():
                    file.seek(-len(f'#mcc {date_str}\n'), 2) 
                    file.truncate()  
                    file.flush()  
                    os.fsync(file.fileno())  
            print(f"Successfully removed '#mcc {date_str}' from {file_path}")
    except Exception as e:
        print(f"Error modifying file: {e}")

# Git commands
def run_git_command(command):
    try:
        print(f"Running command: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=repo_path)
        if result.returncode != 0:
            print(f"Error: Command '{command}' failed with exit code {result.returncode}")
            print(f"Standard Output: {result.stdout}")
            print(f"Standard Error: {result.stderr}")
        else:
            print(f"Success: {result.stdout}")
    except Exception as e:
        print(f"Command failed: {e}")

# Loop through each day
current_date = datetime.now()
day_counter = 0  # To track whether to add or remove '#mcc + date string'
while start_date <= current_date:
    try:
        backdate_str = start_date.strftime("%Y-%m-%d")

        if day_counter % 2 == 0:
            modify_file(file_path, 'add', backdate_str)
        else:
            modify_file(file_path, 'remove', backdate_str)

        # Check git status
        run_git_command('git status')

        # Stage the file for commit
        run_git_command(f'git add {file_path}')

        # Commit the changes with the backdated date
        run_git_command(f'git commit --allow-empty --date="{backdate_str}" -m "{commit_message} on {backdate_str}"')

        # Print progress
        print(f"Committed for {backdate_str}")

        # Push the commits after each commit
        try:
            run_git_command('git push --force')
            print("Commits pushed successfully.")
        except Exception as e:
            print(f"Error pushing commits: {e}")

        # Move to the next day
        start_date += timedelta(days=1)
        day_counter += 1  # Increment counter

        # Delay between commits
        time.sleep(2)

    except Exception as e:
        print(f"Failed to commit for {backdate_str}: {e}")