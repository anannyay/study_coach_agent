import json
import re
from groq import Groq
import os
from dotenv import load_dotenv
import streamlit as st

# Load local .env file if it exists
load_dotenv()

class QuizAgent:
    def __init__(self):
        # Try Streamlit secrets first, fallback to .env
        api_key = (
            st.secrets.get("GROQ_API_KEY")
            if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets
            else os.getenv("GROQ_API_KEY")
        )
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in Streamlit secrets or .env file.")
        self.client = Groq(api_key=api_key)

    def generate_quiz(self, topic, num_questions=5):
        prompt = f"""Generate exactly {num_questions} multiple choice questions about {topic}.

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "question": "What is the capital of France?",
    "options": ["London", "Paris", "Berlin", "Madrid"],
    "answer": "Paris"
  }}
]

Requirements:
- Return ONLY the JSON array, no other text
- Each question must have exactly 4 options
- The answer must be one of the options (exact match)
- No markdown, no explanations, just JSON"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a quiz generator that returns only valid JSON arrays."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            text = response.choices[0].message.content.strip()
            text = self._clean_json_response(text)
            quiz_data = json.loads(text)

            if not isinstance(quiz_data, list) or len(quiz_data) == 0:
                print("Error: Empty or invalid quiz response.")
                return None

            valid_questions = [q for i, q in enumerate(quiz_data) if self._validate_question(q, i)]
            return valid_questions if valid_questions else None

        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return None
        except Exception as e:
            print(f"Error generating quiz: {e}")
            return None

    def _clean_json_response(self, text):
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            text = match.group(0)
        return text.strip()

    def _validate_question(self, q, index):
        if not isinstance(q, dict):
            return False
        if not all(k in q for k in ['question', 'options', 'answer']):
            return False
        if not isinstance(q['options'], list) or len(q['options']) != 4:
            return False
        if q['answer'] not in q['options']:
            return False
        return True
