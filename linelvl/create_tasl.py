import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

# Configure logging
logging.basicConfig(
    filename="cvat_task_creator.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class CVATTaskCreator:
    def __init__(self, image_dir: str, project_id: int, cvat_username: str, 
                 cvat_password: str, server_host: str, server_port: int, 
                 image_quality: int = 70, frame_step: int = 5, 
                 bug_tracker_template: str = "https://bug-tracker.com/{task_id}"):
        """
        Initializes the CVATTaskCreator for images.

        Args:
            image_dir (str): Directory containing image subfolders.
            project_id (int): CVAT project ID.
            cvat_username (str): CVAT username.
            cvat_password (str): CVAT password.
            server_host (str): CVAT server host.
            server_port (int): CVAT server port.
            image_quality (int): Image quality for annotations (default: 70).
            frame_step (int): Frame step for image annotation (default: 5).
            bug_tracker_template (str): Template for bug tracker URL.
        """
        self.image_dir = image_dir
        self.project_id = project_id
        self.cvat_username = cvat_username
        self.cvat_password = cvat_password
        self.server_host = server_host
        self.server_port = server_port
        self.image_quality = image_quality
        self.frame_step = frame_step
        self.bug_tracker_template = bug_tracker_template
        self.image_extensions = ('.jpg', '.png')  # Supported image formats

        logging.info("Initialized CVATTaskCreator with project ID %s", self.project_id)

    def get_image_files(self) -> Dict[str, List[str]]:
        """
        Retrieves all image files (.jpg, .png) from subdirectories.

        Returns:
            Dict[str, List[str]]: A dictionary where keys are subfolder names and values are lists of image paths.
        """
        subfolders = [
            name for name in os.listdir(self.image_dir)
            if os.path.isdir(os.path.join(self.image_dir, name))
        ]

        image_dict = defaultdict(list)

        # First, list all subfolders
        print(f"Found subfolders: {subfolders}")

        for subfolder in subfolders:
            image_dict[subfolder] = []

        logging.info(f"Found {len(image_dict)} sub-folders with images.")
        return image_dict

    def create_task(self, task_name: str, image_paths: List[str]) -> None:
        """
        Creates a CVAT task for a given set of image files.

        Args:
            task_name (str): Name of the task (subfolder name).
            image_paths (List[str]): List of image file paths.
        """
        

        import glob
        import os

        image_dir = f"../Hard_linelvl/{task_name}/images"
        image_paths = glob.glob(os.path.join(image_dir, "*.jpg"))  # Get all image files

        command = [
            "cvat-cli",
            "--org", "BGV",
            "--auth", f"{self.cvat_username}:{self.cvat_password}",
            "--server-host", self.server_host,
            "--server-port", str(self.server_port),
            "task", "create",
            "--project_id", str(self.project_id),
            task_name,
            "local"
        ] + image_paths  # Append image files

        print("Generated Command:", command)

        try:
            logging.info(f"Creating task for {task_name} with {len(image_paths)} images.")
            print(f"\nCreating task for {task_name}...")

            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True
            )

            logging.info(f"Successfully created task '{task_name}'")
            print(f"Successfully created task '{task_name}'")

        except subprocess.CalledProcessError as e:
            logging.error(f"Error creating task for {task_name}: {e.stderr}")
            print(f"Error creating task for {task_name}: {e.stderr}")

        except Exception as e:
            logging.error(f"Unexpected error creating task for {task_name}: {str(e)}")
            print(f"Unexpected error creating task for {task_name}: {str(e)}")

    def process_images(self) -> None:
        """
        Processes all images in the directory and creates tasks in CVAT.
        """
        file_dict = self.get_image_files()
        for subfolder, image_list in file_dict.items():
            self.create_task(subfolder, image_list)