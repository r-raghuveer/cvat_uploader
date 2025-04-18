from create_tasl import CVATTaskCreator
from export import CVATAnnotationExporter
from importer import CVATAnnotationHandler, JSONToXMLConverter

# Configuration
IMAGE_DIR = "../Hard_linelvl"
CVAT_USERNAME = "raghuveer.r@tihiitb.org"
CVAT_PASSWORD = "raghuveer2004@"
SERVER_HOST = "http://10.2.192.138"
SERVER_PORT = 8080
PROJECT_ID = 2  # Check from CVAT GUI
OUTPUT_DIR = "LinelvlXMLs"  # Local directory for storing exported XML files
IMPORT_FORMAT = "CVAT 1.1"
#EXPORT_FORMAT = "CVAT for video 1.1"

# Initialize and run the task creator
cvat_creator = CVATTaskCreator(
    image_dir=IMAGE_DIR,
    project_id=PROJECT_ID,
    cvat_username=CVAT_USERNAME,
    cvat_password=CVAT_PASSWORD,
    server_host=SERVER_HOST,
    server_port=SERVER_PORT
)

#cvat_creator.process_images()

# Initialize and run the annotation importer
cvat_handler = CVATAnnotationHandler(
    host=SERVER_HOST,
    port=SERVER_PORT,
    user=CVAT_USERNAME,
    password=CVAT_PASSWORD,
    project_id=PROJECT_ID,
    annotations_dir=IMAGE_DIR,
    import_format=IMPORT_FORMAT
)
# Convert JSON to XML
converter = JSONToXMLConverter(IMAGE_DIR)

#converter.convert_json_to_xml()

# Import annotations
cvat_handler.import_annotations()

'''
# Initialize and run the annotation exporter
exporter = CVATAnnotationExporter(
    host=SERVER_HOST,
    port=SERVER_PORT,
    user=CVAT_USERNAME,
    password=CVAT_PASSWORD,
    project_id=PROJECT_ID,
    output_dir=OUTPUT_DIR,
    export_format=EXPORT_FORMAT
)

#exporter.export_annotations()'''