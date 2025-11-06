from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

key = os.getenv("GROQ_API_KEY")

if key:
    print("✅ Environment variable loaded successfully!")
    print("First 6 characters of key:", key[:6] + "******")
else:
    print("❌ Failed to load GROQ_API_KEY. Check your .env file or its location.")
