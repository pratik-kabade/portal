import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB3, ResNet50V2, InceptionV3
from tensorflow.keras.applications.efficientnet import preprocess_input as efn_preprocess
from tensorflow.keras.applications.resnet_v2 import preprocess_input as resnet_preprocess
from tensorflow.keras.applications.inception_v3 import preprocess_input as inception_preprocess
from tensorflow.keras.preprocessing import image
import matplotlib.pyplot as plt

# Telecom device categories - can be expanded with your specific devices
TELECOM_CATEGORIES = [
    "router", "modem", "switch", "access point", "network card", "network adapter",
    "fiber optic cable", "ethernet cable", "network switch", "firewall", "gateway",
    "cellular tower", "antenna", "satellite dish", "cell phone", "smartphone", 
    "telecommunications equipment", "wireless access point", "server", "data center equipment",
    "network hub", "patch panel", "network rack", "fiber optic transmitter", "fiber optic receiver",
    "network interface card", "media converter", "repeater", "network bridge", "optical network terminal"
]

def load_and_prepare_image(img_path, target_size=(299, 299)):
    """Load an image and prepare it for the model."""
    img = image.load_img(img_path, target_size=target_size)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array, img

def ensemble_prediction(img_path, confidence_threshold=0.30):
    """Use an ensemble of models to improve prediction confidence."""
    models = [
        (EfficientNetB3(weights='imagenet'), efn_preprocess, (300, 300)),
        (ResNet50V2(weights='imagenet'), resnet_preprocess, (224, 224)),
        (InceptionV3(weights='imagenet'), inception_preprocess, (299, 299))
    ]
    
    all_predictions = []
    
    for model, preprocess_func, size in models:
        # Load and preprocess the image for this specific model
        img, original_img = load_and_prepare_image(img_path, target_size=size)
        processed_img = preprocess_func(img)
        
        # Make predictions
        preds = model.predict(processed_img)
        
        # Get the top 10 predictions
        top_preds = tf.keras.applications.imagenet_utils.decode_predictions(preds, top=10)[0]
        all_predictions.extend(top_preds)
    
    # Create a dictionary to merge predictions of the same class
    merged_predictions = {}
    for _, label, score in all_predictions:
        if label in merged_predictions:
            merged_predictions[label] += score
        else:
            merged_predictions[label] = score
    
    # Sort predictions by score
    sorted_predictions = sorted(merged_predictions.items(), key=lambda x: x[1], reverse=True)
    
    # Filter for telecom-related predictions or boost their scores
    telecom_predictions = []
    general_predictions = []
    
    for label, score in sorted_predictions:
        # Check if any telecom category word is in the prediction label
        is_telecom = any(category.lower() in label.lower() for category in TELECOM_CATEGORIES)
        
        if is_telecom:
            # Boost telecom-related predictions
            telecom_predictions.append((label, score * 1.5))
        else:
            general_predictions.append((label, score))
    
    # Combine and sort all predictions
    final_predictions = sorted(telecom_predictions + general_predictions, key=lambda x: x[1], reverse=True)
    
    # Display results
    plt.figure(figsize=(10, 10))
    plt.imshow(image.load_img(img_path))
    plt.axis('off')
    
    # Format top prediction for title
    top_pred = final_predictions[0]
    formatted_label = ' '.join(word.capitalize() for word in top_pred[0].replace('_', ' ').split())
    plt.title(f"Predicted: {formatted_label} ({top_pred[1]*100:.2f}%)", fontsize=16)
    
    # # Print predictions
    # print("\nTop 10 predictions:")
    for i, (label, score) in enumerate(final_predictions[:10]):
        formatted_label = ' '.join(word.capitalize() for word in label.replace('_', ' ').split())
        confidence = score * 100
        telecom_indicator = "✓" if any(category.lower() in label.lower() for category in TELECOM_CATEGORIES) else " "
        
        # Check confidence level
        if confidence >= confidence_threshold * 100:
            confidence_level = "High"
        elif confidence >= 20:
            confidence_level = "Medium"
        else:
            confidence_level = "Low"
            
        # print(f"{i+1}: {formatted_label} - {confidence:.2f}% ({confidence_level} confidence) {telecom_indicator}")
    
    # print("\nPredictions marked with ✓ are telecom-related categories")
    
    plt.show()
    return final_predictions[:10]

if __name__ == "__main__":
    # Replace with the path to your image
    image_path = "images/img.JPG"
    
    # Basic prediction
    predictions = ensemble_prediction(image_path)
    