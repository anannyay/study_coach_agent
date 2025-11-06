from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

class PlannerAgent:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def create_plan(self, topic, days, hours):
        """Generate a personalized study plan"""
        resp = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a motivating AI study coach who creates structured, goal-based study plans."},
                {"role": "user", "content": f"Create a {days}-day study plan for {topic}. The student can study {hours} hours per day."}
            ]
        )
        return resp.choices[0].message.content
