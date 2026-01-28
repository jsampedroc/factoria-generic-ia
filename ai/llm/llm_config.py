import os
from crewai import LLM
from dotenv import load_dotenv

load_dotenv()

llm = LLM(
    model="deepseek-chat",
    base_url="https://api.deepseek.com/v1",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)