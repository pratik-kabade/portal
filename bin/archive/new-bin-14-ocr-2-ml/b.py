
import fitz
import base64
import ollama

def process_pdf(pdf_path):
    text_content = ""
    images = []
    
    doc = fitz.open(pdf_path)
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text_content += page.get_text()
        
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_data = base_image["image"]
            encoded_image = base64.b64encode(image_data).decode("utf-8")
            images.append(encoded_image)
    
    return text_content, images

def read_img():
    pdf_text, pdf_images = process_pdf("pdf/res.pdf")

    response = ollama.chat(model='gemma3:12b', 
                        messages=[{
                            'role': 'user', 
                            'content': f"Here's the text from my PDF: {pdf_text}, what is the name of the candidate",
                        }])

    return response['message']['content']

print(read_img())