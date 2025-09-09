import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import Any

def load_env_and_models() -> Any:
    """
    Load environment variables and initialize the Gemini model.
    Raises ValueError if any required environment variable is missing.
    Returns the initialized generative model.
    """
    load_dotenv()
    required_vars = ["GROQ_API_KEY", "GOOGLE_API_KEY", "ELEVENLABS_API_KEY"]
    for var in required_vars:
        if not os.getenv(var):
            raise ValueError(f"Please set the {var} environment variable.")
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel(model_name='gemini-2.5-flash')
    return model
