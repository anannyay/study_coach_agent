import os
import streamlit as st
from groq import Groq

class PlannerAgent:
    def __init__(self):
        # Load key from Streamlit secrets (cloud) or .env (local)
        api_key = (
            st.secrets.get("GROQ_API_KEY") 
            if "GROQ_API_KEY" in st.secrets 
            else os.getenv("GROQ_API_KEY")
        )
        self.client = Groq(api_key=api_key)

    def create_plan(self, topic, days, hours):
        prompt = f"Create a {days}-day structured study plan for {topic}, {hours} hours per day."
        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful study planner."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content
