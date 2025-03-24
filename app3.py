import streamlit as st
from yoga_analysis import YogaPoseAnalysis
from chat_handler3 import YogaChatHandler
from image_processor import ImageProcessor
from style import get_custom_styles

class YogaPoseAnalysisApp:
    def __init__(self):
        self.yoga_analysis = YogaPoseAnalysis()
        self.chat_handler = YogaChatHandler()
        self.image_processor = ImageProcessor()
        
        # Initialize session state
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'yoga_context' not in st.session_state:
            st.session_state.yoga_context = ""
        if 'current_image_id' not in st.session_state:
            st.session_state.current_image_id = None
        
        # Apply custom CSS
        st.markdown(f"<style>{get_custom_styles()}</style>", unsafe_allow_html=True)

    def setup_streamlit(self):
        st.title("🧘‍♂️ Yoga Pose Analysis System")

        # Create a container for main content
        main_content = st.container()
        
        with main_content:
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
                        current_file_id = hash(uploaded_file.getvalue())
                        if current_file_id != st.session_state.current_image_id:
                            self.reset_chat_history()
                            st.session_state.current_image_id = current_file_id
                            self.process_uploaded_file(uploaded_file)

                elif analysis_option == "Provide Image URL":
                    image_url = st.text_input("Enter the Image URL")
                    if image_url:
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

            # Chat interface
            if 'analysis_result' in st.session_state:
                self.display_chat_interface()

        # Custom chat input form
        if 'analysis_result' in st.session_state:
            self.render_custom_chat_input()

    def reset_chat_history(self):
        """Reset chat history when new image is processed"""
        st.session_state.chat_history = []
        st.session_state.yoga_context = ""

    def process_uploaded_file(self, uploaded_file):
        """Process uploaded image file"""
        image_path = self.image_processor.save_uploaded_file(uploaded_file)
        st.session_state.current_image = uploaded_file
        self.perform_analysis(image_path)

    def process_image_url(self, image_url):
        """Process image from URL"""
        image_path = self.image_processor.download_image(image_url)
        if image_path:
            st.session_state.current_image = image_url
            self.perform_analysis(image_path)

    def perform_analysis(self, image_path):
        """Perform yoga pose analysis"""
        analysis_result = self.yoga_analysis.analyze_image(image_path)
        st.session_state.analysis_result = analysis_result
        st.session_state.yoga_context = analysis_result['full_analysis']

    def display_analysis_results(self):
        """Display yoga pose analysis results"""
        result = st.session_state.analysis_result
        
        st.subheader("📊 Pose Analysis")
        st.metric(label="Identified Pose", value=result['pose_name'])

        with st.expander("📝 Detailed Pose Analysis"):
            st.markdown(result['full_analysis'])

    def display_chat_interface(self):
        """Display chat interface with message history"""
        st.subheader("AI Assistant")
        
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Hidden Streamlit chat input (will be triggered by custom input)
        user_query = st.chat_input("", key="hidden_chat_input")
        
        if user_query:
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            response = self.chat_handler.get_response(user_query, st.session_state.yoga_context)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()

    def render_custom_chat_input(self):
        """Render custom chat input form"""
        st.markdown("""
            <div class="chat-container">
                <form id="chat-form" class="chat-input-container">
                    <input type="text" id="chat-input" class="chat-input" 
                           placeholder="Ask a question about your pose or yoga practice..." 
                           onkeypress="if(event.keyCode==13)document.getElementById('chat-submit').click()">
                    <button type="button" id="chat-submit" class="chat-submit">
                        ↑
                    </button>
                </form>
            </div>
            
            <script>
                // JavaScript to handle chat submission
                const form = document.getElementById('chat-form');
                const input = document.getElementById('chat-input');
                const submit = document.getElementById('chat-submit');
                
                submit.addEventListener('click', function(e) {
                    e.preventDefault();
                    if (input.value.trim()) {
                        // Find and trigger the hidden Streamlit chat input
                        const streamlitInput = window.parent.document.querySelector('.stChatInput input');
                        streamlitInput.value = input.value;
                        streamlitInput.dispatchEvent(new Event('input', { bubbles: true }));
                        const submitButton = window.parent.document.querySelector('.stChatInput button');
                        submitButton.click();
                        input.value = '';
                    }
                });
            </script>
        """, unsafe_allow_html=True)

def main():
    app = YogaPoseAnalysisApp()
    app.setup_streamlit()

if __name__ == "__main__":
    main()