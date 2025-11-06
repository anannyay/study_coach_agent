from groq import Groq
from dotenv import load_dotenv
import os
from agents.planner import PlannerAgent

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

planner = PlannerAgent(client)
plan = planner.create_plan("Machine Learning", 5, 2)
print(plan)
