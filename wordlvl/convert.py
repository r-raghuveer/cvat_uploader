import json
import xml.etree.ElementTree as ET

def read_jsonl(file_path):
    """Reads a JSONL file and returns a list of dictionaries."""
    data = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            data.append(json.loads(line.strip()))  # Parse each JSON object
    return data

def jsonl_to_xml(jsonl_data):
    """Converts JSONL data to the required XML format."""
    root = ET.Element("annotations")

    meta = ET.SubElement(root, "meta")
    job = ET.SubElement(meta, "job")

    # Mock job data (adjust as needed)
    ET.SubElement(job, "id").text = "2"
    ET.SubElement(job, "size").text = str(len(jsonl_data))
    ET.SubElement(job, "mode").text = "annotation"
    ET.SubElement(job, "overlap").text = "0"
    ET.SubElement(job, "subset").text = "default"
    ET.SubElement(job, "start_frame").text = "0"
    ET.SubElement(job, "stop_frame").text = str(len(jsonl_data) - 1)

    labels = ET.SubElement(job, "labels")
    label = ET.SubElement(labels, "label")
    ET.SubElement(label, "name").text = "BBOx"
    ET.SubElement(label, "color").text = "#92c6b4"
    ET.SubElement(label, "type").text = "any"

    # Process each image
    for entry in jsonl_data:
        image_id = entry["image_id"].replace("image_", "")
        image = ET.SubElement(root, "image", id=image_id, name=f"part2_{image_id}.jpg", width="1654", height="2339")

        for paragraph in entry.get("paragraphs", []):
            for line in paragraph.get("lines", []):
                for word in line.get("words", []):
                    if "vertices" in word and len(word["vertices"]) > 1:
                        x_coords = [point[0] for point in word["vertices"]]
                        y_coords = [point[1] for point in word["vertices"]]

                        xtl, ytl = min(x_coords), min(y_coords)
                        xbr, ybr = max(x_coords), max(y_coords)

                        ET.SubElement(image, "box", label="BBOx", source="manual", occluded="0",
                                      xtl=str(xtl), ytl=str(ytl), xbr=str(xbr), ybr=str(ybr), z_order="0")

    return ET.ElementTree(root)

def save_xml(tree, output_path):
    """Saves XML tree to a file."""
    tree.write(output_path, encoding="utf-8", xml_declaration=True)

# File paths
jsonl_file = "c.jsonl"  # JSONL file named 'c'
xml_output_file = "output.xml"

# Read, convert, and save XML
jsonl_data = read_jsonl(jsonl_file)
xml_tree = jsonl_to_xml(jsonl_data)
save_xml(xml_tree, xml_output_file)

print(f"Converted XML saved to {xml_output_file}")

