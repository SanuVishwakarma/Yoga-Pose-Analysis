from groq import Groq
import os
from dotenv import load_dotenv

class YogaChatHandler:
    def __init__(self):
        load_dotenv()
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        if self.GROQ_API_KEY:
            self.groq_client = Groq(api_key=self.GROQ_API_KEY)

    def count_words(self, text):
        """Count words in text"""
        return len(text.split())

    def get_response(self, user_query, yoga_context):
        try:
            messages = [
                {
                    "role": "system",
                    "content": """
                    You are an experienced yoga instructor providing concise guidance.
                    Key instructions:
                    - Limit responses to maximum 200 words
                    - Be direct and specific
                    - Focus on the most relevant information
                    - Only include essential details
                    - Skip general advice unless specifically asked
                    - Maintain a supportive but concise tone
                    - If the question can be answered briefly, do so
                    """
                },
                {
                    "role": "user",
                    "content": f"""
                    Context: {yoga_context}
                    
                    Question: {user_query}
                    
                    Remember to provide a focused response in 200 words or less.
                    """
                }
            ]

            chat_completion = self.groq_client.chat.completions.create(
                messages=messages,
                model="llama3-8b-8192",
                max_tokens=300,  # Reduced token limit
                temperature=0.7,
                top_p=0.9
            )

            response = chat_completion.choices[0].message.content

            # Add disclaimer only if response is about practice or safety
            if any(word in user_query.lower() for word in ['practice', 'safe', 'risk', 'hurt', 'pain', 'modify']):
                disclaimer = (
                    "\n\n---\n"
                    "*Note: Please practice with proper instruction and consult a qualified instructor for personalized guidance.*"
                )
                response += disclaimer

            # Verify response length
            if self.count_words(response) > 200:
                # Truncate to last complete sentence before 200 words
                words = response.split()
                truncated = ' '.join(words[:200])
                last_sentence = truncated.rsplit('.', 1)[0] + '.'
                return last_sentence

            return response

        except Exception as e:
            return f"Unable to generate response: {str(e)}"