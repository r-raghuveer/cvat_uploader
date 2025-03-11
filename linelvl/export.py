import os
from cvat_sdk import make_client

class CVATAnnotationExporter:
    def __init__(self, host: str, port: int, user: str, password: str, 
                 project_id: int, output_dir: str, export_format: str = 'CVAT for video 1.1'):
        """
        Initializes the CVAT Annotation Exporter.

        Args:
            host (str): CVAT server host
            port (int): CVAT server port
            user (str): CVAT username
            password (str): CVAT password
            project_id (int): CVAT project ID
            output_dir (str): Directory to save annotation files
            export_format (str): Format of the exported annotations (default: 'CVAT for video 1.1')
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.project_id = project_id
        self.output_dir = output_dir
        self.export_format = export_format

        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

    def export_annotations(self) -> None:
        """
        Exports all annotations for the given project and saves them as XML files.
        """
        with make_client(self.host, port=self.port, credentials=(self.user, self.password)) as client:
            project = client.projects.retrieve(self.project_id)  # Get project details
            tasks = project.get_tasks()  # Get all tasks in the project
            
            for task in tasks:
                task_name = os.path.splitext(task.name)[0]  # Strip file extension if applicable
                output_file = os.path.join(self.output_dir, f'{task_name}.xml')

                # Export annotations without images
                task.export_dataset(format_name=self.export_format, filename=output_file, include_images=False)
                print(f"Exported annotations for task {task.id} to {output_file}")
