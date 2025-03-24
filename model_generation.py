import tensorflow as tf
from tensorflow import keras


def create_default_model(img_shape=(224, 224, 3), num_classes=10):
    """
    Create default yoga pose classification model using transfer learning
    
    Args:
        img_shape (tuple): Shape of input images
        num_classes (int): Number of yoga pose classes to predict
    
    Returns:
        model: Compiled tensorflow model
    """
    # Use MobileNetV2 as base model for transfer learning
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=img_shape,
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze the base model layers
    base_model.trainable = False
    
    model = tf.keras.Sequential([
        # Base model
        base_model,
        
        # Global average pooling
        tf.keras.layers.GlobalAveragePooling2D(),
        
        # Dense layers for pose classification
        tf.keras.layers.Dense(512, activation='relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.3),
        
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.3),
        
        # Output layer for pose classification
        tf.keras.layers.Dense(num_classes, activation='softmax')
    ])
    
    # Compile model
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def save_default_model():
    """
    Create and save default yoga pose classification model
    """
    model = create_default_model()
    
    # Save model
    model.save('yoga_pose_model.h5')
    print("Default yoga pose classification model created and saved successfully!")

# Allow direct execution to create model
if __name__ == "__main__":
    save_default_model()