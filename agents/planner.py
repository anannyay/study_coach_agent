from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables from .env or Streamlit secrets
load_dotenv()

class PlannerAgent:
    def __init__(self):
        # Get API key from environment (works locally + Streamlit Cloud)
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("Missing GROQ_API_KEY. Please set it in Streamlit secrets or .env file.")
        self.client = Groq(api_key=api_key)

    def create_plan(self, topic, days, hours):
        """Generate a structured study plan."""
        prompt = f"""
        Create a detailed study plan for learning **{topic}** in {days} days,
        with about {hours} hours of study per day.

        Format the response as:
        - Clear daily breakdown (Day 1, Day 2, etc.)
        - Include key topics, tasks, and small review goals.
        - Use short, action-focused sentences.
        """

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are an expert academic planner creating clear, actionable schedules."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1200
            )

            # Extract plan text
            plan_text = response.choices[0].message.content.strip()
            return plan_text

        except Exception as e:
            print(f"Error generating plan: {e}")
            return "⚠️ Error: Could not generate a study plan. Check your API key or connection."
