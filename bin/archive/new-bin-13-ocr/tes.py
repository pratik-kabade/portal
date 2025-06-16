import os
import re
import json
import pytesseract
import cv2
from PIL import Image

def process_images(input_dir="images", output_dir="tes_annotated_images", pattern=r'[a-z]+-[a-z]+'):

    # create output directory if it doesnt exist
    os.makedirs(output_dir, exist_ok=True)
    
    # initialize result dictionary
    results = {"images": {}, "metadata": {}}
    
    # process all images
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
            image_path = os.path.join(input_dir, filename)

            try:
                print(f"Processing {filename}")
                
                # read image with PIL (for text extraction)
                img_pil = Image.open(image_path)
                
                # extract text
                extracted_text = pytesseract.image_to_string(img_pil)
                results["metadata"][filename] = extracted_text.split('\n')
                
                # find pattern matches
                matches = re.findall(pattern, extracted_text, re.IGNORECASE)
                
                # read image with OpenCV (for annotation)
                img_cv = cv2.imread(image_path)
                
                # get data with bounding boxes
                data = pytesseract.image_to_data(img_pil, output_type=pytesseract.Output.DICT)
                
                # first, draw red boxes around all detected text
                for i, text in enumerate(data['text']):
                    if text.strip():  # Only process non-empty text
                        x = data['left'][i]
                        y = data['top'][i]
                        w = data['width'][i]
                        h = data['height'][i]
                        cv2.rectangle(img_cv, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Red box
                
                # then, draw green boxes over pattern matches (will override red boxes)
                for match in matches:
                    # add to dictionary
                    if match not in results["images"]:
                        results["images"][match] = []
                    if filename not in results["images"][match]:
                        results["images"][match].append(filename)
                    
                    # find and highlight matched text in image
                    for i, text in enumerate(data['text']):
                        if match in text:
                            x = data['left'][i]
                            y = data['top'][i]
                            w = data['width'][i]
                            h = data['height'][i]
                            cv2.rectangle(img_cv, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green box
                
                # save annotated image
                output_path = os.path.join(output_dir, filename)
                cv2.imwrite(output_path, img_cv)
                print(f"Saved annotated image to {output_path}\n")

            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

    # save results to JSON file
    with open('tes_extraction_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Processing complete! Found '{len(results['images'])}' pattern matches, Results saved to 'tes_extraction_results.json'")
    
    return results

if __name__ == "__main__":
    results = process_images()