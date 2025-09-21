from dotenv import load_dotenv
import os

load_dotenv()  # 👈 this will read .env and set env vars

def get_llm():
    from langchain_mistralai import ChatMistralAI
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY not found. Did you set it in .env?")
    return ChatMistralAI(model="codestral-latest", api_key=api_key)
