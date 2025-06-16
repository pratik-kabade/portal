import numpy as np
import os
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB3, ResNet50V2, InceptionV3
from tensorflow.keras.applications.efficientnet import preprocess_input as efn_preprocess
from tensorflow.keras.applications.resnet_v2 import preprocess_input as resnet_preprocess
from tensorflow.keras.applications.inception_v3 import preprocess_input as inception_preprocess
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.preprocessing import image
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
import json

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

def create_embedding_model():
    """Create a model that outputs embeddings instead of classifications."""
    # Use EfficientNetB3 as the base model for feature extraction
    base_model = EfficientNetB3(weights='imagenet', include_top=False)
    
    # Add a global average pooling layer and get embeddings
    x = base_model.output
    embeddings = GlobalAveragePooling2D()(x)
    
    # Create the embedding model
    model = Model(inputs=base_model.input, outputs=embeddings)
    return model

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
    
    # Print predictions
    print("\nTop 10 predictions:")
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
            
        print(f"{i+1}: {formatted_label} - {confidence:.2f}% ({confidence_level} confidence) {telecom_indicator}")
    
    print("\nPredictions marked with ✓ are telecom-related categories")
    
    plt.show()
    return final_predictions[:10]

def fine_tune_for_telecom(train_dir, epochs=10):
    """Fine-tune a model specifically for telecom devices."""
    # This requires labeled telecom device images in the train_dir
    # Each subdirectory should be named after a telecom device category
    base_model = EfficientNetB3(weights='imagenet', include_top=False)
    
    # Add classification head
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(256, activation='relu')(x)
    predictions = Dense(len(os.listdir(train_dir)), activation='softmax')(x)
    
    # Create the fine-tuned model
    model = Model(inputs=base_model.input, outputs=predictions)
    
    # Freeze the base model layers
    for layer in base_model.layers:
        layer.trainable = False
    
    # Compile the model
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    
    # Create data generators for training
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    
    train_datagen = ImageDataGenerator(
        preprocessing_function=efn_preprocess,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(300, 300),
        batch_size=32,
        class_mode='categorical'
    )
    
    # Train the model
    model.fit(
        train_generator,
        epochs=epochs
    )
    
    # Unfreeze some layers for fine-tuning
    for layer in base_model.layers[-30:]:
        layer.trainable = True
    
    # Recompile with a lower learning rate
    model.compile(
        optimizer=tf.keras.optimizers.Adam(1e-5),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Continue training
    model.fit(
        train_generator,
        epochs=epochs
    )
    
    return model

def content_based_image_search(query_img_path, image_folder, top_k=5):
    """Search for similar telecom devices in a folder of images."""
    # Create the embedding model
    embedding_model = create_embedding_model()
    
    # Get the embedding for the query image
    query_img, _ = load_and_prepare_image(query_img_path)
    query_embedding = embedding_model.predict(efn_preprocess(query_img))
    
    # Get embeddings for all images in the folder
    image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder) 
                  if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    image_embeddings = []
    for img_path in image_paths:
        img, _ = load_and_prepare_image(img_path)
        embedding = embedding_model.predict(efn_preprocess(img))
        image_embeddings.append(embedding)
    
    # Calculate similarities
    similarities = [cosine_similarity(query_embedding.reshape(1, -1), 
                                     embedding.reshape(1, -1))[0][0] 
                   for embedding in image_embeddings]
    
    # Get the indices of top-k similar images
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    
    # Display the results
    plt.figure(figsize=(15, 10))
    
    # Display query image
    plt.subplot(2, 3, 1)
    plt.imshow(image.load_img(query_img_path))
    plt.title("Query Image", fontsize=14)
    plt.axis('off')
    
    # Display similar images
    for i, idx in enumerate(top_indices):
        plt.subplot(2, 3, i + 2)
        plt.imshow(image.load_img(image_paths[idx]))
        plt.title(f"Similar {i+1}: {similarities[idx]:.2f}", fontsize=12)
        plt.axis('off')
    
    plt.tight_layout()
    plt.show()
    
    return [(image_paths[idx], similarities[idx]) for idx in top_indices]

def predict_telecom_device(img_path):
    """Main function to predict telecom device from image."""
    # Use ensemble prediction for better results
    predictions = ensemble_prediction(img_path)
    return predictions

# Example usage
if __name__ == "__main__":
    # Replace with the path to your image
    image_path = "images/img.JPG"
    
    # Basic prediction
    predictions = predict_telecom_device(image_path)
    
    # If you have a folder with similar images for comparison
    # similar_images = content_based_image_search(image_path, "path/to/image/folder")
    
    # If you have labeled training data for fine-tuning
    # telecom_model = fine_tune_for_telecom("path/to/labeled/telecom/images")