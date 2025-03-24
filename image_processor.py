import numpy as np
import PIL.Image
import os
import requests
import io

class ImageProcessor:
    def __init__(self):
        self.temp_dir = "temp"
        os.makedirs(self.temp_dir, exist_ok=True)

    def save_uploaded_file(self, uploaded_file):
        """Save uploaded file and return path"""
        image_path = os.path.join(self.temp_dir, "temp_uploaded_image.png")
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return image_path

    def download_image(self, image_url):
        """Download image from URL and return path"""
        try:
            response = requests.get(image_url)
            if response.status_code == 200:
                image_path = os.path.join(self.temp_dir, "temp_url_image.png")
                img = PIL.Image.open(io.BytesIO(response.content))
                img.save(image_path)
                return image_path
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None

    def preprocess_image(self, image_path):
        """Preprocess image for model input"""
        try:
            img = PIL.Image.open(image_path)
            img_resized = img.resize((224, 224))
            img_array = np.array(img_resized)
            img_normalized = img_array / 255.0
            img_input = np.expand_dims(img_normalized, axis=0)
            return img_input
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None

    def cleanup(self):
        """Clean up temporary files"""
        for file in os.listdir(self.temp_dir):
            try:
                os.remove(os.path.join(self.temp_dir, file))
            except Exception as e:
                print(f"Error cleaning up file {file}: {e}")