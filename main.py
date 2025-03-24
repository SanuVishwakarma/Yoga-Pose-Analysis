import streamlit as st
from yoga_analysis import YogaPoseAnalysis
from chat_handler import YogaChatHandler
from image_processor import ImageProcessor

class YogaPoseAnalysisApp:
    def __init__(self):
        self.yoga_analysis = YogaPoseAnalysis()
        self.chat_handler = YogaChatHandler()
        self.image_processor = ImageProcessor()
        
        # Initialize session state for chat history and context
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'yoga_context' not in st.session_state:
            st.session_state.yoga_context = ""
        if 'current_image_id' not in st.session_state:
            st.session_state.current_image_id = None

    def reset_chat_history(self):
        """Reset chat history when new image is processed"""
        st.session_state.chat_history = []
        st.session_state.yoga_context = ""

    def setup_streamlit(self):
        st.title("🧘‍♂️ Yoga Pose Analysis System")

        # Sidebar for input methods
        with st.sidebar:
            analysis_option = st.radio(
                "Choose your input method",
                ("Upload Image", "Provide Image URL")
            )

            if analysis_option == "Upload Image":
                uploaded_file = st.file_uploader(
                    "Upload Yoga Pose Image", 
                    type=['png', 'jpg', 'jpeg'],
                    help="Upload a clear photo of your yoga pose for analysis"
                )
                if uploaded_file:
                    # Check if this is a new image
                    current_file_id = hash(uploaded_file.getvalue())
                    if current_file_id != st.session_state.current_image_id:
                        self.reset_chat_history()
                        st.session_state.current_image_id = current_file_id
                        self.process_uploaded_file(uploaded_file)

            elif analysis_option == "Provide Image URL":
                image_url = st.text_input("Enter the Image URL")
                if image_url:
                    # Check if this is a new URL
                    current_url_id = hash(image_url)
                    if current_url_id != st.session_state.current_image_id:
                        self.reset_chat_history()
                        st.session_state.current_image_id = current_url_id
                        self.process_image_url(image_url)

        # Main content area
        if 'current_image' in st.session_state:
            st.image(st.session_state.current_image, caption="Yoga Pose", use_container_width=True)

        if 'analysis_result' in st.session_state:
            self.display_analysis_results()

        # Chat interface at the bottom
        if 'analysis_result' in st.session_state:
            self.display_chat_interface()

    def process_uploaded_file(self, uploaded_file):
        image_path = self.image_processor.save_uploaded_file(uploaded_file)
        st.session_state.current_image = uploaded_file
        self.perform_analysis(image_path)

    def process_image_url(self, image_url):
        image_path = self.image_processor.download_image(image_url)
        if image_path:
            st.session_state.current_image = image_url
            self.perform_analysis(image_path)

    def perform_analysis(self, image_path):
        analysis_result = self.yoga_analysis.analyze_image(image_path)
        st.session_state.analysis_result = analysis_result
        # Update yoga context with the full analysis
        st.session_state.yoga_context = analysis_result['full_analysis']

    def display_analysis_results(self):
        result = st.session_state.analysis_result
        
        st.subheader("📊 Pose Analysis")
        st.metric(label="Identified Pose", value=result['pose_name'])

        with st.expander("📝 Detailed Pose Analysis"):
            st.markdown(result['full_analysis'])

    def display_chat_interface(self):
        st.subheader("Chat Assistant")
        
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input at the bottom
        with st.container():
            st.markdown('<div style="margin-bottom: 50px;"></div>', unsafe_allow_html=True)
            user_query = st.chat_input("Ask a question about your pose or yoga practice")
            
            if user_query:
                # Add user message to chat history
                st.session_state.chat_history.append({"role": "user", "content": user_query})
                
                # Get chatbot response using the full analysis as context
                response = self.chat_handler.get_response(
                    user_query, 
                    st.session_state.yoga_context
                )
                
                # Add assistant response to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                
                # Rerun to update chat display
                st.rerun()

def main():
    app = YogaPoseAnalysisApp()
    app.setup_streamlit()

if __name__ == "__main__":
    main()