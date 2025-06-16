import os
import re
import json
import cv2
import easyocr
import numpy as np
from predictor import ensemble_prediction

def read_image(img_path):
    # initialize EasyOCR reader
    reader = easyocr.Reader(['en'])  # Initialize for English

    # read image with OpenCV
    img = cv2.imread(img_path)
    
    # validate the image
    if img is None:
        print(f"Could not read image: {img_path}")
        return None
    
    # check image dimensions
    height, width = img.shape[:2]
    if height <= 0 or width <= 0:
        print(f"Invalid image dimensions for {img_path}: {width}x{height}")
        return None
                    
    # extract text using EasyOCR
    detections = reader.readtext(img)
    
    # collect all text for metadata
    all_text = []
    for detection in detections:
        text = detection[1]
        all_text.append(text)

    return img, detections, all_text


def match_pattern(results, all_text, folder, filename):
    # join all text for pattern matching
    full_text = " ".join(all_text)
    
    # Extract folder name as one location
    folder_name = os.path.basename(os.path.abspath(folder))
    
    # Initialize the entry for this image with the new format
    results[filename] = {
        "devices": [],
        "location": [folder_name, ""],  # First entry is folder name, second will be from image
        "tags": [],  # Empty as requested
        "metadata": all_text  # All text found in the image
    }

    # Find device patterns: XXXX-YYYY-ZZ where XXXX might be a location
    # This regex matches patterns like 4124-accd-01
    device_pattern = r'(\d{4})-([a-zA-Z0-9]{4})-(\d{2})'
    device_matches = re.findall(device_pattern, full_text)
    
    # Process device matches
    for match in device_matches:
        device_name = f"{match[0]}-{match[1]}-{match[2]}"
        location_code = match[0]
        
        # Add device to devices list if not already there
        if device_name not in results[filename]["devices"]:
            results[filename]["devices"].append(device_name)
        
        # If location from image is empty, use the location code from device
        if not results[filename]["location"][1]:
            results[filename]["location"][1] = location_code

    return results


def annotate_image(img, detections, results, output_dir, folder, filename):
    # create copy of image for annotation
    img_annotated = img.copy()

    # First, draw red boxes around ALL detected text
    for detection in detections:
        bbox = detection[0]  # Get bounding box coordinates
        
        # convert points to integers
        pts = np.array(bbox, np.int32)
        pts = pts.reshape((-1, 1, 2))

        # draw red polygon around all text
        cv2.polylines(img_annotated, [pts], True, (0, 0, 255), 2)

    # Then, draw green boxes around matched device names
    for detection in detections:
        bbox = detection[0]
        text = detection[1]
        
        # Check if this text contains any of our device matches
        for device in results[filename]["devices"]:
            if device in text:
                # convert points to integers
                pts = np.array(bbox, np.int32)
                pts = pts.reshape((-1, 1, 2))

                # green polygon around matched text
                cv2.polylines(img_annotated, [pts], True, (0, 255, 0), 2)

    # save annotated image
    output_path = os.path.join(output_dir, folder, filename)
    cv2.imwrite(output_path, img_annotated)
    return output_path


def assign_tags(image_path, results, filename):
    # tag = [ensemble_prediction(image_path)]
    # results[filename]["tags"] = tag
    return results


def process_images(input_dir="images", output_dir="ocr_annotated_images"):
    # initialize result dictionary with new format
    results = {}

    # process all images
    for folder in os.listdir(input_dir):
        if os.path.isdir(os.path.join(input_dir, folder)):
            # create output directory if it doesn't exist
            os.makedirs(os.path.join(output_dir, folder), exist_ok=True)

            for filename in os.listdir(os.path.join(input_dir, folder)):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
                    # construct full image path
                    image_path = os.path.join(input_dir, folder, filename)
                    
                    try:
                        print(f"Processing {folder}/{filename}")

                        # Detect text in the image
                        img, detections, all_text = read_image(image_path)

                        # If no text is detected, skip this image
                        if all_text == None:
                            continue
                        
                        # Perform pattern matching
                        results = match_pattern(results, all_text, folder, filename)

                        # Create annotated image
                        output_path = annotate_image(img, detections, results, output_dir, folder, filename)

                        # Tag prediction
                        tags = assign_tags(image_path, results, filename)

                        print(f"Saved annotated image to {output_path}\n")
                        
                    except Exception as e:
                        print(f"Error processing {filename}: {str(e)}")

    # save results to JSON file
    with open('ocr_extraction_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Processing complete! Found data for {len(results)} images. Results saved to 'ocr_extraction_results.json'")

    return results

if __name__ == "__main__":
    results = process_images()