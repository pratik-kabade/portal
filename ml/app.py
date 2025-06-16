from imageai.Detection import ObjectDetection

detector = ObjectDetection()
detector.setModelTypeAsYOLOv3()
detector.setModelPath("yolo.h5")  # Download YOLO model
detector.loadModel()
detections = detector.detectObjectsFromImage(
   input_image="IMG_3873.JPG",
   output_image_path="output.jpg"
)
