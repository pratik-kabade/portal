import os
import re
import json
import easyocr
import ast
import pandas as pd
from llm import read_img
 
 
def read_image(img_path):
    reader = easyocr.Reader(['en'])
    img = reader.readtext(img_path)
    all_text = [detection[1] for detection in img]
    return all_text
 
 
def extract_devices(all_text):
    full_text = " ".join(all_text)
    device_pattern = r'([a-zA-Z0-9]{3,})-([a-zA-Z0-9]{3,})-(\d{2})'
    device_matches = re.findall(device_pattern, full_text)
 
    devices = list({f"{m[0]}-{m[1]}-{m[2]}" for m in device_matches})
    return devices
 
 
def extract_ports_with_llm(image_path):
    prompt = '''
    Task description-
    You are an expert in Image reading and analysis. Analyse the image and give the result in a dictionary-
    The output will contain only three columns that are PortNumber, PortLabel and Connected.
    PortNumber - Number the ports serially from top-left to bottom-right.
    PortLabel - Show the label on the respective port (above or below the port).
    Connected - Show whether the port is connected or not ("yes" or "no").
 
    Output Format:
    {
        "PortNumber": [],
        "PortLabel": [],
        "Connected": []
    }
 
    Important guidelines:
    - Output strictly in dictionary format.
    - Do not return any text other than the dictionary.
    - Scan and analyze every port available in the image.
    - Do not give output in markdown or code block format.
    - Do not include any additional information or explanations.
    '''
 
    response = read_img(image_path, prompt)
    print(f"LLM response for port extraction: {response}")
    # try:
    port_dict= response.replace("```", "").replace("python","").replace("json","").strip()
    port_dict = ast.literal_eval(port_dict)
    result=pd.DataFrame(port_dict).to_dict(orient="records")
    print(f"Parsed port info: {result}")
    return result
    # except Exception as e:
    #     print(f"Error parsing port info from LLM: {e}")
    #     return []
 
 
def process_images(input_dir="new_images", output_json="ocr_extraction_results.json"):
    results = {}
 
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(input_dir, filename)
            print(f"Processing {filename}...")
 
            try:
                all_text = read_image(image_path)
                devices = extract_devices(all_text)
                port_details = extract_ports_with_llm(image_path)
 
                results[filename] = {
                    "devices": devices,
                    "metadata": all_text,
                    "port-details": port_details
                }
 
            except Exception as e:
                print(f"Failed to process {filename}: {e}")
                continue
 
    with open(output_json, 'w') as f:
        json.dump(results, f, indent=2)
 
    print(f"✅ Done! Output saved to {output_json}")
 
 
if __name__ == "__main__":
    process_images()
 
 
