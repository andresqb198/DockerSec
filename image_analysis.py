import subprocess
import json
import os
import shutil


def inspect_image(image):
    
    pull_command = ["docker", "pull", image]
    subprocess.run(pull_command, capture_output=True, text=True)

    container_id = subprocess.check_output(["docker", "create", image]).decode().strip()

    check_git_command = ["docker", "cp", f"{container_id}:/", "/tmp/docker_inspect"]
    subprocess.run(check_git_command, capture_output=True)

    git_folder_exists = os.path.exists("/tmp/docker_inspect/.git")
    
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
        "is_python_version_below_3.8": (
            base_python_version < "3.8" if base_python_version != "Unknown or Python not installed" else False
        )
    }