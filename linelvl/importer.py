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
                    xml_file_path = os.path.join(subfolder_path, f"{task_name}.xml")

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

class JSONToXMLConverter:
    def __init__(self, json_folder: str):
        """
        Initializes the converter with the JSON folder path.

        Args:
            json_folder (str): The main directory containing JSON subfolders.
        """
        self.json_folder = json_folder
        self.json_extension = ".json"

    def list_subfolders(self):
        """
        Lists all subfolders inside the JSON directory.

        Returns:
            List[str]: A list of subfolder names.
        """
        subfolders = [
            name for name in os.listdir(self.json_folder)
            if os.path.isdir(os.path.join(self.json_folder, name))
        ]
        logging.info(f"Found {len(subfolders)} subfolders: {subfolders}")
        return subfolders

    def convert_json_to_xml(self):
        """
        Converts all JSON files in subfolders to a single XML per subfolder.
        """
        logging.info("Starting JSON to XML conversion...")
        subfolders = self.list_subfolders()

        for subfolder in subfolders:
            subfolder_path = os.path.join(self.json_folder, subfolder)

            # Find all .json files in the subfolder
            json_files = [
                os.path.join(subfolder_path, f)
                for f in os.listdir(subfolder_path)
                if f.lower().endswith(self.json_extension)
            ]

            if not json_files:
                logging.warning(f"No JSON files found in {subfolder}, skipping.")
                continue

            # Output XML file (same as subfolder name)
            output_xml_file = os.path.join(subfolder_path, f"{subfolder}.xml")

            # Convert JSON files to a single XML file
            self.process_json_files(json_files, output_xml_file)

    def process_json_files(self, json_files: list, output_xml_file: str):
        """
        Converts multiple JSON files from a subfolder into a single XML file.

        Args:
            json_files (list): List of JSON file paths.
            output_xml_file (str): Path to save the output XML file.
        """
        try:
            # Create XML structure
            annotations = ET.Element("annotations")
            meta = ET.SubElement(annotations, "meta")

            # Job details
            job = ET.SubElement(meta, "job")
            ET.SubElement(job, "id").text = "4"
            ET.SubElement(job, "size").text = str(len(json_files))
            ET.SubElement(job, "mode").text = "annotation"
            ET.SubElement(job, "overlap").text = "0"
            ET.SubElement(job, "created").text = "2025-02-20 09:26:59.190346+00:00"
            ET.SubElement(job, "updated").text = "2025-02-20 09:28:44.134112+00:00"

            # Process each JSON file
            for json_file in json_files:
                try:
                    with open(json_file, "r", encoding="utf-8") as file:
                        data = json.load(file)

                    # Extract image details
                    image_name = os.path.basename(json_file).replace(".json", ".jpg")
                    # Open the corresponding image to find the width and height
                    subfolder_path = "/".join(json_file.split("/")[:-1])
                    image_path = os.path.join(subfolder_path,"images", image_name)
                    with Image.open(image_path) as img:
                        width, height = img.size

                    # Create <image> tag
                    image = ET.SubElement(annotations, "image", id="0", name=image_name, width=str(width), height=str(height))

                    # Add bounding boxes
                    for item in data:
                        bbox = item["bbox"]
                        ocr_text = item["ocr"]

                        box = ET.SubElement(
                            image, "box", label="OCR", source="manual", occluded="0",
                            xtl=str(bbox[0]), ytl=str(bbox[1]), xbr=str(bbox[2]), ybr=str(bbox[3]), z_order="0"
                        )

                        attribute = ET.SubElement(box, "attribute", name="OCR Text")
                        attribute.text = ocr_text

                except Exception as e:
                    logging.error(f"❌ Error processing {json_file}: {str(e)}")

            # Convert to XML string
            xml_str = ET.tostring(annotations, encoding="utf-8").decode()

            # Save XML to file
            with open(output_xml_file, "w", encoding="utf-8") as file:
                file.write(xml_str)

            logging.info(f"✅ XML saved: {output_xml_file}")

        except Exception as e:
            logging.error(f"❌ Error converting JSON files to XML: {str(e)}")


# Example Usage
if __name__ == "__main__":
    json_folder = "/dataset/annotations"  # Update with your path
    converter = JSONToXMLConverter(json_folder)
    converter.convert_json_to_xml()
