import subprocess
import json
import os
import re
import shutil


def inspect_image(image):
    
    pull_command = ["docker", "pull", image]
    subprocess.run(pull_command, capture_output=True, text=True)

    container_id = subprocess.check_output(["docker", "create", image]).decode().strip()

    check_git_command = ["docker", "run", f"{image}", "ls", "-a"]
    result_git = subprocess.run(check_git_command, capture_output=True)

    if b'.git' in result_git.stdout.split():
        git_folder_exists = True
        get_git_info_command = ["docker", "run", f"{image}", "cat", ".git/config"]
        git_info = subprocess.run(get_git_info_command, capture_output=True, text=True)
        git_info = git_info.stdout.strip()
        match = re.search(r'url\s*=\s*(.+)', git_info)
        if match:
            repo_url = match.group(1).strip()
            print("La URL del repositorio es:", repo_url)
        else:
            print("No se encontró la URL del repositorio.")
    else:
        git_folder_exists = False
    
    base_python_version = None
    python_check_command = ["docker", "run", "--rm", image, "python3", "--version"]
    try:
        python_version_output = subprocess.check_output(python_check_command, text=True).strip()
        base_python_version = python_version_output.split()[1]
    except subprocess.CalledProcessError:
        base_python_version = "Unknown or Python not installed"

    subprocess.run(["docker", "rm", container_id], capture_output=True)
    shutil.rmtree("/tmp/docker_inspect", ignore_errors=True)

    return {
        "image": image,
        "has_git_folder": git_folder_exists,
        "base_python_version": base_python_version,
        "repo_url": repo_url if git_folder_exists else None,
        "is_python_version_below_3.8": (
            base_python_version < "3.8" if base_python_version != "Unknown or Python not installed" else False
        )
    }