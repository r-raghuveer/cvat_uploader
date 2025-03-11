import json
import xml.etree.ElementTree as ET

# Load JSON data from file
json_file = "data.json"  # Update this with your actual JSON file name
with open(json_file, "r", encoding="utf-8") as file:
    data = json.load(file)

# Create XML structure
annotations = ET.Element("annotations")
meta = ET.SubElement(annotations, "meta")

# Job details
job = ET.SubElement(meta, "job")
ET.SubElement(job, "id").text = "4"
ET.SubElement(job, "size").text = str(len(data))
ET.SubElement(job, "mode").text = "annotation"
ET.SubElement(job, "overlap").text = "0"
ET.SubElement(job, "created").text = "2025-02-20 09:26:59.190346+00:00"
ET.SubElement(job, "updated").text = "2025-02-20 09:28:44.134112+00:00"

# Image details
image = ET.SubElement(annotations, "image", id="0", name="image_0.jpg", width="2339", height="1656")

# Add bounding boxes
for item in data:
    bbox = item["bbox"]
    ocr_text = item["ocr"]

    box = ET.SubElement(
        image, "box", label="Hello", source="manual", occluded="0",
        xtl=str(bbox[0]), ytl=str(bbox[1]), xbr=str(bbox[2]), ybr=str(bbox[3]), z_order="0"
    )

    attribute = ET.SubElement(box, "attribute", name="OCR Text")
    attribute.text = ocr_text

# Convert to XML string
xml_str = ET.tostring(annotations, encoding="utf-8").decode()

# Save XML to file
xml_file = "output.xml"  # Update with your desired output file
with open(xml_file, "w", encoding="utf-8") as file:
    file.write(xml_str)

print("XML conversion completed successfully!")

