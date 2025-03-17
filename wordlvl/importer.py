import os
import json
import logging
import xml.etree.ElementTree as ET
from cvat_sdk import make_client
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("cvat_task_creator.log"),  # Log file for JSON to XML conversion
        logging.StreamHandler()  # Print logs to console
    ]
)

class CVATAnnotationHandler:
    def __init__(self, host: str, port: int, user: str, password: str,
                 project_id: int, annotations_dir: str, import_format: str = 'CVAT 1.1'):
        """
        Initializes the CVAT Annotation Handler.

        Args:
            host (str): CVAT server host
            port (int): CVAT server port
            user (str): CVAT username
            password (str): CVAT password
            project_id (int): CVAT project ID
            annotations_dir (str): Directory containing annotation XML subfolders
            import_format (str): Format of the annotations (default: 'CVAT 1.1')
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.project_id = project_id
        self.annotations_dir = annotations_dir
        self.import_format = import_format

        # Ensure the annotation directory exists
        if not os.path.isdir(self.annotations_dir):
            raise FileNotFoundError(f"❌ Annotation directory '{self.annotations_dir}' does not exist.")

    def import_annotations(self) -> None:
        """
        Imports annotations for tasks in the given project from matching XML files.
        """
        logging.info("🔹 Starting annotation import process...")

        with make_client(self.host, port=self.port, credentials=(self.user, self.password)) as client:
            project = client.projects.retrieve(self.project_id)
            tasks = project.get_tasks()

            # List all subfolders in the annotations directory
            subfolders = [
                name for name in os.listdir(self.annotations_dir)
                if os.path.isdir(os.path.join(self.annotations_dir, name))
            ]

            logging.info(f"🔹 Found {len(subfolders)} annotation subfolders: {subfolders}")

            for task in tasks:
                task_name = task.name # Strip file extension
                print(task_name, subfolders)
                # Check if the task name matches a subfolder
                if task_name in subfolders:
                    subfolder_path = os.path.join(self.annotations_dir, task_name)
                    xml_file_path = os.path.join(subfolder_path,"results", f"{task_name}.xml")

                    # Ensure the XML file exists inside the subfolder
                    if os.path.exists(xml_file_path):
                        try:
                            task.import_annotations(self.import_format, xml_file_path)
                            logging.info(f"✅ Successfully imported annotations for '{task_name}' from '{xml_file_path}'")

                        except Exception as e:
                            logging.error(f"❌ Error importing annotations for '{task_name}': {str(e)}")
                    else:
                        logging.warning(f"⚠ No XML file found for task '{task_name}' at '{xml_file_path}'")
                else:
                    logging.warning(f"⚠ No matching subfolder found for task '{task_name}'")

class JSONLToXMLConverter:
    def __init__(self, jsonl_folder: str):
        """Initializes the converter with the JSONL folder path."""
        self.jsonl_folder = jsonl_folder
        self.jsonl_extension = ".jsonl"

    def list_subfolders(self):
        """Lists all subfolders inside the JSONL directory."""
        subfolders = [
            name for name in os.listdir(self.jsonl_folder)
            if os.path.isdir(os.path.join(self.jsonl_folder, name))
        ]
        logging.info(f"Found {len(subfolders)} subfolders: {subfolders}")
        return subfolders

    def convert_jsonl_to_xml(self):
        """Converts all JSONL files in subfolders to a single XML per subfolder."""
        logging.info("Starting JSONL to XML conversion...")
        subfolders = self.list_subfolders()

        for subfolder in subfolders:
            subfolder_path = os.path.join(self.jsonl_folder, subfolder, "results")

            # Find all .jsonl files in the subfolder
            jsonl_files = [
                os.path.join(subfolder_path, f)
                for f in os.listdir(subfolder_path)
                if f.lower().endswith(self.jsonl_extension)
            ]

            if not jsonl_files:
                logging.warning(f"No JSONL files found in {subfolder}, skipping.")
                continue

            # Output XML file (same as subfolder name)
            output_xml_file = os.path.join(subfolder_path, f"{subfolder}.xml")

            # Convert JSONL files to a single XML file
            xml_tree = self.process_jsonl_files(jsonl_files)
            self.save_xml(xml_tree, output_xml_file)

    def process_jsonl_files(self, jsonl_files):
        """Converts multiple JSONL files from a subfolder into an XML tree."""
        root = ET.Element("annotations")

        for jsonl_file in jsonl_files:
            try:
                with open(jsonl_file, "r", encoding="utf-8") as file:
                    for line in file:
                        data = json.loads(line.strip())  # Read each JSONL entry

                        image_id = data["image_id"].replace("image_", "")
                        image_name = f"{image_id}.jpg"

                        # Create <image> tag
                        image = ET.SubElement(root, "image", id=image_id, name=image_name)

                        # Extract bounding boxes
                        for paragraph in data.get("paragraphs", []):
                            for line in paragraph.get("lines", []):
                                for word in line.get("words", []):
                                    if "vertices" in word and len(word["vertices"]) > 1:
                                        x_coords = [point[0] for point in word["vertices"]]
                                        y_coords = [point[1] for point in word["vertices"]]

                                        xtl, ytl = min(x_coords), min(y_coords)
                                        xbr, ybr = max(x_coords), max(y_coords)

                                        ET.SubElement(image, "box", label="BBox", source="automated", occluded="0",
                                                      xtl=str(xtl), ytl=str(ytl), xbr=str(xbr), ybr=str(ybr), z_order="0")

            except Exception as e:
                logging.error(f"❌ Error processing {jsonl_file}: {str(e)}")

        return ET.ElementTree(root)

    def save_xml(self, tree, output_path):
        """Saves XML tree to a file."""
        tree.write(output_path, encoding="utf-8", xml_declaration=True)
        logging.info(f"✅ XML saved: {output_path}")
