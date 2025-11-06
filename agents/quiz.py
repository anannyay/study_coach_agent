import json
import re
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

class QuizAgent:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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

            # Get raw text from model
            text = response.choices[0].message.content.strip()
            print("=" * 50)
            print("RAW RESPONSE:")
            print(text)
            print("=" * 50)
            
            # Clean the response
            text = self._clean_json_response(text)
            
            # Parse JSON
            quiz_data = json.loads(text)
            
            # Validate structure
            if not isinstance(quiz_data, list):
                print("Error: Response is not a list")
                return None
                
            if len(quiz_data) == 0:
                print("Error: Empty quiz list")
                return None
            
            # Validate each question
            valid_questions = []
            for i, q in enumerate(quiz_data):
                if self._validate_question(q, i):
                    valid_questions.append(q)
            
            if len(valid_questions) == 0:
                print("Error: No valid questions found")
                return None
                
            print(f"Successfully parsed {len(valid_questions)} questions")
            return valid_questions
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Cleaned text: {text[:500]}")
            return None
        except Exception as e:
            print(f"Error generating quiz: {e}")
            return None
    
    def _clean_json_response(self, text):
        """Clean the response to extract valid JSON"""
        # Remove markdown code blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Find JSON array
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            text = match.group(0)
        
        # Remove any text before [ or after ]
        start = text.find('[')
        end = text.rfind(']')
        if start != -1 and end != -1:
            text = text[start:end+1]
        
        return text.strip()
    
    def _validate_question(self, q, index):
        """Validate a single question structure"""
        if not isinstance(q, dict):
            print(f"Q{index}: Not a dictionary")
            return False
        
        required_keys = ['question', 'options', 'answer']
        for key in required_keys:
            if key not in q:
                print(f"Q{index}: Missing key '{key}'")
                return False
        
        if not isinstance(q['options'], list):
            print(f"Q{index}: Options is not a list")
            return False
        
        if len(q['options']) < 2:
            print(f"Q{index}: Not enough options")
            return False
        
        if q['answer'] not in q['options']:
            print(f"Q{index}: Answer '{q['answer']}' not in options")
            # Try to fix it
            if isinstance(q['answer'], str):
                for opt in q['options']:
                    if q['answer'].lower() in opt.lower() or opt.lower() in q['answer'].lower():
                        q['answer'] = opt
                        print(f"Q{index}: Fixed answer to '{opt}'")
                        return True
            return False
        
        return True