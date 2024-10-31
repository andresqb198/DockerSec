import subprocess
import json
import os
from image_analysis import inspect_image

def get_deployment_images(namespace):

    command = ["kubectl", "get", "deployments", "-n", namespace, "-o", "json"]
    result = subprocess.run(command, capture_output=True, text=True)

    deployments = json.loads(result.stdout)
    
    images = {}
    for deployment in deployments["items"]:
        deployment_name = deployment["metadata"]["name"]
        container_images = [
            container["image"] for container in deployment["spec"]["template"]["spec"]["containers"]
        ]
        images[deployment_name] = container_images

    return images

dir = "./Data"
cluster = "Raijin"
namespace = "thori-guane-ds-dev"
images = get_deployment_images(namespace)

for image in images:
    for container in images[image]:
        image_data = inspect_image(container)
        images[image][container] = image_data


if not os.path.exists(f"{dir}/{cluster}/{namespace}"):
    os.makedirs(f"{dir}/{cluster}/{namespace}")

with open(f"{dir}/{cluster}/{namespace}/images.json", "w") as f:
    json.dump(images, f, indent=4)
