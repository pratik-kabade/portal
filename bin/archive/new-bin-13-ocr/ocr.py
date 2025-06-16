import os
import re
import json
import cv2
import easyocr
import numpy as np

def process_images(input_dir="images", output_dir="ocr_annotated_images", pattern=r'[a-z]+-[a-z]+'):

    # create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # initialize EasyOCR reader
    reader = easyocr.Reader(['en'])  # Initialize for English

    # initialize result dictionary
    results = {"images": {}, "metadata": {}}

    # process all images
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
            image_path = os.path.join(input_dir, filename)
            
            try:
                print(f"Processing {filename}")
                
                # read image with OpenCV
                img = cv2.imread(image_path)
                
                # validate the image
                if img is None:
                    print(f"Could not read image: {image_path}")
                    continue
                
                # check image dimensions
                height, width = img.shape[:2]
                if height <= 0 or width <= 0:
                    print(f"Invalid image dimensions for {image_path}: {width}x{height}")
                    continue
                                
                # extract text using EasyOCR
                detections = reader.readtext(img)  # Use the image array instead of path
                
                # collect all text into a single string and for metadata
                all_text = []
                for detection in detections:
                    text = detection[1]
                    all_text.append(text)

                # join all text and store in metadata
                full_text = " ".join(all_text)
                results["metadata"][filename] = all_text

                # find pattern matches
                matches = re.findall(pattern, full_text, re.IGNORECASE)

                # create copy of image for annotation
                img_annotated = img.copy()

                # first, draw red boxes around ALL detected text
                for detection in detections:
                    bbox = detection[0]  # Get bounding box coordinates
                    text = detection[1]  # Get text

                    # convert points to integers
                    pts = np.array(bbox, np.int32)
                    pts = pts.reshape((-1, 1, 2))

                    # draw red polygon around all text
                    cv2.polylines(img_annotated, [pts], True, (0, 0, 255), 2)

                # then, draw green boxes around matched text
                for match in matches:

                    # add to dictionary
                    if match not in results["images"]:
                        results["images"][match] = []
                    if filename not in results["images"][match]:
                        results["images"][match].append(filename)

                    # find and highlight matched text in image
                    for detection in detections:
                        bbox = detection[0]
                        text = detection[1]
                        if match.lower() in text.lower():

                            # convert points to integers
                            pts = np.array(bbox, np.int32)
                            pts = pts.reshape((-1, 1, 2))

                            # green polygon around matched text
                            cv2.polylines(img_annotated, [pts], True, (0, 255, 0), 2)

                # save annotated image
                output_path = os.path.join(output_dir, filename)
                cv2.imwrite(output_path, img_annotated)
                print(f"Saved annotated image to {output_path}\n")
                
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

    # save results to JSON file
    with open('ocr_extraction_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Processing complete! Found '{len(results['images'])}' pattern matches, Results saved to 'ocr_extraction_results.json'")

    return results

if __name__ == "__main__":
    results = process_images()