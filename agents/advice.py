from groq import Groq
import os
from dotenv import load_dotenv
import streamlit as st

# Load local .env if running locally
load_dotenv()

class AdviceAgent:
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

    def give_advice(self, topic, score, total, plan_summary=None):
        """Generate personalized learning advice"""
        accuracy = round((score / total) * 100, 1)
        user_level = "beginner" if accuracy < 50 else "intermediate" if accuracy < 80 else "advanced"

        user_prompt = f"""
        The user studied {topic} and scored {score}/{total} ({accuracy}%).
        The user's level is roughly {user_level}.
        Give clear, practical, and motivational advice on:
        1. What concepts to focus on next
        2. Study methods or resources that match their level
        3. How to improve retention and confidence.
        Keep it concise, professional, and encouraging.
        """

        if plan_summary:
            user_prompt += f"\nTheir plan summary: {plan_summary}"

        resp = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an experienced academic coach giving actionable learning advice."},
                {"role": "user", "content": user_prompt}
            ]
        )

        return resp.choices[0].message.content.strip()
