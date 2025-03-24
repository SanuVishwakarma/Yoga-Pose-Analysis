import tensorflow as tf
import google.generativeai as genai
import os
import PIL.Image
from dotenv import load_dotenv
import re

class YogaPoseAnalysis:
    def __init__(self):
        load_dotenv()
        self.setup_apis()
        self.load_models()

    def setup_apis(self):
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if self.GEMINI_API_KEY:
            genai.configure(api_key=self.GEMINI_API_KEY)
            self.gemini_vision_model = genai.GenerativeModel('gemini-1.5-flash')

    def load_models(self):
        try:
            self.pose_classifier = tf.keras.models.load_model('yoga_pose_model.h5')
        except:
            from model_generation import create_default_model
            self.pose_classifier = create_default_model()
            self.pose_classifier.save('yoga_pose_model.h5')

    def extract_pose_name(self, analysis_text):
        """Extract pose name from the analysis text"""
        try:
            # Look for pose name in the first few lines of analysis
            first_paragraph = analysis_text.split('\n')[0:5]
            for line in first_paragraph:
                # Look for common patterns in pose identification
                if any(x in line.lower() for x in ['pose:', 'asana:', 'position:', 'identified as']):
                    # Extract the pose name, typically following these markers
                    pose_name = line.split(':')[-1].strip()
                    return pose_name
            # If no specific markers found, take the first sentence that might contain pose name
            for line in first_paragraph:
                if 'pose' in line.lower() or 'asana' in line.lower():
                    return line.strip()
            return "Pose name not identified"
        except:
            return "Pose name not identified"

    def analyze_image(self, image_path):
        try:
            img = PIL.Image.open(image_path)
            
            prompt = """
            You are a professional yoga instructor and alignment specialist. Analyze this yoga pose 
            and provide a detailed assessment including:
            1. Pose Identification and Classification (Start with 'Pose:' followed by the pose name)
            2. Alignment Analysis
            3. Suggested Adjustments and Corrections
            4. Safety Considerations and Precautions
            5. Benefits of the Pose
            6. Common Mistakes to Avoid
            
            Use a supportive and encouraging tone while maintaining professional accuracy.
            Emphasize proper form and safety in practice.
            """

            response = self.gemini_vision_model.generate_content([prompt, img])
            analysis_text = response.text if response and response.text else "Unable to generate pose analysis."
            
            return {
                'full_analysis': analysis_text,
                'pose_name': self.extract_pose_name(analysis_text)
            }
            
        except Exception as e:
            return {
                'full_analysis': f"Analysis error: {e}",
                'pose_name': "Analysis Failed"
            }